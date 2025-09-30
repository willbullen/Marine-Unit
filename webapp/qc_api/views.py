from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from django.http import JsonResponse, FileResponse, Http404
from django.conf import settings
import os
import sys
import subprocess
import uuid
from datetime import datetime
import json

# Add the parent directory to Python path to import QC processor
sys.path.append(str(settings.BASE_DIR.parent / 'QC Scripts'))

from .models import (
    BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult,
    ThirdPartyDataSource, ThirdPartyData, DataConfirmation
)
from .serializers import (
    BuoyStationSerializer, QCParameterSerializer, StationQCLimitSerializer,
    QCProcessingJobSerializer, QCResultSerializer, QCLimitUpdateSerializer,
    QCProcessingRequestSerializer, ThirdPartyDataSourceSerializer,
    ThirdPartyDataSerializer, DataConfirmationSerializer,
    ThirdPartyDataImportSerializer, DataConfirmationRequestSerializer
)

class BuoyStationViewSet(viewsets.ModelViewSet):
    """ViewSet for managing buoy stations"""
    queryset = BuoyStation.objects.all()
    serializer_class = BuoyStationSerializer
    lookup_field = 'station_id'

class QCParameterViewSet(viewsets.ModelViewSet):
    """ViewSet for managing QC parameters"""
    queryset = QCParameter.objects.all()
    serializer_class = QCParameterSerializer

class StationQCLimitViewSet(viewsets.ModelViewSet):
    """ViewSet for managing station-specific QC limits"""
    queryset = StationQCLimit.objects.all()
    serializer_class = StationQCLimitSerializer

    def get_queryset(self):
        queryset = StationQCLimit.objects.all()
        station_id = self.request.query_params.get('station_id')
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        return queryset

class QCResultViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing QC processing results"""
    queryset = QCResult.objects.all()
    serializer_class = QCResultSerializer

    def get_queryset(self):
        queryset = QCResult.objects.all()
        station_id = self.request.query_params.get('station_id')
        year = self.request.query_params.get('year')
        
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset

@api_view(['GET'])
def dashboard_overview(request):
    """Get dashboard overview data"""
    try:
        stations = BuoyStation.objects.filter(is_active=True)
        results = QCResult.objects.all()
        
        dashboard_data = {
            'total_stations': stations.count(),
            'total_results': results.count(),
            'station_summary': [],
            'recent_processing': []
        }
        
        # Get summary for each station
        for station in stations:
            station_results = results.filter(station=station).order_by('-year')
            latest_result = station_results.first()
            
            station_data = {
                'station_id': station.station_id,
                'name': station.name,
                'location': station.location_description,
                'exposure_type': station.exposure_type,
                'years_available': list(station_results.values_list('year', flat=True)),
                'latest_qc_rate': latest_result.qc_completion_rate if latest_result else 0,
                'latest_year': latest_result.year if latest_result else None,
                'total_records': sum(r.total_records for r in station_results),
                'avg_qc_rate': sum(r.qc_completion_rate for r in station_results) / len(station_results) if station_results else 0
            }
            dashboard_data['station_summary'].append(station_data)
        
        # Get recent processing jobs
        recent_jobs = QCProcessingJob.objects.order_by('-started_at')[:10]
        dashboard_data['recent_processing'] = QCProcessingJobSerializer(recent_jobs, many=True).data
        
        return Response(dashboard_data)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def update_qc_limits(request):
    """Update QC limits for a station and parameter"""
    serializer = QCLimitUpdateSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            station_id = serializer.validated_data['station_id']
            parameter_name = serializer.validated_data['parameter_name']
            
            station = BuoyStation.objects.get(station_id=station_id)
            parameter = QCParameter.objects.get(name=parameter_name)
            
            # Get or create the QC limit
            qc_limit, created = StationQCLimit.objects.get_or_create(
                station=station,
                parameter=parameter,
                defaults={
                    'min_value': serializer.validated_data.get('min_value'),
                    'max_value': serializer.validated_data.get('max_value'),
                    'spike_threshold': serializer.validated_data.get('spike_threshold'),
                    'notes': serializer.validated_data.get('notes', '')
                }
            )
            
            if not created:
                # Update existing limit
                if 'min_value' in serializer.validated_data:
                    qc_limit.min_value = serializer.validated_data['min_value']
                if 'max_value' in serializer.validated_data:
                    qc_limit.max_value = serializer.validated_data['max_value']
                if 'spike_threshold' in serializer.validated_data:
                    qc_limit.spike_threshold = serializer.validated_data['spike_threshold']
                if 'notes' in serializer.validated_data:
                    qc_limit.notes = serializer.validated_data['notes']
                qc_limit.save()
            
            return Response({
                'message': 'QC limits updated successfully',
                'limit': StationQCLimitSerializer(qc_limit).data
            })
            
        except BuoyStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
        except QCParameter.DoesNotExist:
            return Response({'error': 'Parameter not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def run_qc_processing(request):
    """Trigger QC processing for specified stations and years"""
    serializer = QCProcessingRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            # Generate unique job ID
            job_id = f"qc_job_{uuid.uuid4().hex[:8]}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create processing job record
            job = QCProcessingJob.objects.create(
                job_id=job_id,
                status='pending',
                started_at=datetime.now()
            )
            
            # TODO: Implement async processing using Celery or background task
            # For now, return the job ID for tracking
            
            return Response({
                'message': 'QC processing job created',
                'job_id': job_id,
                'status': 'pending'
            })
            
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def download_qc_file(request, station_id, year, file_type):
    """Download QC files (CSV, PDF, PNG)"""
    try:
        # Construct file path based on type
        if file_type == 'csv':
            filename = f'buoy_{station_id}_{year}_qcd.csv'
        elif file_type == 'pdf':
            filename = f'buoy_{station_id}_{year}_qc_report.pdf'
        elif file_type == 'png':
            filename = f'buoy_{station_id}_{year}_qc_overview.png'
        elif file_type == 'md':
            filename = f'buoy_{station_id}_{year}_qc_report.md'
        else:
            raise Http404("Invalid file type")
        
        file_path = settings.QC_DATA_DIR / filename
        
        if not file_path.exists():
            raise Http404("File not found")
        
        return FileResponse(
            open(file_path, 'rb'),
            as_attachment=True,
            filename=filename
        )
        
    except Exception as e:
        raise Http404(f"Error accessing file: {str(e)}")

@api_view(['GET'])
def get_station_qc_limits(request, station_id):
    """Get all QC limits for a specific station"""
    try:
        station = BuoyStation.objects.get(station_id=station_id)
        parameters = QCParameter.objects.filter(is_active=True)
        
        limits_data = []
        for param in parameters:
            try:
                station_limit = StationQCLimit.objects.get(station=station, parameter=param)
                limit_data = {
                    'parameter': param.name,
                    'display_name': param.display_name,
                    'unit': param.unit,
                    'parameter_type': param.parameter_type,
                    'min_value': station_limit.min_value,
                    'max_value': station_limit.max_value,
                    'spike_threshold': station_limit.spike_threshold,
                    'notes': station_limit.notes,
                    'is_custom': True,
                    'updated_at': station_limit.updated_at
                }
            except StationQCLimit.DoesNotExist:
                # Use default values
                limit_data = {
                    'parameter': param.name,
                    'display_name': param.display_name,
                    'unit': param.unit,
                    'parameter_type': param.parameter_type,
                    'min_value': param.default_min,
                    'max_value': param.default_max,
                    'spike_threshold': param.default_spike_threshold,
                    'notes': '',
                    'is_custom': False,
                    'updated_at': None
                }
            
            limits_data.append(limit_data)
        
        return Response({
            'station_id': station_id,
            'station_name': station.name,
            'exposure_type': station.exposure_type,
            'limits': limits_data
        })
        
    except BuoyStation.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# Third-Party Data Management Views

class ThirdPartyDataSourceViewSet(viewsets.ModelViewSet):
    """ViewSet for managing third-party data sources"""
    queryset = ThirdPartyDataSource.objects.all()
    serializer_class = ThirdPartyDataSourceSerializer

class ThirdPartyDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing third-party data"""
    queryset = ThirdPartyData.objects.all()
    serializer_class = ThirdPartyDataSerializer
    
    def get_queryset(self):
        queryset = ThirdPartyData.objects.all()
        station_id = self.request.query_params.get('station_id')
        source_id = self.request.query_params.get('source_id')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        if source_id:
            queryset = queryset.filter(source_id=source_id)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset

class DataConfirmationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing data confirmations"""
    queryset = DataConfirmation.objects.all()
    serializer_class = DataConfirmationSerializer
    
    def get_queryset(self):
        queryset = DataConfirmation.objects.all()
        station_id = self.request.query_params.get('station_id')
        status_filter = self.request.query_params.get('status')
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        if status_filter:
            queryset = queryset.filter(confirmation_status=status_filter)
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        return queryset

@api_view(['POST'])
def import_third_party_data(request):
    """Import third-party data for a station"""
    serializer = ThirdPartyDataImportSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            station_id = serializer.validated_data['station_id']
            source_id = serializer.validated_data['source_id']
            data_records = serializer.validated_data['data']
            
            station = BuoyStation.objects.get(station_id=station_id)
            source = ThirdPartyDataSource.objects.get(id=source_id)
            
            imported_count = 0
            updated_count = 0
            errors = []
            
            for record in data_records:
                try:
                    # Parse timestamp
                    from datetime import datetime
                    timestamp = record.get('timestamp')
                    if isinstance(timestamp, str):
                        timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                    
                    # Create or update third-party data record
                    third_party_data, created = ThirdPartyData.objects.update_or_create(
                        station=station,
                        source=source,
                        timestamp=timestamp,
                        defaults={
                            'air_pressure': record.get('air_pressure'),
                            'air_temp': record.get('air_temp'),
                            'humidity': record.get('humidity'),
                            'wind_speed': record.get('wind_speed'),
                            'wind_direction': record.get('wind_direction'),
                            'wave_height': record.get('wave_height'),
                            'wave_height_max': record.get('wave_height_max'),
                            'wave_period': record.get('wave_period'),
                            'wave_direction': record.get('wave_direction'),
                            'sea_temp': record.get('sea_temp'),
                            'data_quality': record.get('data_quality', ''),
                            'raw_data': record
                        }
                    )
                    
                    if created:
                        imported_count += 1
                    else:
                        updated_count += 1
                        
                except Exception as e:
                    errors.append(f"Error importing record {record.get('timestamp')}: {str(e)}")
            
            return Response({
                'message': 'Third-party data import completed',
                'imported': imported_count,
                'updated': updated_count,
                'errors': errors
            })
            
        except BuoyStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
        except ThirdPartyDataSource.DoesNotExist:
            return Response({'error': 'Data source not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def run_data_confirmation(request):
    """Run data confirmation comparing station data with third-party data"""
    serializer = DataConfirmationRequestSerializer(data=request.data)
    
    if serializer.is_valid():
        try:
            import pandas as pd
            from datetime import datetime
            
            station_id = serializer.validated_data['station_id']
            start_date = serializer.validated_data['start_date']
            end_date = serializer.validated_data['end_date']
            parameters = serializer.validated_data.get('parameters', [])
            tolerance_percent = serializer.validated_data.get('tolerance_percent', 10.0)
            
            station = BuoyStation.objects.get(station_id=station_id)
            
            # Parameter mapping between station data and third-party data
            param_mapping = {
                'airpressure': 'air_pressure',
                'airtemp': 'air_temp',
                'humidity': 'humidity',
                'windsp': 'wind_speed',
                'winddir': 'wind_direction',
                'hm0': 'wave_height',
                'hmax': 'wave_height_max',
                'tp': 'wave_period',
                'mdir': 'wave_direction',
                'seatemp_aa': 'sea_temp'
            }
            
            # Get third-party data for the time period
            third_party_data = ThirdPartyData.objects.filter(
                station=station,
                timestamp__gte=start_date,
                timestamp__lte=end_date
            ).order_by('timestamp', 'source')
            
            if not third_party_data.exists():
                return Response({
                    'message': 'No third-party data available for the specified period',
                    'confirmations_created': 0
                })
            
            # Load station QC data (this would need to be from actual QC'd CSV files)
            # For now, we'll create a placeholder implementation
            confirmations_created = 0
            
            # Get or create QC parameters
            if not parameters:
                parameters = list(param_mapping.keys())
            
            for param_name in parameters:
                try:
                    param = QCParameter.objects.get(name=param_name)
                    third_party_field = param_mapping.get(param_name)
                    
                    if not third_party_field:
                        continue
                    
                    # Process each third-party data point
                    for tp_data in third_party_data:
                        tp_value = getattr(tp_data, third_party_field)
                        
                        if tp_value is None:
                            continue
                        
                        # Create confirmation record
                        # Note: station_value and station_qc_status would need to be loaded from QC'd data
                        # This is a simplified implementation
                        confirmation, created = DataConfirmation.objects.update_or_create(
                            station=station,
                            timestamp=tp_data.timestamp,
                            parameter=param,
                            defaults={
                                'third_party_source': tp_data.source,
                                'third_party_value': tp_value,
                                'tolerance_threshold': tolerance_percent,
                                'confirmation_status': 'pending'
                            }
                        )
                        
                        if created:
                            confirmations_created += 1
                            
                except QCParameter.DoesNotExist:
                    continue
            
            return Response({
                'message': 'Data confirmation completed',
                'station_id': station_id,
                'period': f"{start_date} to {end_date}",
                'confirmations_created': confirmations_created,
                'third_party_records': third_party_data.count()
            })
            
        except BuoyStation.DoesNotExist:
            return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def confirmation_summary(request, station_id):
    """Get confirmation summary for a station"""
    try:
        station = BuoyStation.objects.get(station_id=station_id)
        
        confirmations = DataConfirmation.objects.filter(station=station)
        
        # Calculate summary statistics
        total_confirmations = confirmations.count()
        status_breakdown = {}
        for status_choice in DataConfirmation.CONFIRMATION_STATUS:
            status_code = status_choice[0]
            count = confirmations.filter(confirmation_status=status_code).count()
            if count > 0:
                status_breakdown[status_code] = {
                    'count': count,
                    'percentage': (count / total_confirmations * 100) if total_confirmations > 0 else 0,
                    'label': status_choice[1]
                }
        
        # Get parameter-wise breakdown
        parameter_summary = []
        parameters = QCParameter.objects.filter(is_active=True)
        
        for param in parameters:
            param_confirmations = confirmations.filter(parameter=param)
            if param_confirmations.count() > 0:
                confirmed_count = param_confirmations.filter(confirmation_status='confirmed').count()
                discrepancy_count = param_confirmations.filter(confirmation_status='discrepancy').count()
                
                parameter_summary.append({
                    'parameter': param.name,
                    'display_name': param.display_name,
                    'total': param_confirmations.count(),
                    'confirmed': confirmed_count,
                    'discrepancies': discrepancy_count,
                    'confirmation_rate': (confirmed_count / param_confirmations.count() * 100) if param_confirmations.count() > 0 else 0
                })
        
        return Response({
            'station_id': station_id,
            'station_name': station.name,
            'total_confirmations': total_confirmations,
            'status_breakdown': status_breakdown,
            'parameter_summary': parameter_summary
        })
        
    except BuoyStation.DoesNotExist:
        return Response({'error': 'Station not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
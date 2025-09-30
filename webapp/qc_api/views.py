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
    ThirdPartyBuoyData, QCConfirmation
)
from .serializers import (
    BuoyStationSerializer, QCParameterSerializer, StationQCLimitSerializer,
    QCProcessingJobSerializer, QCResultSerializer, QCLimitUpdateSerializer,
    QCProcessingRequestSerializer, ThirdPartyBuoyDataSerializer, QCConfirmationSerializer
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
class ThirdPartyBuoyDataViewSet(viewsets.ModelViewSet):
    """ViewSet for managing third-party buoy data"""
    queryset = ThirdPartyBuoyData.objects.all()
    serializer_class = ThirdPartyBuoyDataSerializer
    
    def get_queryset(self):
        queryset = ThirdPartyBuoyData.objects.all()
        station_id = self.request.query_params.get('station_id')
        year = self.request.query_params.get('year')
        source = self.request.query_params.get('source')
        
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        if year:
            queryset = queryset.filter(timestamp__year=year)
        if source:
            queryset = queryset.filter(source=source)
        
        return queryset.order_by('-timestamp')

class QCConfirmationViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for viewing QC confirmation results"""
    queryset = QCConfirmation.objects.all()
    serializer_class = QCConfirmationSerializer
    
    def get_queryset(self):
        queryset = QCConfirmation.objects.all()
        station_id = self.request.query_params.get('station_id')
        year = self.request.query_params.get('year')
        
        if station_id:
            queryset = queryset.filter(station__station_id=station_id)
        if year:
            queryset = queryset.filter(year=year)
        
        return queryset.order_by('-year')

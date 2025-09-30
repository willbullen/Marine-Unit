from rest_framework import serializers
from .models import (
    BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult,
    ThirdPartyDataSource, ThirdPartyData, DataConfirmation
)

class QCParameterSerializer(serializers.ModelSerializer):
    class Meta:
        model = QCParameter
        fields = '__all__'

class StationQCLimitSerializer(serializers.ModelSerializer):
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)
    parameter_display_name = serializers.CharField(source='parameter.display_name', read_only=True)
    parameter_unit = serializers.CharField(source='parameter.unit', read_only=True)
    parameter_type = serializers.CharField(source='parameter.parameter_type', read_only=True)
    
    class Meta:
        model = StationQCLimit
        fields = ['id', 'parameter', 'parameter_name', 'parameter_display_name', 
                 'parameter_unit', 'parameter_type', 'min_value', 'max_value', 
                 'spike_threshold', 'notes', 'updated_at']

class BuoyStationSerializer(serializers.ModelSerializer):
    qc_limits = StationQCLimitSerializer(source='stationqclimit_set', many=True, read_only=True)
    
    class Meta:
        model = BuoyStation
        fields = ['station_id', 'name', 'latitude', 'longitude', 
                 'location_description', 'exposure_type', 'is_active', 
                 'qc_limits', 'created_at', 'updated_at']

class QCProcessingJobSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    
    class Meta:
        model = QCProcessingJob
        fields = ['job_id', 'station_id', 'year', 'status', 'progress', 
                 'started_at', 'completed_at', 'error_message', 'results']

class QCResultSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = QCResult
        fields = ['station_id', 'station_name', 'year', 'total_records', 
                 'qc_complete_records', 'qc_completion_rate', 'processing_date',
                 'csv_file_path', 'report_md_path', 'report_pdf_path', 
                 'visualization_path', 'issues_summary']

class QCLimitUpdateSerializer(serializers.Serializer):
    """Serializer for updating QC limits"""
    station_id = serializers.CharField(max_length=10)
    parameter_name = serializers.CharField(max_length=50)
    min_value = serializers.FloatField(required=False, allow_null=True)
    max_value = serializers.FloatField(required=False, allow_null=True)
    spike_threshold = serializers.FloatField(required=False, allow_null=True)
    notes = serializers.CharField(required=False, allow_blank=True, max_length=1000)

class QCProcessingRequestSerializer(serializers.Serializer):
    """Serializer for QC processing requests"""
    station_ids = serializers.ListField(
        child=serializers.CharField(max_length=10),
        required=False,
        help_text="List of station IDs to process. If empty, all stations will be processed."
    )
    years = serializers.ListField(
        child=serializers.IntegerField(min_value=2020, max_value=2030),
        required=False,
        help_text="List of years to process. If empty, all available years will be processed."
    )

class ThirdPartyDataSourceSerializer(serializers.ModelSerializer):
    """Serializer for third-party data sources"""
    source_type_display = serializers.CharField(source='get_source_type_display', read_only=True)
    
    class Meta:
        model = ThirdPartyDataSource
        fields = ['id', 'name', 'source_type', 'source_type_display', 'description', 
                 'api_endpoint', 'update_frequency', 'is_active', 'created_at', 'updated_at']
        read_only_fields = ['created_at', 'updated_at']

class ThirdPartyDataSerializer(serializers.ModelSerializer):
    """Serializer for third-party buoy data"""
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    source_name = serializers.CharField(source='source.name', read_only=True)
    
    class Meta:
        model = ThirdPartyData
        fields = ['id', 'station_id', 'station_name', 'source', 'source_name', 'timestamp',
                 'air_pressure', 'air_temp', 'humidity', 'wind_speed', 'wind_direction',
                 'wave_height', 'wave_height_max', 'wave_period', 'wave_direction',
                 'sea_temp', 'data_quality', 'raw_data', 'imported_at']
        read_only_fields = ['imported_at']

class DataConfirmationSerializer(serializers.ModelSerializer):
    """Serializer for data confirmations"""
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    parameter_name = serializers.CharField(source='parameter.name', read_only=True)
    parameter_display_name = serializers.CharField(source='parameter.display_name', read_only=True)
    source_name = serializers.CharField(source='third_party_source.name', read_only=True)
    confirmation_status_display = serializers.CharField(source='get_confirmation_status_display', read_only=True)
    
    class Meta:
        model = DataConfirmation
        fields = ['id', 'station_id', 'station_name', 'timestamp', 'parameter', 
                 'parameter_name', 'parameter_display_name', 'station_value', 
                 'station_qc_status', 'third_party_source', 'source_name',
                 'third_party_value', 'difference', 'percent_difference',
                 'confirmation_status', 'confirmation_status_display', 'tolerance_threshold',
                 'notes', 'confirmed_at']
        read_only_fields = ['confirmed_at']

class ThirdPartyDataImportSerializer(serializers.Serializer):
    """Serializer for importing third-party data"""
    station_id = serializers.CharField(max_length=10)
    source_id = serializers.IntegerField()
    data = serializers.ListField(
        child=serializers.DictField(),
        help_text="List of data records to import. Each record should contain timestamp and parameter values."
    )
    
class DataConfirmationRequestSerializer(serializers.Serializer):
    """Serializer for requesting data confirmation"""
    station_id = serializers.CharField(max_length=10)
    start_date = serializers.DateTimeField()
    end_date = serializers.DateTimeField()
    parameters = serializers.ListField(
        child=serializers.CharField(max_length=50),
        required=False,
        help_text="List of parameter names to confirm. If empty, all available parameters will be confirmed."
    )
    tolerance_percent = serializers.FloatField(
        default=10.0,
        help_text="Tolerance percentage for confirmation (default: 10%)"
    )

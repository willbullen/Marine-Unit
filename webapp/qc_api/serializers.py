from rest_framework import serializers
from .models import (
    BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult,
    ThirdPartyBuoyData, QCConfirmation
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

class ThirdPartyBuoyDataSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    
    class Meta:
        model = ThirdPartyBuoyData
        fields = '__all__'

class QCConfirmationSerializer(serializers.ModelSerializer):
    station_id = serializers.CharField(source='station.station_id', read_only=True)
    station_name = serializers.CharField(source='station.name', read_only=True)
    
    class Meta:
        model = QCConfirmation
        fields = ['station_id', 'station_name', 'year', 'total_comparisons',
                 'confirmed_records', 'deviation_records', 'confirmation_rate',
                 'air_pressure_confirmation', 'air_temp_confirmation',
                 'wind_speed_confirmation', 'wave_height_confirmation',
                 'sea_temp_confirmation', 'mean_absolute_error',
                 'root_mean_square_error', 'correlation_coefficient',
                 'third_party_source', 'analysis_date', 'notes']

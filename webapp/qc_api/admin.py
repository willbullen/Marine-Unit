from django.contrib import admin
from .models import (
    BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult,
    ThirdPartyDataSource, ThirdPartyData, DataConfirmation
)

@admin.register(BuoyStation)
class BuoyStationAdmin(admin.ModelAdmin):
    list_display = ['station_id', 'name', 'location_description', 'exposure_type', 'is_active']
    list_filter = ['exposure_type', 'is_active']
    search_fields = ['station_id', 'name', 'location_description']

@admin.register(QCParameter)
class QCParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'unit', 'parameter_type', 'is_active']
    list_filter = ['parameter_type', 'is_active']
    search_fields = ['name', 'display_name']

@admin.register(StationQCLimit)
class StationQCLimitAdmin(admin.ModelAdmin):
    list_display = ['station', 'parameter', 'min_value', 'max_value', 'spike_threshold']
    list_filter = ['station', 'parameter__parameter_type']
    search_fields = ['station__station_id', 'parameter__name']

@admin.register(QCProcessingJob)
class QCProcessingJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'station', 'year', 'status', 'progress', 'started_at']
    list_filter = ['status', 'station']
    search_fields = ['job_id']
    readonly_fields = ['job_id', 'started_at', 'completed_at']

@admin.register(QCResult)
class QCResultAdmin(admin.ModelAdmin):
    list_display = ['station', 'year', 'total_records', 'qc_completion_rate', 'processing_date']
    list_filter = ['station', 'year']
    search_fields = ['station__station_id']

@admin.register(ThirdPartyDataSource)
class ThirdPartyDataSourceAdmin(admin.ModelAdmin):
    list_display = ['name', 'source_type', 'update_frequency', 'is_active', 'created_at']
    list_filter = ['source_type', 'is_active']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ThirdPartyData)
class ThirdPartyDataAdmin(admin.ModelAdmin):
    list_display = ['station', 'source', 'timestamp', 'wave_height', 'air_temp', 'wind_speed']
    list_filter = ['station', 'source', 'timestamp']
    search_fields = ['station__station_id', 'source__name']
    readonly_fields = ['imported_at']
    date_hierarchy = 'timestamp'

@admin.register(DataConfirmation)
class DataConfirmationAdmin(admin.ModelAdmin):
    list_display = ['station', 'parameter', 'timestamp', 'confirmation_status', 'difference', 'percent_difference']
    list_filter = ['confirmation_status', 'station', 'parameter']
    search_fields = ['station__station_id', 'parameter__name']
    readonly_fields = ['confirmed_at']
    date_hierarchy = 'timestamp'


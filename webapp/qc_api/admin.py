from django.contrib import admin
from .models import (
    BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult,
    ThirdPartyBuoyData, QCConfirmation
)

@admin.register(BuoyStation)
class BuoyStationAdmin(admin.ModelAdmin):
    list_display = ['station_id', 'name', 'location_description', 'exposure_type', 'is_active']
    list_filter = ['exposure_type', 'is_active']
    search_fields = ['station_id', 'name', 'location_description']

@admin.register(QCParameter)
class QCParameterAdmin(admin.ModelAdmin):
    list_display = ['name', 'display_name', 'parameter_type', 'unit', 'is_active']
    list_filter = ['parameter_type', 'is_active']
    search_fields = ['name', 'display_name']

@admin.register(StationQCLimit)
class StationQCLimitAdmin(admin.ModelAdmin):
    list_display = ['station', 'parameter', 'min_value', 'max_value', 'spike_threshold']
    list_filter = ['station', 'parameter__parameter_type']
    search_fields = ['station__station_id', 'parameter__name']

@admin.register(QCProcessingJob)
class QCProcessingJobAdmin(admin.ModelAdmin):
    list_display = ['job_id', 'station', 'year', 'status', 'progress', 'started_at', 'completed_at']
    list_filter = ['status', 'station']
    search_fields = ['job_id']
    readonly_fields = ['job_id', 'started_at', 'completed_at']

@admin.register(QCResult)
class QCResultAdmin(admin.ModelAdmin):
    list_display = ['station', 'year', 'qc_completion_rate', 'total_records', 'processing_date']
    list_filter = ['station', 'year']
    search_fields = ['station__station_id']
    readonly_fields = ['processing_date']

@admin.register(ThirdPartyBuoyData)
class ThirdPartyBuoyDataAdmin(admin.ModelAdmin):
    list_display = ['station', 'timestamp', 'source', 'data_quality', 'created_at']
    list_filter = ['source', 'data_quality', 'station']
    search_fields = ['station__station_id', 'notes']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'timestamp'

@admin.register(QCConfirmation)
class QCConfirmationAdmin(admin.ModelAdmin):
    list_display = ['station', 'year', 'confirmation_rate', 'total_comparisons', 'third_party_source', 'analysis_date']
    list_filter = ['station', 'year', 'third_party_source']
    search_fields = ['station__station_id']
    readonly_fields = ['analysis_date']

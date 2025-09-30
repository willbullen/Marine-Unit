from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
import json

class BuoyStation(models.Model):
    """Model representing a buoy station with its metadata"""
    station_id = models.CharField(max_length=10, unique=True, primary_key=True)
    name = models.CharField(max_length=100, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    location_description = models.CharField(max_length=200, blank=True)
    exposure_type = models.CharField(
        max_length=20,
        choices=[
            ('exposed', 'Exposed Atlantic'),
            ('coastal', 'Coastal/Sheltered'),
            ('intermediate', 'Intermediate Exposure'),
            ('variable', 'Variable Conditions'),
            ('unique', 'Unique Location')
        ],
        default='intermediate'
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Station {self.station_id} - {self.location_description}"

    class Meta:
        ordering = ['station_id']

class QCParameter(models.Model):
    """Model representing QC parameters and their default limits"""
    name = models.CharField(max_length=50, unique=True)
    display_name = models.CharField(max_length=100)
    unit = models.CharField(max_length=20, blank=True)
    description = models.TextField(blank=True)
    default_min = models.FloatField(null=True, blank=True)
    default_max = models.FloatField(null=True, blank=True)
    default_spike_threshold = models.FloatField(null=True, blank=True)
    parameter_type = models.CharField(
        max_length=20,
        choices=[
            ('environmental', 'Environmental'),
            ('wave', 'Wave'),
            ('water', 'Water Quality')
        ],
        default='environmental'
    )
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.display_name} ({self.name})"

    class Meta:
        ordering = ['parameter_type', 'name']

class StationQCLimit(models.Model):
    """Model for station-specific QC limits that override defaults"""
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    parameter = models.ForeignKey(QCParameter, on_delete=models.CASCADE)
    min_value = models.FloatField(null=True, blank=True)
    max_value = models.FloatField(null=True, blank=True)
    spike_threshold = models.FloatField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.station.station_id} - {self.parameter.name}"

    class Meta:
        unique_together = ['station', 'parameter']
        ordering = ['station', 'parameter__parameter_type', 'parameter__name']

class QCProcessingJob(models.Model):
    """Model to track QC processing jobs and their status"""
    job_id = models.CharField(max_length=50, unique=True)
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('processing', 'Processing'),
            ('completed', 'Completed'),
            ('failed', 'Failed')
        ],
        default='pending'
    )
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    error_message = models.TextField(blank=True)
    results = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        station_str = f"Station {self.station.station_id}" if self.station else "All Stations"
        year_str = f" - {self.year}" if self.year else ""
        return f"QC Job {self.job_id}: {station_str}{year_str} ({self.status})"

    class Meta:
        ordering = ['-started_at']

class QCResult(models.Model):
    """Model to store QC processing results for quick access"""
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    year = models.IntegerField()
    total_records = models.IntegerField()
    qc_complete_records = models.IntegerField()
    qc_completion_rate = models.FloatField()
    processing_date = models.DateTimeField(auto_now=True)
    csv_file_path = models.CharField(max_length=500, blank=True)
    report_md_path = models.CharField(max_length=500, blank=True)
    report_pdf_path = models.CharField(max_length=500, blank=True)
    visualization_path = models.CharField(max_length=500, blank=True)
    issues_summary = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"Station {self.station.station_id} - {self.year} ({self.qc_completion_rate:.1f}% QC)"

    class Meta:
        unique_together = ['station', 'year']
        ordering = ['station', '-year']

class ThirdPartyBuoyData(models.Model):
    """Model to store third-party buoy data for QC confirmation"""
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField()
    source = models.CharField(
        max_length=50,
        choices=[
            ('era5', 'ERA5 Reanalysis'),
            ('met_eireann', 'Met Éireann'),
            ('noaa', 'NOAA'),
            ('copernicus', 'Copernicus Marine Service'),
            ('other', 'Other Source')
        ],
        default='era5'
    )
    
    # Atmospheric parameters
    air_pressure = models.FloatField(null=True, blank=True, help_text="Air pressure (hPa)")
    air_temperature = models.FloatField(null=True, blank=True, help_text="Air temperature (°C)")
    humidity = models.FloatField(null=True, blank=True, help_text="Relative humidity (%)")
    
    # Wind parameters
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed (knots)")
    wind_direction = models.FloatField(null=True, blank=True, help_text="Wind direction (degrees)")
    wind_gust = models.FloatField(null=True, blank=True, help_text="Wind gust (knots)")
    
    # Wave parameters
    significant_wave_height = models.FloatField(null=True, blank=True, help_text="Significant wave height (m)")
    max_wave_height = models.FloatField(null=True, blank=True, help_text="Maximum wave height (m)")
    wave_period = models.FloatField(null=True, blank=True, help_text="Wave period (s)")
    wave_direction = models.FloatField(null=True, blank=True, help_text="Wave direction (degrees)")
    
    # Water parameters
    sea_temperature = models.FloatField(null=True, blank=True, help_text="Sea surface temperature (°C)")
    salinity = models.FloatField(null=True, blank=True, help_text="Salinity (ppt)")
    
    # Metadata
    data_quality = models.CharField(
        max_length=20,
        choices=[
            ('good', 'Good Quality'),
            ('fair', 'Fair Quality'),
            ('poor', 'Poor Quality'),
            ('unknown', 'Unknown Quality')
        ],
        default='unknown'
    )
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.source} data for Station {self.station.station_id} at {self.timestamp}"

    class Meta:
        unique_together = ['station', 'timestamp', 'source']
        ordering = ['station', '-timestamp']
        verbose_name_plural = "Third Party Buoy Data"

class QCConfirmation(models.Model):
    """Model to store QC confirmation results comparing station data with third-party data"""
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    qc_result = models.ForeignKey(QCResult, on_delete=models.CASCADE, null=True, blank=True)
    year = models.IntegerField()
    
    # Confirmation statistics
    total_comparisons = models.IntegerField(default=0)
    confirmed_records = models.IntegerField(default=0)
    deviation_records = models.IntegerField(default=0)
    confirmation_rate = models.FloatField(default=0.0, help_text="Percentage of confirmed records")
    
    # Parameter-specific confirmation rates
    air_pressure_confirmation = models.FloatField(null=True, blank=True)
    air_temp_confirmation = models.FloatField(null=True, blank=True)
    wind_speed_confirmation = models.FloatField(null=True, blank=True)
    wave_height_confirmation = models.FloatField(null=True, blank=True)
    sea_temp_confirmation = models.FloatField(null=True, blank=True)
    
    # Statistical metrics
    mean_absolute_error = models.JSONField(default=dict, blank=True, help_text="MAE for each parameter")
    root_mean_square_error = models.JSONField(default=dict, blank=True, help_text="RMSE for each parameter")
    correlation_coefficient = models.JSONField(default=dict, blank=True, help_text="Correlation for each parameter")
    
    # Metadata
    third_party_source = models.CharField(max_length=50, default='era5')
    analysis_date = models.DateTimeField(auto_now=True)
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"QC Confirmation for Station {self.station.station_id} - {self.year} ({self.confirmation_rate:.1f}%)"

    class Meta:
        unique_together = ['station', 'year', 'third_party_source']
        ordering = ['station', '-year']
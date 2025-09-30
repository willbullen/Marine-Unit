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

class ThirdPartyDataSource(models.Model):
    """Model representing a third-party data source for confirmation"""
    SOURCE_TYPES = [
        ('noaa', 'NOAA/NDBC'),
        ('copernicus', 'Copernicus Marine Service'),
        ('ukmo', 'UK Met Office'),
        ('manual', 'Manual Upload'),
        ('other', 'Other Source')
    ]
    
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPES)
    description = models.TextField(blank=True)
    api_endpoint = models.URLField(blank=True, help_text="API endpoint URL if applicable")
    update_frequency = models.CharField(max_length=50, blank=True, help_text="e.g., 'hourly', 'daily'")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} ({self.get_source_type_display()})"
    
    class Meta:
        ordering = ['name']

class ThirdPartyData(models.Model):
    """Model to store third-party buoy data for confirmation"""
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    source = models.ForeignKey(ThirdPartyDataSource, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(db_index=True)
    
    # Environmental parameters
    air_pressure = models.FloatField(null=True, blank=True, help_text="Air pressure in hPa")
    air_temp = models.FloatField(null=True, blank=True, help_text="Air temperature in °C")
    humidity = models.FloatField(null=True, blank=True, help_text="Humidity in %")
    wind_speed = models.FloatField(null=True, blank=True, help_text="Wind speed in m/s")
    wind_direction = models.FloatField(null=True, blank=True, help_text="Wind direction in degrees")
    
    # Wave parameters
    wave_height = models.FloatField(null=True, blank=True, help_text="Significant wave height (Hm0) in m")
    wave_height_max = models.FloatField(null=True, blank=True, help_text="Maximum wave height in m")
    wave_period = models.FloatField(null=True, blank=True, help_text="Wave period in s")
    wave_direction = models.FloatField(null=True, blank=True, help_text="Wave direction in degrees")
    
    # Water parameters
    sea_temp = models.FloatField(null=True, blank=True, help_text="Sea temperature in °C")
    
    # Metadata
    data_quality = models.CharField(max_length=20, blank=True, help_text="Quality flag from source")
    raw_data = models.JSONField(default=dict, blank=True, help_text="Original raw data from source")
    imported_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.station.station_id} - {self.source.name} - {self.timestamp}"
    
    class Meta:
        unique_together = ['station', 'source', 'timestamp']
        ordering = ['station', '-timestamp']
        indexes = [
            models.Index(fields=['station', 'timestamp']),
            models.Index(fields=['source', 'timestamp']),
        ]

class DataConfirmation(models.Model):
    """Model to track confirmation/validation against third-party data"""
    CONFIRMATION_STATUS = [
        ('confirmed', 'Confirmed - Data matches within tolerance'),
        ('discrepancy', 'Discrepancy - Significant difference detected'),
        ('missing', 'Missing - No third-party data available'),
        ('pending', 'Pending - Awaiting confirmation')
    ]
    
    station = models.ForeignKey(BuoyStation, on_delete=models.CASCADE)
    timestamp = models.DateTimeField(db_index=True)
    parameter = models.ForeignKey(QCParameter, on_delete=models.CASCADE)
    
    # Station data values
    station_value = models.FloatField(null=True, blank=True)
    station_qc_status = models.IntegerField(help_text="QC indicator from station data")
    
    # Third-party comparison
    third_party_source = models.ForeignKey(ThirdPartyDataSource, on_delete=models.CASCADE, null=True, blank=True)
    third_party_value = models.FloatField(null=True, blank=True)
    difference = models.FloatField(null=True, blank=True, help_text="Absolute difference between values")
    percent_difference = models.FloatField(null=True, blank=True, help_text="Percentage difference")
    
    # Confirmation result
    confirmation_status = models.CharField(max_length=20, choices=CONFIRMATION_STATUS, default='pending')
    tolerance_threshold = models.FloatField(help_text="Tolerance threshold used for comparison")
    notes = models.TextField(blank=True)
    
    confirmed_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.station.station_id} - {self.parameter.name} - {self.timestamp} - {self.confirmation_status}"
    
    class Meta:
        unique_together = ['station', 'timestamp', 'parameter']
        ordering = ['station', '-timestamp', 'parameter']
        indexes = [
            models.Index(fields=['station', 'confirmation_status']),
            models.Index(fields=['timestamp', 'confirmation_status']),
        ]
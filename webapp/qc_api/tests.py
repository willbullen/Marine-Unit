from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from .models import (
    BuoyStation, QCParameter, ThirdPartyDataSource, ThirdPartyData, DataConfirmation
)

class ThirdPartyDataModelTest(TestCase):
    """Test third-party data models"""
    
    def setUp(self):
        """Set up test data"""
        # Create a buoy station
        self.station = BuoyStation.objects.create(
            station_id='62091',
            name='M2 Buoy',
            location_description='Test Location',
            exposure_type='exposed'
        )
        
        # Create a third-party data source
        self.source = ThirdPartyDataSource.objects.create(
            name='Test Source',
            source_type='noaa',
            description='Test data source'
        )
        
        # Create a QC parameter
        self.parameter = QCParameter.objects.create(
            name='airtemp',
            display_name='Air Temperature',
            unit='°C',
            parameter_type='environmental',
            default_min=-40,
            default_max=50
        )
    
    def test_create_third_party_data_source(self):
        """Test creating a third-party data source"""
        source = ThirdPartyDataSource.objects.create(
            name='NOAA NDBC',
            source_type='noaa',
            description='National Data Buoy Center'
        )
        self.assertEqual(source.name, 'NOAA NDBC')
        self.assertEqual(source.source_type, 'noaa')
        self.assertTrue(source.is_active)
    
    def test_create_third_party_data(self):
        """Test creating third-party data records"""
        timestamp = timezone.now()
        data = ThirdPartyData.objects.create(
            station=self.station,
            source=self.source,
            timestamp=timestamp,
            air_temp=15.5,
            wind_speed=8.3,
            wave_height=2.1
        )
        self.assertEqual(data.station, self.station)
        self.assertEqual(data.source, self.source)
        self.assertEqual(data.air_temp, 15.5)
        self.assertEqual(data.wind_speed, 8.3)
        self.assertEqual(data.wave_height, 2.1)
    
    def test_unique_constraint_third_party_data(self):
        """Test unique constraint on third-party data"""
        timestamp = timezone.now()
        ThirdPartyData.objects.create(
            station=self.station,
            source=self.source,
            timestamp=timestamp,
            air_temp=15.5
        )
        
        # Creating duplicate should not raise error (update_or_create pattern)
        # but when creating directly, it should
        from django.db import IntegrityError
        with self.assertRaises(IntegrityError):
            ThirdPartyData.objects.create(
                station=self.station,
                source=self.source,
                timestamp=timestamp,
                air_temp=16.0
            )
    
    def test_create_data_confirmation(self):
        """Test creating data confirmation records"""
        timestamp = timezone.now()
        confirmation = DataConfirmation.objects.create(
            station=self.station,
            timestamp=timestamp,
            parameter=self.parameter,
            station_value=15.5,
            station_qc_status=1,
            third_party_source=self.source,
            third_party_value=15.8,
            difference=0.3,
            percent_difference=1.94,
            confirmation_status='confirmed',
            tolerance_threshold=10.0
        )
        
        self.assertEqual(confirmation.station, self.station)
        self.assertEqual(confirmation.parameter, self.parameter)
        self.assertEqual(confirmation.confirmation_status, 'confirmed')
        self.assertEqual(confirmation.difference, 0.3)
    
    def test_confirmation_status_choices(self):
        """Test confirmation status choices"""
        timestamp = timezone.now()
        
        # Test each status
        for status_code, status_label in DataConfirmation.CONFIRMATION_STATUS:
            confirmation = DataConfirmation.objects.create(
                station=self.station,
                timestamp=timestamp + timedelta(seconds=ord(status_code[0])),  # Unique timestamp
                parameter=self.parameter,
                station_value=15.5,
                station_qc_status=1,
                confirmation_status=status_code,
                tolerance_threshold=10.0
            )
            self.assertEqual(confirmation.confirmation_status, status_code)
            self.assertEqual(confirmation.get_confirmation_status_display(), status_label)

class ThirdPartyDataAPITest(TestCase):
    """Test third-party data API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        from django.contrib.auth.models import User
        
        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            password='testpass123'
        )
        
        self.station = BuoyStation.objects.create(
            station_id='62091',
            name='M2 Buoy',
            location_description='Test Location',
            exposure_type='exposed'
        )
        
        self.source = ThirdPartyDataSource.objects.create(
            name='Test Source',
            source_type='noaa',
            description='Test data source'
        )
        
        # Login the test user
        self.client.login(username='testuser', password='testpass123')
    
    def test_third_party_sources_endpoint(self):
        """Test listing third-party data sources"""
        response = self.client.get('/api/third-party-sources/')
        self.assertEqual(response.status_code, 200)
    
    def test_third_party_data_endpoint(self):
        """Test listing third-party data"""
        response = self.client.get('/api/third-party-data/')
        self.assertEqual(response.status_code, 200)
    
    def test_confirmations_endpoint(self):
        """Test listing confirmations"""
        response = self.client.get('/api/confirmations/')
        self.assertEqual(response.status_code, 200)


from django.core.management.base import BaseCommand
from qc_api.models import BuoyStation, QCParameter, StationQCLimit
import sys
import os

class Command(BaseCommand):
    help = 'Set up initial QC data from existing QC processor configuration'

    def handle(self, *args, **options):
        self.stdout.write('Setting up QC data from existing configuration...')
        
        # Add the QC Scripts directory to path
        qc_scripts_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', 'QC Scripts')
        sys.path.append(qc_scripts_path)
        
        try:
            from buoy_qc_processor import BuoyQCProcessor
            processor = BuoyQCProcessor()
            
            # Create QC parameters from default limits
            self.stdout.write('Creating QC parameters...')
            parameter_mapping = {
                'airpressure': {'display_name': 'Air Pressure', 'unit': 'hPa', 'type': 'environmental'},
                'airtemp': {'display_name': 'Air Temperature', 'unit': '°C', 'type': 'environmental'},
                'humidity': {'display_name': 'Humidity', 'unit': '%', 'type': 'environmental'},
                'seatemp_16': {'display_name': 'Sea Temperature (16)', 'unit': '°C', 'type': 'water'},
                'seatemp_aa': {'display_name': 'Sea Temperature (AA)', 'unit': '°C', 'type': 'water'},
                'windsp': {'display_name': 'Wind Speed', 'unit': 'm/s', 'type': 'environmental'},
                'windgust': {'display_name': 'Wind Gust', 'unit': 'm/s', 'type': 'environmental'},
                'winddir': {'display_name': 'Wind Direction', 'unit': '°', 'type': 'environmental'},
                'hm0': {'display_name': 'Significant Wave Height', 'unit': 'm', 'type': 'wave'},
                'hmax': {'display_name': 'Maximum Wave Height', 'unit': 'm', 'type': 'wave'},
                'tp': {'display_name': 'Wave Period', 'unit': 's', 'type': 'wave'},
                'mdir': {'display_name': 'Mean Wave Direction', 'unit': '°', 'type': 'wave'},
                'salinity_16': {'display_name': 'Salinity', 'unit': 'ppt', 'type': 'water'}
            }
            
            for param_name, param_info in parameter_mapping.items():
                if param_name in processor.default_qc_limits:
                    limits = processor.default_qc_limits[param_name]
                    parameter, created = QCParameter.objects.get_or_create(
                        name=param_name,
                        defaults={
                            'display_name': param_info['display_name'],
                            'unit': param_info['unit'],
                            'parameter_type': param_info['type'],
                            'default_min': limits.get('min'),
                            'default_max': limits.get('max'),
                            'default_spike_threshold': limits.get('spike_threshold'),
                            'description': f"QC parameter for {param_info['display_name']}"
                        }
                    )
                    if created:
                        self.stdout.write(f'  Created parameter: {param_info["display_name"]}')
            
            # Create buoy stations
            self.stdout.write('Creating buoy stations...')
            station_info = {
                '62091': {'name': 'M2 Buoy', 'location': 'Exposed Atlantic Location', 'exposure': 'exposed'},
                '62092': {'name': 'M3 Buoy', 'location': 'Coastal/Sheltered Location', 'exposure': 'coastal'},
                '62093': {'name': 'M4 Buoy', 'location': 'Intermediate Exposure Location', 'exposure': 'intermediate'},
                '62094': {'name': 'M5 Buoy', 'location': 'Variable Conditions Location', 'exposure': 'variable'},
                '62095': {'name': 'M6 Buoy', 'location': 'Unique Location Characteristics', 'exposure': 'unique'}
            }
            
            for station_id, info in station_info.items():
                station, created = BuoyStation.objects.get_or_create(
                    station_id=station_id,
                    defaults={
                        'name': info['name'],
                        'location_description': info['location'],
                        'exposure_type': info['exposure']
                    }
                )
                if created:
                    self.stdout.write(f'  Created station: {station_id} - {info["name"]}')
            
            # Create station-specific QC limits
            self.stdout.write('Creating station-specific QC limits...')
            for station_id, station_limits in processor.station_qc_limits.items():
                try:
                    station = BuoyStation.objects.get(station_id=station_id)
                    for param_name, limits in station_limits.items():
                        try:
                            parameter = QCParameter.objects.get(name=param_name)
                            limit_obj, created = StationQCLimit.objects.get_or_create(
                                station=station,
                                parameter=parameter,
                                defaults={
                                    'min_value': limits.get('min'),
                                    'max_value': limits.get('max'),
                                    'spike_threshold': limits.get('spike_threshold'),
                                    'notes': f'Station-specific limit for {station.exposure_type} location'
                                }
                            )
                            if created:
                                self.stdout.write(f'  Created limit: {station_id} - {param_name}')
                        except QCParameter.DoesNotExist:
                            self.stdout.write(f'  Warning: Parameter {param_name} not found')
                except BuoyStation.DoesNotExist:
                    self.stdout.write(f'  Warning: Station {station_id} not found')
            
            self.stdout.write(self.style.SUCCESS('QC data setup completed successfully!'))
            
        except ImportError as e:
            self.stdout.write(self.style.ERROR(f'Could not import QC processor: {e}'))
            self.stdout.write('Make sure the QC Scripts directory is accessible.')
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error setting up QC data: {e}'))

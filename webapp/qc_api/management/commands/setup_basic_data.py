from django.core.management.base import BaseCommand
from qc_api.models import BuoyStation, QCParameter

class Command(BaseCommand):
    help = 'Setup basic buoy stations and QC parameters'

    def handle(self, *args, **options):
        self.stdout.write('Setting up basic buoy stations and QC parameters...')
        
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
            else:
                self.stdout.write(f'  Already exists: {station_id} - {info["name"]}')
        
        # Create QC parameters
        self.stdout.write('\nCreating QC parameters...')
        parameter_mapping = {
            'airpressure': {'display_name': 'Air Pressure', 'unit': 'hPa', 'type': 'environmental', 'min': 950, 'max': 1050},
            'airtemp': {'display_name': 'Air Temperature', 'unit': '°C', 'type': 'environmental', 'min': -20, 'max': 40},
            'humidity': {'display_name': 'Humidity', 'unit': '%', 'type': 'environmental', 'min': 0, 'max': 100},
            'windsp': {'display_name': 'Wind Speed', 'unit': 'm/s', 'type': 'environmental', 'min': 0, 'max': 50},
            'winddir': {'display_name': 'Wind Direction', 'unit': 'degrees', 'type': 'environmental', 'min': 0, 'max': 360},
            'hm0': {'display_name': 'Significant Wave Height', 'unit': 'm', 'type': 'wave', 'min': 0, 'max': 15},
            'hmax': {'display_name': 'Maximum Wave Height', 'unit': 'm', 'type': 'wave', 'min': 0, 'max': 25},
            'tp': {'display_name': 'Wave Period', 'unit': 's', 'type': 'wave', 'min': 1, 'max': 25},
            'mdir': {'display_name': 'Wave Direction', 'unit': 'degrees', 'type': 'wave', 'min': 0, 'max': 360},
            'seatemp_aa': {'display_name': 'Sea Temperature', 'unit': '°C', 'type': 'water', 'min': -2, 'max': 30}
        }
        
        for param_name, param_info in parameter_mapping.items():
            param, created = QCParameter.objects.get_or_create(
                name=param_name,
                defaults={
                    'display_name': param_info['display_name'],
                    'unit': param_info['unit'],
                    'parameter_type': param_info['type'],
                    'default_min': param_info.get('min'),
                    'default_max': param_info.get('max'),
                    'description': f"QC parameter for {param_info['display_name']}"
                }
            )
            if created:
                self.stdout.write(f'  Created parameter: {param_info["display_name"]}')
            else:
                self.stdout.write(f'  Already exists: {param_info["display_name"]}')
        
        self.stdout.write(self.style.SUCCESS('\nBasic setup completed successfully!'))

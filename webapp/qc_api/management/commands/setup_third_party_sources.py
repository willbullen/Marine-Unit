from django.core.management.base import BaseCommand
from qc_api.models import ThirdPartyDataSource

class Command(BaseCommand):
    help = 'Set up initial third-party data sources for buoy data confirmation'

    def handle(self, *args, **options):
        self.stdout.write('Setting up third-party data sources...')
        
        sources = [
            {
                'name': 'NOAA NDBC',
                'source_type': 'noaa',
                'description': 'National Data Buoy Center - Provides real-time and historical ocean observations',
                'api_endpoint': 'https://www.ndbc.noaa.gov/data/realtime2/',
                'update_frequency': 'hourly',
                'is_active': True
            },
            {
                'name': 'Copernicus Marine Service',
                'source_type': 'copernicus',
                'description': 'EU Copernicus Marine Environment Monitoring Service',
                'api_endpoint': 'https://marine.copernicus.eu/',
                'update_frequency': 'daily',
                'is_active': True
            },
            {
                'name': 'UK Met Office Marine',
                'source_type': 'ukmo',
                'description': 'UK Met Office marine observations and forecasts',
                'api_endpoint': 'https://www.metoffice.gov.uk/weather/marine',
                'update_frequency': 'hourly',
                'is_active': True
            },
            {
                'name': 'Manual Upload',
                'source_type': 'manual',
                'description': 'Manually uploaded third-party data from various sources',
                'api_endpoint': '',
                'update_frequency': 'as needed',
                'is_active': True
            }
        ]
        
        created_count = 0
        for source_data in sources:
            source, created = ThirdPartyDataSource.objects.get_or_create(
                name=source_data['name'],
                defaults={
                    'source_type': source_data['source_type'],
                    'description': source_data['description'],
                    'api_endpoint': source_data['api_endpoint'],
                    'update_frequency': source_data['update_frequency'],
                    'is_active': source_data['is_active']
                }
            )
            
            if created:
                self.stdout.write(f'  Created: {source.name}')
                created_count += 1
            else:
                self.stdout.write(f'  Already exists: {source.name}')
        
        self.stdout.write(self.style.SUCCESS(f'\nSetup completed! Created {created_count} new sources.'))

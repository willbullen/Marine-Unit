"""
Management command to import third-party buoy data for QC confirmation

This command imports data from external sources (ERA5, Met Éireann, NOAA, etc.)
to be used for validating and confirming QC'd buoy data.

Usage:
    python manage.py import_third_party_data --source era5 --file path/to/data.csv
    python manage.py import_third_party_data --source met_eireann --station 62091
"""

from django.core.management.base import BaseCommand, CommandError
from qc_api.models import BuoyStation, ThirdPartyBuoyData
import pandas as pd
import os
from datetime import datetime


class Command(BaseCommand):
    help = 'Import third-party buoy data for QC confirmation'

    def add_arguments(self, parser):
        parser.add_argument(
            '--source',
            type=str,
            default='era5',
            choices=['era5', 'met_eireann', 'noaa', 'copernicus', 'other'],
            help='Source of the third-party data'
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Path to CSV file containing third-party data'
        )
        parser.add_argument(
            '--station',
            type=str,
            help='Station ID to import data for (optional, if not in file)'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Clear existing third-party data before import'
        )

    def handle(self, *args, **options):
        source = options['source']
        file_path = options.get('file')
        station_id = options.get('station')
        clear_existing = options['clear']

        self.stdout.write(f'Importing third-party data from {source}...')

        if not file_path:
            # Create sample third-party data directory if it doesn't exist
            sample_dir = os.path.join(
                os.path.dirname(__file__), 
                '..', '..', '..', '..', 
                'Third Party Data'
            )
            os.makedirs(sample_dir, exist_ok=True)
            
            self.stdout.write(
                self.style.WARNING(
                    f'\nNo file specified. To import third-party data:\n'
                    f'1. Place CSV files in: {sample_dir}\n'
                    f'2. Run: python manage.py import_third_party_data --source {source} --file path/to/file.csv\n\n'
                    f'CSV format should include columns:\n'
                    f'  - station_id (required)\n'
                    f'  - timestamp (required, format: YYYY-MM-DD HH:MM:SS)\n'
                    f'  - air_pressure, air_temperature, humidity\n'
                    f'  - wind_speed, wind_direction, wind_gust\n'
                    f'  - significant_wave_height, max_wave_height, wave_period, wave_direction\n'
                    f'  - sea_temperature, salinity\n'
                    f'  - data_quality (optional: good/fair/poor/unknown)\n'
                )
            )
            return

        # Load the CSV file
        if not os.path.exists(file_path):
            raise CommandError(f'File not found: {file_path}')

        self.stdout.write(f'Loading data from {file_path}...')
        
        try:
            df = pd.read_csv(file_path)
        except Exception as e:
            raise CommandError(f'Error reading CSV file: {e}')

        # Validate required columns
        required_cols = ['station_id', 'timestamp']
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise CommandError(f'Missing required columns: {missing_cols}')

        # Clear existing data if requested
        if clear_existing:
            if station_id:
                count = ThirdPartyBuoyData.objects.filter(
                    station_id=station_id,
                    source=source
                ).delete()[0]
                self.stdout.write(f'Deleted {count} existing records for station {station_id}')
            else:
                count = ThirdPartyBuoyData.objects.filter(source=source).delete()[0]
                self.stdout.write(f'Deleted {count} existing records from {source}')

        # Column mapping from CSV to model fields
        column_mapping = {
            'air_pressure': 'air_pressure',
            'airpressure': 'air_pressure',
            'air_temperature': 'air_temperature',
            'airtemp': 'air_temperature',
            'humidity': 'humidity',
            'wind_speed': 'wind_speed',
            'windsp': 'wind_speed',
            'wind_direction': 'wind_direction',
            'winddir': 'wind_direction',
            'wind_gust': 'wind_gust',
            'windgust': 'wind_gust',
            'significant_wave_height': 'significant_wave_height',
            'hm0': 'significant_wave_height',
            'max_wave_height': 'max_wave_height',
            'hmax': 'max_wave_height',
            'wave_period': 'wave_period',
            'tp': 'wave_period',
            'wave_direction': 'wave_direction',
            'mdir': 'wave_direction',
            'sea_temperature': 'sea_temperature',
            'seatemp': 'sea_temperature',
            'seatemp_aa': 'sea_temperature',
            'salinity': 'salinity',
            'data_quality': 'data_quality',
        }

        # Import data
        imported_count = 0
        skipped_count = 0
        error_count = 0

        for idx, row in df.iterrows():
            try:
                # Get or validate station
                row_station_id = station_id if station_id else str(row['station_id'])
                
                try:
                    station = BuoyStation.objects.get(station_id=row_station_id)
                except BuoyStation.DoesNotExist:
                    self.stdout.write(
                        self.style.WARNING(f'Station {row_station_id} not found, skipping...')
                    )
                    skipped_count += 1
                    continue

                # Parse timestamp
                timestamp = pd.to_datetime(row['timestamp'])

                # Build data dict with available fields
                data = {
                    'station': station,
                    'timestamp': timestamp,
                    'source': source,
                }

                # Map CSV columns to model fields
                for csv_col, model_field in column_mapping.items():
                    if csv_col in df.columns and pd.notna(row[csv_col]):
                        data[model_field] = row[csv_col]

                # Create or update record
                obj, created = ThirdPartyBuoyData.objects.update_or_create(
                    station=station,
                    timestamp=timestamp,
                    source=source,
                    defaults=data
                )

                imported_count += 1
                
                if idx % 100 == 0 and idx > 0:
                    self.stdout.write(f'  Processed {idx} records...')

            except Exception as e:
                error_count += 1
                if error_count <= 5:  # Only show first 5 errors
                    self.stdout.write(
                        self.style.ERROR(f'Error importing row {idx}: {e}')
                    )

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS(f'Import completed!'))
        self.stdout.write(f'  Imported: {imported_count} records')
        self.stdout.write(f'  Skipped: {skipped_count} records')
        if error_count > 0:
            self.stdout.write(self.style.WARNING(f'  Errors: {error_count} records'))
        self.stdout.write('='*50)

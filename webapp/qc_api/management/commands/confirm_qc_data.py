"""
Management command to confirm QC data using third-party buoy data

This command compares QC'd buoy data with third-party data sources to validate
the quality control results and generate confirmation statistics.

Usage:
    python manage.py confirm_qc_data --station 62091 --year 2023
    python manage.py confirm_qc_data --all
"""

from django.core.management.base import BaseCommand, CommandError
from qc_api.models import BuoyStation, ThirdPartyBuoyData, QCResult, QCConfirmation
import pandas as pd
import numpy as np
import os
from datetime import datetime, timedelta
import sys


class Command(BaseCommand):
    help = 'Confirm QC data using third-party buoy data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--station',
            type=str,
            help='Station ID to confirm QC data for'
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year to confirm QC data for'
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Confirm QC data for all stations and years'
        )
        parser.add_argument(
            '--source',
            type=str,
            default='era5',
            help='Third-party data source to use for confirmation'
        )
        parser.add_argument(
            '--tolerance',
            type=int,
            default=60,
            help='Time tolerance in minutes for matching records (default: 60)'
        )

    def handle(self, *args, **options):
        station_id = options.get('station')
        year = options.get('year')
        process_all = options['all']
        source = options['source']
        tolerance_minutes = options['tolerance']

        # Add QC Scripts directory to path to import BuoyQCProcessor
        qc_scripts_path = os.path.join(
            os.path.dirname(__file__), 
            '..', '..', '..', '..', 
            'QC'
        )
        sys.path.insert(0, qc_scripts_path)

        self.stdout.write('='*60)
        self.stdout.write('QC Data Confirmation using Third-Party Data')
        self.stdout.write('='*60)

        if process_all:
            # Process all stations and years that have QC results
            qc_results = QCResult.objects.all()
            for qc_result in qc_results:
                self.confirm_station_year(
                    qc_result.station.station_id,
                    qc_result.year,
                    source,
                    tolerance_minutes
                )
        elif station_id and year:
            # Process specific station and year
            self.confirm_station_year(station_id, year, source, tolerance_minutes)
        else:
            raise CommandError('Please specify --station and --year, or use --all')

    def confirm_station_year(self, station_id, year, source, tolerance_minutes):
        """Confirm QC data for a specific station and year"""
        self.stdout.write(f'\nProcessing Station {station_id} - {year}...')
        
        try:
            station = BuoyStation.objects.get(station_id=station_id)
        except BuoyStation.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'Station {station_id} not found'))
            return

        # Get QC result if it exists
        try:
            qc_result = QCResult.objects.get(station=station, year=year)
        except QCResult.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'No QC results found for {station_id} - {year}'))
            qc_result = None

        # Load QC'd data
        qc_data_dir = os.path.join(
            os.path.dirname(__file__),
            '..', '..', '..', '..', 
            'QC', 'Data'
        )
        qc_file = os.path.join(qc_data_dir, f'buoy_{station_id}_{year}_qcd.csv')
        
        if not os.path.exists(qc_file):
            self.stdout.write(self.style.WARNING(f'QC data file not found: {qc_file}'))
            return

        # Load QC data
        self.stdout.write(f'  Loading QC data from {os.path.basename(qc_file)}...')
        qc_df = pd.read_csv(qc_file)
        qc_df['time'] = pd.to_datetime(qc_df['time'], errors='coerce')
        
        # Filter to only QC-approved records (qc_ind = 1)
        qc_approved = qc_df[qc_df['qc_ind'] == 1].copy()
        self.stdout.write(f'  Found {len(qc_approved):,} QC-approved records')

        # Load third-party data for this station and year
        start_date = datetime(year, 1, 1)
        end_date = datetime(year + 1, 1, 1)
        
        third_party_data = ThirdPartyBuoyData.objects.filter(
            station=station,
            source=source,
            timestamp__gte=start_date,
            timestamp__lt=end_date
        ).order_by('timestamp')

        if not third_party_data.exists():
            self.stdout.write(
                self.style.WARNING(
                    f'  No third-party data from {source} found for {station_id} in {year}'
                )
            )
            return

        self.stdout.write(f'  Found {third_party_data.count():,} third-party records from {source}')

        # Convert third-party data to DataFrame
        tp_data = []
        for record in third_party_data:
            tp_data.append({
                'timestamp': record.timestamp,
                'air_pressure': record.air_pressure,
                'air_temperature': record.air_temperature,
                'humidity': record.humidity,
                'wind_speed': record.wind_speed,
                'wind_direction': record.wind_direction,
                'wind_gust': record.wind_gust,
                'significant_wave_height': record.significant_wave_height,
                'max_wave_height': record.max_wave_height,
                'wave_period': record.wave_period,
                'wave_direction': record.wave_direction,
                'sea_temperature': record.sea_temperature,
                'salinity': record.salinity,
            })
        
        tp_df = pd.DataFrame(tp_data)

        # Perform comparison
        self.stdout.write(f'  Comparing QC data with third-party data...')
        
        comparison_results = self.compare_datasets(
            qc_approved, 
            tp_df, 
            tolerance_minutes
        )

        # Calculate statistics
        stats = self.calculate_statistics(comparison_results)

        # Create or update QC confirmation record
        confirmation, created = QCConfirmation.objects.update_or_create(
            station=station,
            year=year,
            third_party_source=source,
            defaults={
                'qc_result': qc_result,
                'total_comparisons': stats['total_comparisons'],
                'confirmed_records': stats['confirmed_records'],
                'deviation_records': stats['deviation_records'],
                'confirmation_rate': stats['confirmation_rate'],
                'air_pressure_confirmation': stats.get('air_pressure_confirmation'),
                'air_temp_confirmation': stats.get('air_temp_confirmation'),
                'wind_speed_confirmation': stats.get('wind_speed_confirmation'),
                'wave_height_confirmation': stats.get('wave_height_confirmation'),
                'sea_temp_confirmation': stats.get('sea_temp_confirmation'),
                'mean_absolute_error': stats['mean_absolute_error'],
                'root_mean_square_error': stats['root_mean_square_error'],
                'correlation_coefficient': stats['correlation_coefficient'],
            }
        )

        # Display results
        self.stdout.write('\n  ' + '-'*50)
        self.stdout.write(self.style.SUCCESS('  Confirmation Results:'))
        self.stdout.write(f'  Total Comparisons: {stats["total_comparisons"]:,}')
        self.stdout.write(f'  Confirmed Records: {stats["confirmed_records"]:,}')
        self.stdout.write(f'  Deviation Records: {stats["deviation_records"]:,}')
        self.stdout.write(f'  Confirmation Rate: {stats["confirmation_rate"]:.1f}%')
        
        if stats.get('air_pressure_confirmation'):
            self.stdout.write(f'\n  Parameter Confirmation Rates:')
            self.stdout.write(f'    Air Pressure: {stats.get("air_pressure_confirmation", 0):.1f}%')
            self.stdout.write(f'    Air Temperature: {stats.get("air_temp_confirmation", 0):.1f}%')
            self.stdout.write(f'    Wind Speed: {stats.get("wind_speed_confirmation", 0):.1f}%')
            self.stdout.write(f'    Wave Height: {stats.get("wave_height_confirmation", 0):.1f}%')
            self.stdout.write(f'    Sea Temperature: {stats.get("sea_temp_confirmation", 0):.1f}%')
        
        self.stdout.write('  ' + '-'*50)

    def compare_datasets(self, qc_df, tp_df, tolerance_minutes):
        """Compare QC data with third-party data"""
        results = {
            'air_pressure': [],
            'air_temperature': [],
            'wind_speed': [],
            'wave_height': [],
            'sea_temperature': [],
        }

        tolerance = timedelta(minutes=tolerance_minutes)

        for _, qc_row in qc_df.iterrows():
            qc_time = qc_row['time']
            
            # Find closest third-party record within tolerance
            time_diffs = abs(tp_df['timestamp'] - qc_time)
            closest_idx = time_diffs.idxmin() if len(time_diffs) > 0 else None
            
            if closest_idx is not None and time_diffs[closest_idx] <= tolerance:
                tp_row = tp_df.loc[closest_idx]
                
                # Compare air pressure
                if pd.notna(qc_row.get('airpressure')) and pd.notna(tp_row.get('air_pressure')):
                    results['air_pressure'].append({
                        'qc': qc_row['airpressure'],
                        'tp': tp_row['air_pressure'],
                        'diff': abs(qc_row['airpressure'] - tp_row['air_pressure'])
                    })
                
                # Compare air temperature
                if pd.notna(qc_row.get('airtemp')) and pd.notna(tp_row.get('air_temperature')):
                    results['air_temperature'].append({
                        'qc': qc_row['airtemp'],
                        'tp': tp_row['air_temperature'],
                        'diff': abs(qc_row['airtemp'] - tp_row['air_temperature'])
                    })
                
                # Compare wind speed
                if pd.notna(qc_row.get('windsp')) and pd.notna(tp_row.get('wind_speed')):
                    results['wind_speed'].append({
                        'qc': qc_row['windsp'],
                        'tp': tp_row['wind_speed'],
                        'diff': abs(qc_row['windsp'] - tp_row['wind_speed'])
                    })
                
                # Compare wave height (hm0)
                if pd.notna(qc_row.get('hm0')) and pd.notna(tp_row.get('significant_wave_height')):
                    results['wave_height'].append({
                        'qc': qc_row['hm0'],
                        'tp': tp_row['significant_wave_height'],
                        'diff': abs(qc_row['hm0'] - tp_row['significant_wave_height'])
                    })
                
                # Compare sea temperature
                if pd.notna(qc_row.get('seatemp_aa')) and pd.notna(tp_row.get('sea_temperature')):
                    results['sea_temperature'].append({
                        'qc': qc_row['seatemp_aa'],
                        'tp': tp_row['sea_temperature'],
                        'diff': abs(qc_row['seatemp_aa'] - tp_row['sea_temperature'])
                    })

        return results

    def calculate_statistics(self, comparison_results):
        """Calculate statistical metrics for comparison"""
        stats = {
            'total_comparisons': 0,
            'confirmed_records': 0,
            'deviation_records': 0,
            'confirmation_rate': 0.0,
            'mean_absolute_error': {},
            'root_mean_square_error': {},
            'correlation_coefficient': {},
        }

        # Thresholds for confirmation (can be adjusted)
        thresholds = {
            'air_pressure': 5.0,  # hPa
            'air_temperature': 2.0,  # °C
            'wind_speed': 5.0,  # knots
            'wave_height': 1.0,  # m
            'sea_temperature': 2.0,  # °C
        }

        total_params_compared = 0
        confirmed_params = 0

        for param, comparisons in comparison_results.items():
            if not comparisons:
                continue

            total_params_compared += len(comparisons)
            
            qc_values = [c['qc'] for c in comparisons]
            tp_values = [c['tp'] for c in comparisons]
            diffs = [c['diff'] for c in comparisons]

            # Calculate MAE
            mae = np.mean(diffs)
            stats['mean_absolute_error'][param] = round(mae, 3)

            # Calculate RMSE
            rmse = np.sqrt(np.mean([d**2 for d in diffs]))
            stats['root_mean_square_error'][param] = round(rmse, 3)

            # Calculate correlation
            if len(qc_values) > 1:
                corr = np.corrcoef(qc_values, tp_values)[0, 1]
                stats['correlation_coefficient'][param] = round(corr, 3)

            # Count confirmed records (within threshold)
            threshold = thresholds.get(param, 999999)
            param_confirmed = sum(1 for d in diffs if d <= threshold)
            confirmed_params += param_confirmed

            # Calculate parameter-specific confirmation rate
            param_rate = (param_confirmed / len(comparisons)) * 100 if comparisons else 0
            
            if param == 'air_pressure':
                stats['air_pressure_confirmation'] = round(param_rate, 1)
            elif param == 'air_temperature':
                stats['air_temp_confirmation'] = round(param_rate, 1)
            elif param == 'wind_speed':
                stats['wind_speed_confirmation'] = round(param_rate, 1)
            elif param == 'wave_height':
                stats['wave_height_confirmation'] = round(param_rate, 1)
            elif param == 'sea_temperature':
                stats['sea_temp_confirmation'] = round(param_rate, 1)

        stats['total_comparisons'] = total_params_compared
        stats['confirmed_records'] = confirmed_params
        stats['deviation_records'] = total_params_compared - confirmed_params
        stats['confirmation_rate'] = round(
            (confirmed_params / total_params_compared * 100) if total_params_compared > 0 else 0,
            1
        )

        return stats

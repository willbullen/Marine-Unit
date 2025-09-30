"""
Third-Party Data Confirmation Example
======================================

This script demonstrates how to:
1. Import third-party buoy data
2. Compare it with station QC'd data
3. Generate confirmation reports

Usage:
    python demo_third_party_confirmation.py
"""

import os
import sys
import django

# Setup Django environment
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'buoy_qc_web.settings')
django.setup()

from datetime import datetime, timedelta
from qc_api.models import (
    BuoyStation, ThirdPartyDataSource, ThirdPartyData,
    DataConfirmation, QCParameter
)

def create_sample_third_party_data():
    """Create sample third-party data for demonstration"""
    print("=" * 60)
    print("Creating Sample Third-Party Data")
    print("=" * 60)
    
    # Get a station
    try:
        station = BuoyStation.objects.get(station_id='62091')
        print(f"✓ Using station: {station.name} ({station.station_id})")
    except BuoyStation.DoesNotExist:
        print("✗ Station 62091 not found. Please run setup_qc_data command first.")
        return
    
    # Get or create a data source
    source, created = ThirdPartyDataSource.objects.get_or_create(
        name='NOAA NDBC',
        defaults={
            'source_type': 'noaa',
            'description': 'National Data Buoy Center',
            'update_frequency': 'hourly',
            'is_active': True
        }
    )
    print(f"{'✓ Created' if created else '✓ Using'} data source: {source.name}")
    
    # Create sample data for the past 7 days
    base_time = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    records_created = 0
    
    print(f"\nImporting sample data for the past 7 days...")
    for day in range(7):
        for hour in range(0, 24, 3):  # Every 3 hours
            timestamp = base_time - timedelta(days=day, hours=hour)
            
            # Create realistic sample data
            data, created = ThirdPartyData.objects.update_or_create(
                station=station,
                source=source,
                timestamp=timestamp,
                defaults={
                    'air_pressure': 1013.25 + (day * 0.5),
                    'air_temp': 12.5 + (day * 0.3),
                    'humidity': 75.0 + (day * 1.2),
                    'wind_speed': 8.0 + (day * 0.8),
                    'wind_direction': 270.0 + (day * 5),
                    'wave_height': 2.1 + (day * 0.2),
                    'wave_height_max': 3.2 + (day * 0.3),
                    'wave_period': 8.5 + (day * 0.1),
                    'wave_direction': 280.0 + (day * 3),
                    'sea_temp': 11.0 + (day * 0.1),
                    'data_quality': 'good'
                }
            )
            if created:
                records_created += 1
    
    print(f"✓ Imported {records_created} third-party data records")
    
    # Display summary
    total_records = ThirdPartyData.objects.filter(station=station, source=source).count()
    print(f"\nTotal third-party records for {station.station_id}: {total_records}")
    
    # Show latest record
    latest = ThirdPartyData.objects.filter(station=station, source=source).order_by('-timestamp').first()
    if latest:
        print(f"\nLatest record ({latest.timestamp}):")
        print(f"  Air Temp: {latest.air_temp}°C")
        print(f"  Wind Speed: {latest.wind_speed} m/s")
        print(f"  Wave Height: {latest.wave_height} m")

def create_sample_confirmations():
    """Create sample data confirmations"""
    print("\n" + "=" * 60)
    print("Creating Sample Data Confirmations")
    print("=" * 60)
    
    try:
        station = BuoyStation.objects.get(station_id='62091')
        source = ThirdPartyDataSource.objects.get(name='NOAA NDBC')
        
        # Get some parameters
        parameters = ['airtemp', 'windsp', 'hm0']
        confirmations_created = 0
        
        for param_name in parameters:
            try:
                param = QCParameter.objects.get(name=param_name)
                
                # Get third-party data
                third_party_records = ThirdPartyData.objects.filter(
                    station=station,
                    source=source
                ).order_by('-timestamp')[:10]  # Last 10 records
                
                for tp_data in third_party_records:
                    # Simulate station values (would come from actual QC'd data)
                    station_value = None
                    third_party_value = None
                    
                    if param_name == 'airtemp' and tp_data.air_temp:
                        station_value = tp_data.air_temp + 0.2  # Small difference
                        third_party_value = tp_data.air_temp
                    elif param_name == 'windsp' and tp_data.wind_speed:
                        station_value = tp_data.wind_speed - 0.3
                        third_party_value = tp_data.wind_speed
                    elif param_name == 'hm0' and tp_data.wave_height:
                        station_value = tp_data.wave_height + 0.1
                        third_party_value = tp_data.wave_height
                    
                    if station_value and third_party_value:
                        difference = abs(station_value - third_party_value)
                        percent_diff = (difference / third_party_value * 100) if third_party_value != 0 else 0
                        
                        # Determine status based on tolerance
                        tolerance = 10.0  # 10% tolerance
                        if percent_diff <= tolerance:
                            status = 'confirmed'
                        else:
                            status = 'discrepancy'
                        
                        confirmation, created = DataConfirmation.objects.update_or_create(
                            station=station,
                            timestamp=tp_data.timestamp,
                            parameter=param,
                            defaults={
                                'station_value': station_value,
                                'station_qc_status': 1,  # QC passed
                                'third_party_source': source,
                                'third_party_value': third_party_value,
                                'difference': difference,
                                'percent_difference': percent_diff,
                                'confirmation_status': status,
                                'tolerance_threshold': tolerance
                            }
                        )
                        
                        if created:
                            confirmations_created += 1
                
            except QCParameter.DoesNotExist:
                print(f"✗ Parameter {param_name} not found")
                continue
        
        print(f"✓ Created {confirmations_created} confirmation records")
        
        # Display summary
        total_confirmations = DataConfirmation.objects.filter(station=station).count()
        confirmed = DataConfirmation.objects.filter(station=station, confirmation_status='confirmed').count()
        discrepancies = DataConfirmation.objects.filter(station=station, confirmation_status='discrepancy').count()
        
        print(f"\nConfirmation Summary for {station.station_id}:")
        print(f"  Total: {total_confirmations}")
        print(f"  Confirmed: {confirmed}")
        print(f"  Discrepancies: {discrepancies}")
        print(f"  Confirmation Rate: {(confirmed/total_confirmations*100):.1f}%" if total_confirmations > 0 else "  N/A")
        
    except Exception as e:
        print(f"✗ Error creating confirmations: {e}")

def display_confirmation_report():
    """Display a confirmation report"""
    print("\n" + "=" * 60)
    print("Third-Party Data Confirmation Report")
    print("=" * 60)
    
    try:
        station = BuoyStation.objects.get(station_id='62091')
        
        print(f"\nStation: {station.name} ({station.station_id})")
        print(f"Location: {station.location_description}")
        print(f"Exposure: {station.get_exposure_type_display()}")
        
        # Get all confirmations grouped by parameter
        parameters = QCParameter.objects.filter(
            dataconfirmation__station=station
        ).distinct()
        
        print(f"\n{'Parameter':<20} {'Total':>8} {'Confirmed':>10} {'Discrepancy':>12} {'Rate':>8}")
        print("-" * 60)
        
        for param in parameters:
            confirmations = DataConfirmation.objects.filter(
                station=station,
                parameter=param
            )
            total = confirmations.count()
            confirmed = confirmations.filter(confirmation_status='confirmed').count()
            discrepancy = confirmations.filter(confirmation_status='discrepancy').count()
            rate = (confirmed / total * 100) if total > 0 else 0
            
            print(f"{param.display_name:<20} {total:>8} {confirmed:>10} {discrepancy:>12} {rate:>7.1f}%")
        
        # Show recent discrepancies
        recent_discrepancies = DataConfirmation.objects.filter(
            station=station,
            confirmation_status='discrepancy'
        ).order_by('-timestamp')[:5]
        
        if recent_discrepancies.exists():
            print(f"\nRecent Discrepancies:")
            print(f"{'Timestamp':<20} {'Parameter':<15} {'Station':>10} {'3rd Party':>10} {'Diff':>8}")
            print("-" * 70)
            
            for disc in recent_discrepancies:
                print(f"{disc.timestamp.strftime('%Y-%m-%d %H:%M'):<20} "
                      f"{disc.parameter.name:<15} "
                      f"{disc.station_value:>10.2f} "
                      f"{disc.third_party_value:>10.2f} "
                      f"{disc.difference:>8.2f}")
        
    except BuoyStation.DoesNotExist:
        print("✗ Station not found")

def main():
    """Main function"""
    print("\n" + "=" * 60)
    print("THIRD-PARTY DATA CONFIRMATION DEMONSTRATION")
    print("=" * 60)
    
    create_sample_third_party_data()
    create_sample_confirmations()
    display_confirmation_report()
    
    print("\n" + "=" * 60)
    print("Demonstration Complete!")
    print("=" * 60)
    print("\nNext Steps:")
    print("1. Access the Django admin at http://localhost:8000/admin/")
    print("2. View third-party data sources, imported data, and confirmations")
    print("3. Use the API endpoints to:")
    print("   - Import third-party data: POST /api/import-third-party/")
    print("   - Run confirmations: POST /api/run-confirmation/")
    print("   - View confirmation summary: GET /api/stations/{station_id}/confirmation-summary/")

if __name__ == '__main__':
    main()

"""
Test QC Limits Loading Script
============================
Quick test to verify that QC limits are loaded correctly from CSV file
"""

import sys
import os

# Add parent directory to path to import the processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from buoy_qc_processor import BuoyQCProcessor

def test_qc_limits_loading():
    """Test that QC limits are loaded correctly from CSV"""
    print("Testing QC Limits Loading...")
    print("=" * 40)
    
    # Create processor instance
    processor = BuoyQCProcessor()
    
    # Display loaded limits
    processor.display_qc_limits()
    
    # Test getting limits for specific parameters
    print("\nTesting limit retrieval:")
    test_params = ['hm0', 'airtemp', 'windsp']
    test_stations = ['62091', '62092', 'default']
    
    for param in test_params:
        print(f"\nParameter: {param}")
        for station in test_stations:
            limits = processor.get_station_qc_limits(station, param)
            if limits:
                print(f"  Station {station}: {limits}")
            else:
                print(f"  Station {station}: No limits found")
    
    # Test saving limits back to CSV
    print("\nTesting CSV save functionality...")
    test_output = "test_qc_limits_output.csv"
    if processor.save_qc_limits_to_csv(test_output):
        print(f"Successfully saved to {test_output}")
        # Clean up test file
        if os.path.exists(test_output):
            os.remove(test_output)
            print("Test file cleaned up")
    else:
        print("Failed to save to CSV")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_qc_limits_loading()

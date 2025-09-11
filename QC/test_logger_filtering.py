#!/usr/bin/env python3
"""
Test Logger Filtering Script
============================
Test script to verify that the QC processor correctly filters data by live logger
"""

import sys
import os
import pandas as pd
from datetime import datetime

# Add parent directory to path to import the processor
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from QC_Scripts.buoy_qc_processor import BuoyQCProcessor

def test_logger_filtering():
    """Test that logger filtering is working correctly"""
    print("Testing Logger Filtering...")
    print("=" * 40)
    
    # Create processor instance
    processor = BuoyQCProcessor()
    
    # Test logger information loading
    print(f"\nLogger information loaded for {len(processor.logger_info)} stations")
    
    for station, loggers in processor.logger_info.items():
        print(f"\nStation {station}:")
        live_loggers = [lg for lg in loggers if lg['is_live']]
        print(f"  Total loggers: {len(loggers)}")
        print(f"  Live loggers: {len(live_loggers)}")
        
        for logger in loggers:
            status = "LIVE" if logger['is_live'] else "inactive"
            end_str = logger['end_time'].strftime('%Y-%m-%d') if logger['end_time'] else 'Present'
            print(f"    {logger['logger_id']}: {status} from {logger['start_time'].strftime('%Y-%m-%d')} to {end_str}")
    
    # Test live logger detection for specific time periods
    print(f"\nTesting live logger detection:")
    
    # Test case 1: Station 62091 in 2023
    test_station = "62091"
    test_start = datetime(2023, 1, 1)
    test_end = datetime(2023, 12, 31)
    
    live_logger = processor.get_live_logger_for_period(test_station, test_start, test_end)
    if live_logger:
        print(f"  {test_station} 2023: Live logger = {live_logger['logger_id']}")
        print(f"    Active: {live_logger['start_time'].strftime('%Y-%m-%d')} to {live_logger['end_time'].strftime('%Y-%m-%d') if live_logger['end_time'] else 'Present'}")
    else:
        print(f"  {test_station} 2023: No live logger found")
    
    # Test case 2: Station 62092 in 2024
    test_station = "62092"
    test_start = datetime(2024, 1, 1)
    test_end = datetime(2024, 12, 31)
    
    live_logger = processor.get_live_logger_for_period(test_station, test_start, test_end)
    if live_logger:
        print(f"  {test_station} 2024: Live logger = {live_logger['logger_id']}")
        print(f"    Active: {live_logger['start_time'].strftime('%Y-%m-%d')} to {live_logger['end_time'].strftime('%Y-%m-%d') if live_logger['end_time'] else 'Present'}")
    else:
        print(f"  {test_station} 2024: No live logger found")
    
    print("\nTest completed!")

if __name__ == "__main__":
    test_logger_filtering()

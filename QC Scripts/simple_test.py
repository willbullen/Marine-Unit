#!/usr/bin/env python3
"""
Simple test script to verify QC limits system
"""

import sys
import os

print("Simple test script starting...")
print(f"Python version: {sys.version}")
print(f"Current directory: {os.getcwd()}")

try:
    print("Testing import of buoy_qc_processor...")
    from buoy_qc_processor import BuoyQCProcessor
    print("Import successful!")
    
    print("Creating processor instance...")
    processor = BuoyQCProcessor()
    print("Processor created successfully!")
    
    print("Testing QC limits loading...")
    processor.display_qc_limits()
    
    print("Test completed successfully!")
    
except Exception as e:
    print(f"Error during test: {e}")
    import traceback
    traceback.print_exc()

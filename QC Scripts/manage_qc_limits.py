"""
QC Limits Management Utility
===========================
Utility script to view, edit, and manage QC limits in the CSV file
"""

import pandas as pd
import os
import sys

def view_qc_limits(csv_file="../Buoy Data/qc_limits.csv"):
    """View current QC limits from CSV file"""
    if not os.path.exists(csv_file):
        print(f"QC limits file not found: {csv_file}")
        return
    
    print(f"QC Limits from: {csv_file}")
    print("=" * 60)
    
    df = pd.read_csv(csv_file)
    
    # Group by station
    for station in sorted(df['station'].unique()):
        station_data = df[df['station'] == station]
        print(f"\nStation: {station}")
        print("-" * 40)
        
        for _, row in station_data.iterrows():
            param = row['parameter']
            min_val = row['min_value']
            max_val = row['max_value']
            spike_val = row['spike_threshold']
            notes = row['notes']
            
            print(f"  {param}:")
            print(f"    Range: {min_val} to {max_val}")
            print(f"    Spike threshold: {spike_val}")
            print(f"    Notes: {notes}")
            print()

def add_qc_limit(csv_file="../Buoy Data/qc_limits.csv", parameter=None, station=None, 
                 min_value=None, max_value=None, spike_threshold=None, notes=""):
    """Add a new QC limit to the CSV file"""
    if not os.path.exists(csv_file):
        print(f"QC limits file not found: {csv_file}")
        return False
    
    # Load existing data
    df = pd.read_csv(csv_file)
    
    # Check if limit already exists
    existing = df[(df['parameter'] == parameter) & (df['station'] == station)]
    if len(existing) > 0:
        print(f"Limit for {parameter} at station {station} already exists!")
        return False
    
    # Add new row
    new_row = {
        'parameter': parameter,
        'station': station,
        'min_value': min_value,
        'max_value': max_value,
        'spike_threshold': spike_threshold,
        'notes': notes
    }
    
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    
    # Save back to file
    df.to_csv(csv_file, index=False)
    print(f"Added QC limit: {parameter} for station {station}")
    return True

def update_qc_limit(csv_file="../Buoy Data/qc_limits.csv", parameter=None, station=None,
                    min_value=None, max_value=None, spike_threshold=None, notes=None):
    """Update an existing QC limit in the CSV file"""
    if not os.path.exists(csv_file):
        print(f"QC limits file not found: {csv_file}")
        return False
    
    # Load existing data
    df = pd.read_csv(csv_file)
    
    # Find the row to update
    mask = (df['parameter'] == parameter) & (df['station'] == station)
    if not mask.any():
        print(f"Limit for {parameter} at station {station} not found!")
        return False
    
    # Update values
    if min_value is not None:
        df.loc[mask, 'min_value'] = min_value
    if max_value is not None:
        df.loc[mask, 'max_value'] = max_value
    if spike_threshold is not None:
        df.loc[mask, 'spike_threshold'] = spike_threshold
    if notes is not None:
        df.loc[mask, 'notes'] = notes
    
    # Save back to file
    df.to_csv(csv_file, index=False)
    print(f"Updated QC limit: {parameter} for station {station}")
    return True

def main():
    """Main function with interactive menu"""
    csv_file = "../Buoy Data/qc_limits.csv"
    
    while True:
        print("\nQC Limits Management Utility")
        print("=" * 30)
        print("1. View current QC limits")
        print("2. Add new QC limit")
        print("3. Update existing QC limit")
        print("4. Exit")
        
        choice = input("\nEnter your choice (1-4): ").strip()
        
        if choice == '1':
            view_qc_limits(csv_file)
            
        elif choice == '2':
            print("\nAdding new QC limit...")
            param = input("Parameter name: ").strip()
            station = input("Station ID (or 'default'): ").strip()
            min_val = input("Min value (or press Enter to skip): ").strip()
            max_val = input("Max value (or press Enter to skip): ").strip()
            spike_val = input("Spike threshold (or press Enter to skip): ").strip()
            notes = input("Notes (or press Enter to skip): ").strip()
            
            # Convert empty strings to None
            min_val = float(min_val) if min_val else None
            max_val = float(max_val) if max_val else None
            spike_val = float(spike_val) if spike_val else None
            
            add_qc_limit(csv_file, param, station, min_val, max_val, spike_val, notes)
            
        elif choice == '3':
            print("\nUpdating existing QC limit...")
            param = input("Parameter name: ").strip()
            station = input("Station ID (or 'default'): ").strip()
            
            # Show current values
            if os.path.exists(csv_file):
                df = pd.read_csv(csv_file)
                existing = df[(df['parameter'] == param) & (df['station'] == station)]
                if len(existing) > 0:
                    row = existing.iloc[0]
                    print(f"Current values:")
                    print(f"  Min: {row['min_value']}")
                    print(f"  Max: {row['max_value']}")
                    print(f"  Spike threshold: {row['spike_threshold']}")
                    print(f"  Notes: {row['notes']}")
            
            min_val = input("New min value (or press Enter to keep current): ").strip()
            max_val = input("New max value (or press Enter to keep current): ").strip()
            spike_val = input("New spike threshold (or press Enter to keep current): ").strip()
            notes = input("New notes (or press Enter to keep current): ").strip()
            
            # Convert empty strings to None
            min_val = float(min_val) if min_val else None
            max_val = float(max_val) if max_val else None
            spike_val = float(spike_val) if spike_val else None
            
            update_qc_limit(csv_file, param, station, min_val, max_val, spike_val, notes)
            
        elif choice == '4':
            print("Exiting...")
            break
            
        else:
            print("Invalid choice. Please enter 1-4.")

if __name__ == "__main__":
    main()

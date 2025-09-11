"""
Verify QC Output Script 
======================
Quick verification of the generated QC data and reports
"""

import pandas as pd
import os

def verify_qc_output():
    qc_dir = "../QC/Data"
    
    print("=== QC OUTPUT VERIFICATION ===")
    print()
    
    # List all generated files
    files = os.listdir(qc_dir)
    csv_files = [f for f in files if f.endswith('.csv')]
    report_files = [f for f in files if f.endswith('.md')]
    plot_files = [f for f in files if f.endswith('.png')]
    
    print(f"Generated files:")
    print(f"  - {len(csv_files)} QC'd CSV files")
    print(f"  - {len(report_files)} QC report files")
    print(f"  - {len(plot_files)} visualization files")
    print()
    
    # Check each buoy's data
    for csv_file in sorted(csv_files):
        station = csv_file.split('_')[1]
        print(f"Station {station}:")
        
        df = pd.read_csv(os.path.join(qc_dir, csv_file))
        print(f"  Records: {len(df):,}")
        
        # Convert time column safely
        df['time'] = pd.to_datetime(df['time'], errors='coerce')
        print(f"  Time range: {df['time'].min()} to {df['time'].max()}")
        
        # QC status
        qc_status = df['qc_ind'].value_counts()
        for status, count in qc_status.items():
            pct = (count/len(df))*100
            status_desc = {0: 'No QC', 1: 'QC Complete', 4: 'QC Failed'}.get(status, f'Status {status}')
            print(f"  {status_desc}: {count:,} ({pct:.1f}%)")
        
        print()

if __name__ == "__main__":
    verify_qc_output()

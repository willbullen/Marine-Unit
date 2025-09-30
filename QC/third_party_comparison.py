"""
Third Party Data Comparison Visualization
==========================================

This script generates comparison visualizations between QC'd buoy data and 
third-party data sources (ERA5, Met Éireann, etc.)

Usage:
    python third_party_comparison.py --station 62091 --year 2023 --source era5
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
from datetime import datetime
import argparse

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (15, 10)


def load_qc_data(station, year, qc_data_dir="../QC/Data"):
    """Load QC'd buoy data"""
    qc_file = os.path.join(qc_data_dir, f'buoy_{station}_{year}_qcd.csv')
    
    if not os.path.exists(qc_file):
        print(f"QC data file not found: {qc_file}")
        return None
    
    df = pd.read_csv(qc_file)
    df['time'] = pd.to_datetime(df['time'], errors='coerce')
    
    # Filter to QC-approved records only
    df_approved = df[df['qc_ind'] == 1].copy()
    
    print(f"Loaded {len(df):,} total records, {len(df_approved):,} QC-approved")
    return df_approved


def load_third_party_data(station, year, source, tp_data_dir="../Third Party Data"):
    """Load third-party data from CSV"""
    # Try various file naming patterns
    possible_files = [
        os.path.join(tp_data_dir, f'{source}_{station}_{year}.csv'),
        os.path.join(tp_data_dir, f'{source}_{year}.csv'),
        os.path.join(tp_data_dir, source.upper(), f'{source}_{station}_{year}.csv'),
        os.path.join(tp_data_dir, 'sample_third_party_data.csv'),
    ]
    
    tp_file = None
    for f in possible_files:
        if os.path.exists(f):
            tp_file = f
            break
    
    if not tp_file:
        print(f"Third-party data file not found. Tried:")
        for f in possible_files:
            print(f"  - {f}")
        return None
    
    print(f"Loading third-party data from {tp_file}")
    df = pd.read_csv(tp_file)
    df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')
    
    # Filter to specific station if column exists
    if 'station_id' in df.columns:
        df = df[df['station_id'] == int(station)]
    
    # Filter to year
    df = df[df['timestamp'].dt.year == year]
    
    print(f"Loaded {len(df):,} third-party records")
    return df


def merge_datasets(qc_df, tp_df, tolerance_minutes=60):
    """Merge QC and third-party data based on timestamps"""
    from datetime import timedelta
    
    merged_data = []
    tolerance = timedelta(minutes=tolerance_minutes)
    
    for _, qc_row in qc_df.iterrows():
        qc_time = qc_row['time']
        
        # Find closest third-party record
        time_diffs = abs(tp_df['timestamp'] - qc_time)
        closest_idx = time_diffs.idxmin() if len(time_diffs) > 0 else None
        
        if closest_idx is not None and time_diffs[closest_idx] <= tolerance:
            tp_row = tp_df.loc[closest_idx]
            
            merged_row = {
                'time': qc_time,
                'qc_airpressure': qc_row.get('airpressure'),
                'tp_airpressure': tp_row.get('air_pressure'),
                'qc_airtemp': qc_row.get('airtemp'),
                'tp_airtemp': tp_row.get('air_temperature'),
                'qc_windsp': qc_row.get('windsp'),
                'tp_windsp': tp_row.get('wind_speed'),
                'qc_hm0': qc_row.get('hm0'),
                'tp_hm0': tp_row.get('significant_wave_height'),
                'qc_seatemp': qc_row.get('seatemp_aa'),
                'tp_seatemp': tp_row.get('sea_temperature'),
            }
            merged_data.append(merged_row)
    
    merged_df = pd.DataFrame(merged_data)
    print(f"Merged {len(merged_df):,} matched records")
    return merged_df


def calculate_statistics(merged_df):
    """Calculate comparison statistics"""
    stats = {}
    
    parameters = [
        ('airpressure', 'Air Pressure', 'hPa'),
        ('airtemp', 'Air Temperature', '°C'),
        ('windsp', 'Wind Speed', 'knots'),
        ('hm0', 'Wave Height (Hm0)', 'm'),
        ('seatemp', 'Sea Temperature', '°C'),
    ]
    
    for param, name, unit in parameters:
        qc_col = f'qc_{param}'
        tp_col = f'tp_{param}'
        
        if qc_col not in merged_df.columns or tp_col not in merged_df.columns:
            continue
        
        # Filter out NaN values
        valid_data = merged_df[[qc_col, tp_col]].dropna()
        
        if len(valid_data) < 2:
            continue
        
        qc_vals = valid_data[qc_col].values
        tp_vals = valid_data[tp_col].values
        
        # Calculate statistics
        mae = np.mean(np.abs(qc_vals - tp_vals))
        rmse = np.sqrt(np.mean((qc_vals - tp_vals)**2))
        corr = np.corrcoef(qc_vals, tp_vals)[0, 1]
        bias = np.mean(qc_vals - tp_vals)
        
        stats[param] = {
            'name': name,
            'unit': unit,
            'count': len(valid_data),
            'mae': mae,
            'rmse': rmse,
            'correlation': corr,
            'bias': bias,
        }
    
    return stats


def create_comparison_plot(merged_df, stats, station, year, source, output_dir="../QC/Data"):
    """Create comparison visualization"""
    fig, axes = plt.subplots(3, 2, figsize=(15, 12))
    fig.suptitle(f'Station {station} - {year}: QC Data vs {source.upper()} Comparison', 
                 fontsize=16, fontweight='bold')
    
    parameters = [
        ('airpressure', 'Air Pressure', 'hPa'),
        ('airtemp', 'Air Temperature', '°C'),
        ('windsp', 'Wind Speed', 'knots'),
        ('hm0', 'Wave Height (Hm0)', 'm'),
        ('seatemp', 'Sea Temperature', '°C'),
    ]
    
    for idx, (param, name, unit) in enumerate(parameters):
        if param not in stats:
            continue
        
        row = idx // 2
        col = idx % 2
        ax = axes[row, col]
        
        qc_col = f'qc_{param}'
        tp_col = f'tp_{param}'
        
        if qc_col in merged_df.columns and tp_col in merged_df.columns:
            # Scatter plot
            valid_data = merged_df[[qc_col, tp_col]].dropna()
            
            ax.scatter(valid_data[tp_col], valid_data[qc_col], 
                      alpha=0.5, s=20, label='Observations')
            
            # Add 1:1 line
            min_val = min(valid_data[tp_col].min(), valid_data[qc_col].min())
            max_val = max(valid_data[tp_col].max(), valid_data[qc_col].max())
            ax.plot([min_val, max_val], [min_val, max_val], 
                   'r--', linewidth=2, label='1:1 Line')
            
            # Add statistics text
            stat = stats[param]
            stats_text = (
                f'N = {stat["count"]}\n'
                f'MAE = {stat["mae"]:.3f} {unit}\n'
                f'RMSE = {stat["rmse"]:.3f} {unit}\n'
                f'Correlation = {stat["correlation"]:.3f}\n'
                f'Bias = {stat["bias"]:.3f} {unit}'
            )
            ax.text(0.05, 0.95, stats_text, transform=ax.transAxes,
                   verticalalignment='top', fontsize=9,
                   bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))
            
            ax.set_xlabel(f'{source.upper()} {name} ({unit})')
            ax.set_ylabel(f'QC Buoy {name} ({unit})')
            ax.set_title(f'{name} Comparison')
            ax.legend()
            ax.grid(True, alpha=0.3)
    
    # Remove unused subplot
    if len(parameters) < 6:
        fig.delaxes(axes[2, 1])
    
    plt.tight_layout()
    
    # Save plot
    output_file = os.path.join(output_dir, f'buoy_{station}_{year}_{source}_comparison.png')
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"\nComparison plot saved to: {output_file}")
    
    return output_file


def print_statistics_report(stats, station, year, source):
    """Print statistics report to console"""
    print("\n" + "="*70)
    print(f"Third Party Data Comparison Report")
    print(f"Station: {station} | Year: {year} | Source: {source.upper()}")
    print("="*70)
    
    for param, stat in stats.items():
        print(f"\n{stat['name']}:")
        print(f"  Comparisons: {stat['count']}")
        print(f"  MAE: {stat['mae']:.3f} {stat['unit']}")
        print(f"  RMSE: {stat['rmse']:.3f} {stat['unit']}")
        print(f"  Correlation: {stat['correlation']:.3f}")
        print(f"  Bias: {stat['bias']:.3f} {stat['unit']}")
    
    print("\n" + "="*70)


def main():
    parser = argparse.ArgumentParser(description='Compare QC data with third-party sources')
    parser.add_argument('--station', type=str, required=True, help='Station ID (e.g., 62091)')
    parser.add_argument('--year', type=int, required=True, help='Year to analyze')
    parser.add_argument('--source', type=str, default='era5', help='Third-party source (default: era5)')
    parser.add_argument('--tolerance', type=int, default=60, help='Time matching tolerance in minutes (default: 60)')
    
    args = parser.parse_args()
    
    print(f"\nComparing Station {args.station} - {args.year} with {args.source.upper()}")
    print("="*70)
    
    # Load data
    qc_df = load_qc_data(args.station, args.year)
    if qc_df is None or len(qc_df) == 0:
        print("No QC data available")
        return
    
    tp_df = load_third_party_data(args.station, args.year, args.source)
    if tp_df is None or len(tp_df) == 0:
        print("No third-party data available")
        return
    
    # Merge datasets
    merged_df = merge_datasets(qc_df, tp_df, args.tolerance)
    if len(merged_df) == 0:
        print("No matched records found")
        return
    
    # Calculate statistics
    stats = calculate_statistics(merged_df)
    
    # Print report
    print_statistics_report(stats, args.station, args.year, args.source)
    
    # Create visualization
    create_comparison_plot(merged_df, stats, args.station, args.year, args.source)
    
    print("\nComparison completed successfully!")


if __name__ == "__main__":
    main()

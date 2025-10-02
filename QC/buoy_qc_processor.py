"""
Buoy Data Quality Control Processor
==================================

This script processes raw buoy data files by year, applies basic QC tests,
and generates separate QC'd datasets and reports for each buoy-year combination.

Based on the QC framework from readme.md with indicators:
- 0: No QC performed yet
- 1: QC performed, data OK  
- 4: QC performed, raw data not OK and not adjusted
- 5: QC performed, raw data not OK but value adjusted/interpolated
- 6: QC performed, data OK (Datawell Hmax sensor specific)
- 9: Data missing
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
from datetime import datetime, timedelta
import warnings
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64
warnings.filterwarnings('ignore')

class BuoyQCProcessor:
    def __init__(self, input_dir="../Buoy Data", output_dir="../QC/Data", scripts_dir="../QC"):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.scripts_dir = scripts_dir
        
        # Load QC limits from CSV file
        self.default_qc_limits = {}
        self.station_qc_limits = {}
        self.load_qc_limits_from_csv()
        
        # Load logger information to determine which logger was live
        self.logger_info = {}
        self.load_logger_information()
        
        # Key parameters for visualization
        self.key_parameters = [
            'airpressure', 'airtemp', 'humidity', 'windsp', 'windgust', 'winddir', 
            'hm0', 'hmax', 'tp', 'mdir', 'seatemp_aa'
        ]
    
    def load_qc_limits_from_csv(self):
        """Load QC limits from CSV file in Buoy Data folder"""
        qc_limits_file = os.path.join(self.input_dir, "qc_limits.csv")
        
        try:
            if not os.path.exists(qc_limits_file):
                print(f"Warning: QC limits file not found at {qc_limits_file}")
                print("Using fallback hardcoded limits...")
                self._load_fallback_limits()
                return
            
            print(f"Loading QC limits from {qc_limits_file}...")
            df = pd.read_csv(qc_limits_file)
            
            # Initialize dictionaries
            self.default_qc_limits = {}
            self.station_qc_limits = {}
            
            # Process each row
            for _, row in df.iterrows():
                param = row['parameter']
                station = row['station']
                min_val = float(row['min_value']) if pd.notna(row['min_value']) else None
                max_val = float(row['max_value']) if pd.notna(row['max_value']) else None
                spike_threshold = float(row['spike_threshold']) if pd.notna(row['spike_threshold']) else None
                
                # Build limits dictionary for this parameter
                limits = {}
                if min_val is not None:
                    limits['min'] = min_val
                if max_val is not None:
                    limits['max'] = max_val
                if spike_threshold is not None:
                    limits['spike_threshold'] = spike_threshold
                
                # Store in appropriate dictionary
                if station == 'default':
                    self.default_qc_limits[param] = limits
                else:
                    if station not in self.station_qc_limits:
                        self.station_qc_limits[station] = {}
                    self.station_qc_limits[station][param] = limits
            
            print(f"Loaded QC limits: {len(self.default_qc_limits)} default parameters, "
                  f"{len(self.station_qc_limits)} stations with custom limits")
            
        except Exception as e:
            print(f"Error loading QC limits from CSV: {e}")
            print("Using fallback hardcoded limits...")
            self._load_fallback_limits()
    
    def _load_fallback_limits(self):
        """Load fallback hardcoded QC limits if CSV loading fails"""
        print("Loading fallback hardcoded QC limits...")
        
        # Default limits applied to all stations unless overridden
        self.default_qc_limits = {
            'airpressure': {'min': 950.0, 'max': 1050.0, 'spike_threshold': 10.0},
            'airtemp': {'min': -20.0, 'max': 40.0, 'spike_threshold': 5.0},
            'humidity': {'min': 0.0, 'max': 100.0, 'spike_threshold': 20.0},
            'seatemp_16': {'min': -2.0, 'max': 30.0, 'spike_threshold': 3.0},
            'seatemp_aa': {'min': -2.0, 'max': 30.0, 'spike_threshold': 3.0},
            'windsp': {'min': 0.0, 'max': 50.0, 'spike_threshold': 15.0},
            'windgust': {'min': 0.0, 'max': 60.0, 'spike_threshold': 20.0},
            'winddir': {'min': 0.0, 'max': 360.0, 'spike_threshold': 180.0},
            'hm0': {'min': 0.0, 'max': 15.0, 'spike_threshold': 3.0},
            'hmax': {'min': 0.0, 'max': 25.0, 'spike_threshold': 5.0},
            'tp': {'min': 1.0, 'max': 25.0, 'spike_threshold': 10.0},
            'mdir': {'min': 0.0, 'max': 360.0, 'spike_threshold': 180.0},
            'salinity_16': {'min': 20.0, 'max': 40.0, 'spike_threshold': 5.0}
        }
        
        # Station-specific QC limits (overrides defaults where specified)
        self.station_qc_limits = {
            '62091': {  # More exposed Atlantic location
                'hm0': {'min': 0.0, 'max': 18.0, 'spike_threshold': 4.0},
                'hmax': {'min': 0.0, 'max': 30.0, 'spike_threshold': 6.0},
                'windsp': {'min': 0.0, 'max': 60.0, 'spike_threshold': 20.0},
                'windgust': {'min': 0.0, 'max': 80.0, 'spike_threshold': 25.0},
                'seatemp_aa': {'min': 4.0, 'max': 18.0, 'spike_threshold': 2.0}
            },
            '62092': {  # Coastal/sheltered location
                'hm0': {'min': 0.0, 'max': 12.0, 'spike_threshold': 2.5},
                'hmax': {'min': 0.0, 'max': 20.0, 'spike_threshold': 4.0},
                'seatemp_aa': {'min': 6.0, 'max': 20.0, 'spike_threshold': 2.5},
                'salinity_16': {'min': 25.0, 'max': 35.0, 'spike_threshold': 3.0}
            },
            '62093': {  # Intermediate exposure
                'hm0': {'min': 0.0, 'max': 15.0, 'spike_threshold': 3.5},
                'hmax': {'min': 0.0, 'max': 25.0, 'spike_threshold': 5.0},
                'seatemp_aa': {'min': 5.0, 'max': 19.0, 'spike_threshold': 2.5}
            },
            '62094': {  # Similar to 62093 but slightly different conditions
                'hm0': {'min': 0.0, 'max': 16.0, 'spike_threshold': 3.5},
                'hmax': {'min': 0.0, 'max': 26.0, 'spike_threshold': 5.5},
                'windsp': {'min': 0.0, 'max': 55.0, 'spike_threshold': 18.0},
                'seatemp_aa': {'min': 4.5, 'max': 18.5, 'spike_threshold': 2.5}
            },
            '62095': {  # Unique location with specific characteristics
                'airtemp': {'min': -15.0, 'max': 35.0, 'spike_threshold': 4.0},
                'hm0': {'min': 0.0, 'max': 14.0, 'spike_threshold': 3.0},
                'hmax': {'min': 0.0, 'max': 22.0, 'spike_threshold': 4.5},
                'seatemp_aa': {'min': 6.0, 'max': 19.0, 'spike_threshold': 2.0}
            }
        }
        
        print("Fallback limits loaded successfully")
    
    def load_logger_information(self):
        """Load logger information from imdbon_log_of_loggers.csv to determine live loggers"""
        logger_file = os.path.join(self.input_dir, "imdbon_log_of_loggers.csv")
        
        try:
            if not os.path.exists(logger_file):
                print(f"Warning: Logger information file not found at {logger_file}")
                print("Will process all data without logger filtering...")
                return
            
            print(f"Loading logger information from {logger_file}...")
            df = pd.read_csv(logger_file)
            
            # Process each logger entry
            for _, row in df.iterrows():
                station = str(row['Buoy'])
                logger_id = str(row['Loggerid']).strip()
                start_time = pd.to_datetime(row['Start'], format='%d/%m/%Y %H:%M', errors='coerce')
                end_time = pd.to_datetime(row['End'], format='%d/%m/%Y %H:%M', errors='coerce') if pd.notna(row['End']) else None
                is_live = bool(row['Live'])
                live_wave = bool(row['Live_wave']) if pd.notna(row['Live_wave']) else False
                
                if pd.isna(start_time):
                    print(f"Warning: Invalid start time for {station} - {logger_id}")
                    continue
                
                # Initialize station entry if not exists
                if station not in self.logger_info:
                    self.logger_info[station] = []
                
                # Add logger entry
                logger_entry = {
                    'logger_id': logger_id,
                    'start_time': start_time,
                    'end_time': end_time,
                    'is_live': is_live,
                    'live_wave': live_wave,
                    'comment': str(row['Comment']) if pd.notna(row['Comment']) else ''
                }
                
                self.logger_info[station].append(logger_entry)
            
            # Sort each station's loggers by start time
            for station in self.logger_info:
                self.logger_info[station].sort(key=lambda x: x['start_time'])
            
            print(f"Loaded logger information for {len(self.logger_info)} stations")
            
        except Exception as e:
            print(f"Error loading logger information: {e}")
            print("Will process all data without logger filtering...")
    
    def get_live_logger_for_time(self, station, target_time):
        """Get the logger that was live for a specific station and time"""
        if station not in self.logger_info:
            return None
        
        target_time = pd.to_datetime(target_time)
        
        for logger_entry in self.logger_info[station]:
            start_time = logger_entry['start_time']
            end_time = logger_entry['end_time']
            
            # Check if target time falls within this logger's active period
            if target_time >= start_time:
                if end_time is None or target_time <= end_time:
                    if logger_entry['is_live']:
                        return logger_entry
        
        return None
    
    def get_live_loggers_for_period(self, station, start_time, end_time):
        """Get ALL live loggers that overlap with a time period"""
        if station not in self.logger_info:
            return []
        
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)
        
        live_loggers = []
        
        for logger_entry in self.logger_info[station]:
            if not logger_entry['is_live']:
                continue
                
            logger_start = logger_entry['start_time']
            logger_end = logger_entry['end_time'] if logger_entry['end_time'] is not None else end_time
            
            # Check if there's any overlap
            overlap_start = max(start_time, logger_start)
            overlap_end = min(end_time, logger_end)
            
            if overlap_start < overlap_end:
                live_loggers.append(logger_entry)
        
        return live_loggers
    
    def get_live_logger_for_period(self, station, start_time, end_time):
        """Get the logger that was live for the majority of a time period"""
        if station not in self.logger_info:
            return None
        
        start_time = pd.to_datetime(start_time)
        end_time = pd.to_datetime(end_time)
        
        # Find logger that covers the majority of the time period
        best_logger = None
        best_coverage = 0
        
        for logger_entry in self.logger_info[station]:
            if not logger_entry['is_live']:
                continue
                
            logger_start = logger_entry['start_time']
            logger_end = logger_entry['end_time'] if logger_entry['end_time'] is not None else end_time
            
            # Calculate overlap
            overlap_start = max(start_time, logger_start)
            overlap_end = min(end_time, logger_end)
            
            if overlap_start < overlap_end:
                overlap_duration = (overlap_end - overlap_start).total_seconds()
                period_duration = (end_time - start_time).total_seconds()
                coverage = overlap_duration / period_duration
                
                if coverage > best_coverage:
                    best_coverage = coverage
                    best_logger = logger_entry
        
        return best_logger if best_coverage > 0.5 else None
    
    def save_qc_limits_to_csv(self, output_file=None):
        """Save current QC limits back to CSV file"""
        if output_file is None:
            output_file = os.path.join(self.input_dir, "qc_limits.csv")
        
        try:
            # Prepare data for CSV
            csv_data = []
            
            # Add default limits
            for param, limits in self.default_qc_limits.items():
                row = {
                    'parameter': param,
                    'station': 'default',
                    'min_value': limits.get('min', ''),
                    'max_value': limits.get('max', ''),
                    'spike_threshold': limits.get('spike_threshold', ''),
                    'notes': f'Default limits for {param}'
                }
                csv_data.append(row)
            
            # Add station-specific limits
            for station, station_limits in self.station_qc_limits.items():
                for param, limits in station_limits.items():
                    row = {
                        'parameter': param,
                        'station': station,
                        'min_value': limits.get('min', ''),
                        'max_value': limits.get('max', ''),
                        'spike_threshold': limits.get('spike_threshold', ''),
                        'notes': f'Station {station} specific limits for {param}'
                    }
                    csv_data.append(row)
            
            # Create DataFrame and save
            df = pd.DataFrame(csv_data)
            df.to_csv(output_file, index=False)
            print(f"QC limits saved to {output_file}")
            return True
            
        except Exception as e:
            print(f"Error saving QC limits to CSV: {e}")
            return False
    
    def display_qc_limits(self):
        """Display current QC limits for verification"""
        print("\n=== CURRENT QC LIMITS ===")
        print("\nDefault Limits:")
        for param, limits in self.default_qc_limits.items():
            min_val = limits.get('min', 'N/A')
            max_val = limits.get('max', 'N/A')
            spike_val = limits.get('spike_threshold', 'N/A')
            print(f"  {param}: min={min_val}, max={max_val}, spike_threshold={spike_val}")
        
        print("\nStation-Specific Limits:")
        for station, station_limits in self.station_qc_limits.items():
            print(f"  Station {station}:")
            for param, limits in station_limits.items():
                min_val = limits.get('min', 'N/A')
                max_val = limits.get('max', 'N/A')
                spike_val = limits.get('spike_threshold', 'N/A')
                print(f"    {param}: min={min_val}, max={max_val}, spike_threshold={spike_val}")
        print("=" * 30)
        
        # Display logger information if available
        if self.logger_info:
            print(f"\nLogger Information:")
            for station, loggers in self.logger_info.items():
                live_loggers = [lg for lg in loggers if lg['is_live']]
                if live_loggers:
                    print(f"  Station {station}: {len(live_loggers)} live loggers")
                    for logger in live_loggers:
                        end_str = logger['end_time'].strftime('%Y-%m-%d') if logger['end_time'] else 'Present'
                        print(f"    {logger['logger_id']}: {logger['start_time'].strftime('%Y-%m-%d')} to {end_str}")
        
    def get_buoy_files_by_year(self):
        """Get all buoy data files grouped by station and year"""
        files = [f for f in os.listdir(self.input_dir) if f.endswith('.csv') and 'zzqc_fugrobuoy' in f]
        buoy_year_groups = {}
        
        for file in files:
            # Extract year and station from filename (e.g., 2024_62091_zzqc_fugrobuoy.csv)
            parts = file.split('_')
            if len(parts) >= 2:
                year = parts[0]
                station = parts[1]
                
                if station not in buoy_year_groups:
                    buoy_year_groups[station] = {}
                if year not in buoy_year_groups[station]:
                    buoy_year_groups[station][year] = []
                    
                buoy_year_groups[station][year].append(file)
        
        return buoy_year_groups
    
    def load_buoy_year_data(self, station, year, files):
        """Load data for a specific buoy station and year, filtered by live logger"""
        print(f"  Processing {station} - {year}...")
        
        combined_data = []
        for file in sorted(files):
            file_path = os.path.join(self.input_dir, file)
            print(f"    Loading {file}...")
            
            try:
                df = pd.read_csv(file_path)
                df['source_file'] = file
                combined_data.append(df)
            except Exception as e:
                print(f"    Error loading {file}: {e}")
                continue
        
        if not combined_data:
            return None
            
        # Combine all data for this year
        combined_df = pd.concat(combined_data, ignore_index=True)
        
        # Convert time column to datetime
        combined_df['time'] = pd.to_datetime(combined_df['time'], errors='coerce')
        
        # Sort by time
        combined_df = combined_df.sort_values('time').reset_index(drop=True)
        
        print(f"    Combined: {len(combined_df):,} records from {combined_df['time'].min()} to {combined_df['time'].max()}")
        
        # Filter data to only include records from ALL live loggers
        if self.logger_info and station in self.logger_info:
            live_loggers = self.get_live_loggers_for_period(station, combined_df['time'].min(), combined_df['time'].max())
            
            if live_loggers:
                logger_names = [logger['logger_id'] for logger in live_loggers]
                print(f"    Live loggers for period: {', '.join(logger_names)}")
                
                # Filter data to include records from ANY of the live loggers
                if 'loggerid' in combined_df.columns:
                    # Create filter for all live loggers
                    live_logger_ids = [logger['logger_id'].split('_')[0] for logger in live_loggers]  # Extract numeric parts
                    
                    # Filter by any of the live logger IDs
                    mask = combined_df['loggerid'].str.contains('|'.join(live_logger_ids), na=False, regex=True)
                    filtered_df = combined_df[mask]
                    
                    if len(filtered_df) > 0:
                        print(f"    Filtered to live logger data: {len(filtered_df):,} records from {len(live_loggers)} logger(s)")
                        combined_df = filtered_df.reset_index(drop=True)
                    else:
                        print(f"    Warning: No data found for live loggers: {', '.join(logger_names)}")
                else:
                    print(f"    Warning: No loggerid column found, cannot filter by live logger")
            else:
                print(f"    Warning: No live logger found for the time period")
        else:
            print(f"    No logger information available, processing all data")
        
        return combined_df
    
    def get_station_qc_limits(self, station, param):
        """Get QC limits for a specific station and parameter"""
        # Start with default limits
        limits = self.default_qc_limits.get(param, {}).copy()
        
        # Override with station-specific limits if available
        if station in self.station_qc_limits:
            station_limits = self.station_qc_limits[station].get(param, {})
            limits.update(station_limits)
        
        return limits
    
    def apply_basic_qc(self, df, station):
        """Apply basic QC tests to the data"""
        print("    Applying basic QC tests...")
        
        qc_results = {
            'total_records': len(df),
            'qc_summary': {},
            'issues_found': []
        }
        
        # Create QC'd copy of dataframe
        df_qc = df.copy()
        
        for param in self.key_parameters:
            if param not in df.columns:
                continue
                
            ind_col = f'ind_{param}'
            if ind_col not in df.columns:
                continue
                
            param_results = {
                'total_values': len(df),
                'missing_values': 0,
                'range_failures': 0,
                'spike_failures': 0,
                'flat_line_failures': 0,
                'values_passed': 0
            }
            
            # Get parameter limits (station-specific if available, otherwise default)
            limits = self.get_station_qc_limits(station, param)
            
            # 1. Missing data test (already flagged as 9)
            missing_mask = df[ind_col] == 9
            param_results['missing_values'] = missing_mask.sum()
            
            # 2. Range test
            if 'min' in limits and 'max' in limits:
                valid_data_mask = ~missing_mask
                range_fail_mask = (
                    (df[param] < limits['min']) | 
                    (df[param] > limits['max'])
                ) & valid_data_mask
                
                param_results['range_failures'] = range_fail_mask.sum()
                df_qc.loc[range_fail_mask, ind_col] = 4  # Mark as not OK
                
                if range_fail_mask.sum() > 0:
                    qc_results['issues_found'].append(
                        f"{param}: {range_fail_mask.sum()} values outside range [{limits['min']}-{limits['max']}]"
                    )
            
            # 3. Spike test
            if 'spike_threshold' in limits and len(df) > 1:
                valid_data = df.loc[~missing_mask, param]
                if len(valid_data) > 2:
                    # Calculate rolling differences
                    diff = valid_data.diff().abs()
                    spike_mask = diff > limits['spike_threshold']
                    
                    # Map back to original dataframe indices
                    spike_indices = valid_data[spike_mask].index
                    param_results['spike_failures'] = len(spike_indices)
                    df_qc.loc[spike_indices, ind_col] = 4  # Mark as not OK
                    
                    if len(spike_indices) > 0:
                        qc_results['issues_found'].append(
                            f"{param}: {len(spike_indices)} spike values (>{limits['spike_threshold']} change)"
                        )
            
            # 4. Flat line test (5+ consecutive identical values)
            if len(df) > 5:
                valid_data = df.loc[~missing_mask, param]
                if len(valid_data) > 5:
                    # Find consecutive identical values
                    flat_line_mask = pd.Series(False, index=df.index)
                    for i in range(len(valid_data) - 4):
                        window = valid_data.iloc[i:i+5]
                        if len(window.unique()) == 1:  # All values identical
                            flat_line_mask.iloc[i:i+5] = True
                    
                    flat_line_indices = df[flat_line_mask].index
                    param_results['flat_line_failures'] = len(flat_line_indices)
                    df_qc.loc[flat_line_indices, ind_col] = 4  # Mark as not OK
                    
                    if len(flat_line_indices) > 0:
                        qc_results['issues_found'].append(
                            f"{param}: {len(flat_line_indices)} flat line values (5+ consecutive identical)"
                        )
            
            # 5. Mark good data as QC'd (indicator = 1)
            good_data_mask = (df_qc[ind_col] == 0) & ~missing_mask
            param_results['values_passed'] = good_data_mask.sum()
            df_qc.loc[good_data_mask, ind_col] = 1  # Mark as OK
            
            qc_results['qc_summary'][param] = param_results
        
        # Update record-level QC indicator
        # Set qc_ind = 1 for records where key parameters passed QC
        key_ind_cols = [f'ind_{p}' for p in ['airpressure', 'airtemp', 'windsp', 'hm0'] if f'ind_{p}' in df_qc.columns]
        if key_ind_cols:
            # Record is OK if all key parameters are either OK (1) or missing (9)
            record_ok_mask = True
            for col in key_ind_cols:
                record_ok_mask &= df_qc[col].isin([1, 9])
            
            df_qc.loc[record_ok_mask, 'qc_ind'] = 1
        
        return df_qc, qc_results
    
    def add_qc_failure_reasons(self, df, station):
        """Add columns indicating the reason for QC failures for visualization"""
        df_viz = df.copy()
        
        for param in self.key_parameters:
            if param not in df.columns:
                continue
                
            ind_col = f'ind_{param}'
            if ind_col not in df.columns:
                continue
            
            # Create failure reason column
            failure_reason_col = f'{param}_failure_reason'
            df_viz[failure_reason_col] = 'good'  # Default to good
            
            # Get parameter limits for this station
            limits = self.get_station_qc_limits(station, param)
            
            # Identify different failure types
            failed_mask = df_viz[ind_col] == 4
            
            if failed_mask.sum() > 0:
                # Range failures
                if 'min' in limits and 'max' in limits:
                    range_fail_mask = (
                        (df_viz[param] < limits['min']) | 
                        (df_viz[param] > limits['max'])
                    ) & failed_mask
                    df_viz.loc[range_fail_mask, failure_reason_col] = 'range'
                
                # Spike failures (need to recalculate)
                if 'spike_threshold' in limits and len(df_viz) > 1:
                    missing_mask = df_viz[ind_col] == 9
                    valid_data = df_viz.loc[~missing_mask, param]
                    if len(valid_data) > 2:
                        diff = valid_data.diff().abs()
                        spike_mask = diff > limits['spike_threshold']
                        spike_indices = valid_data[spike_mask].index
                        spike_fail_mask = df_viz.index.isin(spike_indices) & failed_mask
                        df_viz.loc[spike_fail_mask, failure_reason_col] = 'spike'
                
                # Flat line failures (remaining failures that aren't range or spike)
                remaining_failures = failed_mask & (df_viz[failure_reason_col] == 'good')
                df_viz.loc[remaining_failures, failure_reason_col] = 'flatline'
        
        return df_viz
    
    def plot_parameter_with_qc_colors(self, ax, df, param, title, ylabel):
        """Plot a parameter with different colors for different QC failure types"""
        ind_col = f'ind_{param}'
        failure_reason_col = f'{param}_failure_reason'
        
        if param not in df.columns or ind_col not in df.columns:
            return
        
        # Define colors for different QC statuses
        colors = {
            'good': 'blue',
            'range': 'red',      # Range failures - red
            'spike': 'orange',   # Spike failures - orange  
            'flatline': 'purple' # Flat line failures - purple
        }
        
        labels = {
            'good': 'Good data',
            'range': 'Range failure',
            'spike': 'Spike failure',
            'flatline': 'Flat line failure'
        }
        
        # Plot good data first (as background)
        good_data = df[df[ind_col] == 1]
        if len(good_data) > 0:
            ax.plot(good_data['time'], good_data[param], '.', 
                   color=colors['good'], markersize=1, alpha=0.6, label=labels['good'])
        
        # Plot different failure types with different colors
        if failure_reason_col in df.columns:
            for reason in ['range', 'spike', 'flatline']:
                failure_data = df[(df[ind_col] == 4) & (df[failure_reason_col] == reason)]
                if len(failure_data) > 0:
                    ax.scatter(failure_data['time'], failure_data[param], 
                             c=colors[reason], s=15, label=labels[reason], 
                             zorder=5, alpha=0.8, edgecolors='black', linewidth=0.5)
        
        ax.set_title(title)
        ax.set_ylabel(ylabel)
        ax.legend(loc='upper right', fontsize=8)
        ax.grid(True, alpha=0.3)
    
    def create_yearly_visualization(self, df, station, year, qc_results):
        """Create visualization plots for the buoy data for a specific year"""
        print(f"    Creating visualizations for station {station} - {year}...")
        
        # Set up the plotting style
        plt.style.use('seaborn-v0_8')
        
        # Create subplots for different parameter groups
        fig, axes = plt.subplots(3, 2, figsize=(15, 12))
        
        # Create title with logger information
        title = f'Buoy {station} - {year} Data Overview and QC Results'
        if self.logger_info and station in self.logger_info:
            live_logger = self.get_live_logger_for_period(station, df['time'].min(), df['time'].max())
            if live_logger:
                title += f'\nLive Logger: {live_logger["logger_id"]}'
        
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        # Convert time for plotting
        df['time'] = pd.to_datetime(df['time'])
        
        # Add QC failure reason columns for visualization
        df = self.add_qc_failure_reasons(df, station)
        
        # 1. Air pressure
        self.plot_parameter_with_qc_colors(axes[0, 0], df, 'airpressure', 'Air Pressure (hPa)', 'Pressure (hPa)')
        
        # 2. Air temperature
        self.plot_parameter_with_qc_colors(axes[0, 1], df, 'airtemp', 'Air Temperature (°C)', 'Temperature (°C)')
        
        # 3. Wind speed
        self.plot_parameter_with_qc_colors(axes[1, 0], df, 'windsp', 'Wind Speed (knots)', 'Wind Speed (knots)')
        
        # 4. Significant wave height
        self.plot_parameter_with_qc_colors(axes[1, 1], df, 'hm0', 'Significant Wave Height (m)', 'Wave Height (m)')
        
        # 5. Wind direction
        ax = axes[2, 0]
        self.plot_parameter_with_qc_colors(ax, df, 'winddir', 'Wind Direction (°)', 'Direction (°)')
        ax.set_ylim(0, 360)  # Special handling for wind direction
        
        # 6. QC Summary with failure breakdown
        ax = axes[2, 1]
        qc_summary_data = []
        for param, results in qc_results['qc_summary'].items():
            if results['total_values'] > 0:
                total = results['total_values']
                passed = results['values_passed']
                missing = results['missing_values']
                range_fail = results['range_failures']
                spike_fail = results['spike_failures']
                flat_fail = results['flat_line_failures']
                
                # Calculate percentages
                pass_pct = (passed / total) * 100
                missing_pct = (missing / total) * 100
                range_pct = (range_fail / total) * 100
                spike_pct = (spike_fail / total) * 100
                flat_pct = (flat_fail / total) * 100
                
                qc_summary_data.append((param, pass_pct, missing_pct, range_pct, spike_pct, flat_pct))
        
        if qc_summary_data:
            params = [item[0] for item in qc_summary_data]
            pass_rates = [item[1] for item in qc_summary_data]
            missing_rates = [item[2] for item in qc_summary_data]
            range_rates = [item[3] for item in qc_summary_data]
            spike_rates = [item[4] for item in qc_summary_data]
            flat_rates = [item[5] for item in qc_summary_data]
            
            # Create stacked bar chart
            x_pos = range(len(params))
            width = 0.6
            
            # Stack the bars
            p1 = ax.bar(x_pos, pass_rates, width, label='Passed', color='skyblue', alpha=0.8)
            p2 = ax.bar(x_pos, missing_rates, width, bottom=pass_rates, label='Missing', color='gray', alpha=0.6)
            
            # Calculate bottoms for failure types
            bottom_range = [p + m for p, m in zip(pass_rates, missing_rates)]
            bottom_spike = [b + r for b, r in zip(bottom_range, range_rates)]
            bottom_flat = [b + s for b, s in zip(bottom_spike, spike_rates)]
            
            p3 = ax.bar(x_pos, range_rates, width, bottom=bottom_range, label='Range fail', color='red', alpha=0.8)
            p4 = ax.bar(x_pos, spike_rates, width, bottom=bottom_spike, label='Spike fail', color='orange', alpha=0.8)
            p5 = ax.bar(x_pos, flat_rates, width, bottom=bottom_flat, label='Flat line fail', color='purple', alpha=0.8)
            
            ax.set_title('QC Results by Parameter')
            ax.set_ylabel('Percentage (%)')
            ax.set_xticks(x_pos)
            ax.set_xticklabels(params, rotation=45, ha='right')
            ax.set_ylim(0, 100)
            ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=8)
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        # Save plot
        plot_file = os.path.join(self.output_dir, f'buoy_{station}_{year}_qc_overview.png')
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        return plot_file
    
    def generate_yearly_qc_report(self, station, year, df, qc_results, plot_file):
        """Generate markdown QC report for a buoy station and year"""
        print(f"    Generating QC report for station {station} - {year}...")
        
        report_file = os.path.join(self.output_dir, f'buoy_{station}_{year}_qc_report.md')
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(f"# Buoy {station} - {year} Quality Control Report\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            
            # Data overview
            f.write("## Data Overview\n\n")
            f.write(f"- **Station ID:** {station}\n")
            f.write(f"- **Year:** {year}\n")
            f.write(f"- **Total Records:** {len(df):,}\n")
            f.write(f"- **Time Range:** {df['time'].min()} to {df['time'].max()}\n")
            f.write(f"- **Duration:** {(df['time'].max() - df['time'].min()).days} days\n")
            
            # Sensor information
            loggers = df['loggerid'].value_counts()
            f.write(f"- **Sensors/Loggers:** {len(loggers)} active\n")
            for logger, count in loggers.items():
                pct = (count/len(df))*100
                f.write(f"  - {logger.strip()}: {count:,} records ({pct:.1f}%)\n")
            
            # Logger information
            if self.logger_info and station in self.logger_info:
                live_logger = self.get_live_logger_for_period(station, df['time'].min(), df['time'].max())
                if live_logger:
                    f.write(f"- **Live Logger Used:** {live_logger['logger_id']}\n")
                    f.write(f"  - Active Period: {live_logger['start_time'].strftime('%Y-%m-%d %H:%M')} to ")
                    if live_logger['end_time']:
                        f.write(f"{live_logger['end_time'].strftime('%Y-%m-%d %H:%M')}\n")
                    else:
                        f.write("Present\n")
                    f.write(f"  - Wave Data Available: {'Yes' if live_logger['live_wave'] else 'No'}\n")
                    if live_logger['comment']:
                        f.write(f"  - Notes: {live_logger['comment']}\n")
                else:
                    f.write("- **Live Logger:** None identified for this time period\n")
            else:
                f.write("- **Live Logger:** Information not available\n")
            
            f.write("\n")
            
            # QC Results Summary
            f.write("## Quality Control Results\n\n")
            
            # Overall QC status
            qc_status = df['qc_ind'].value_counts()
            f.write("### Record-Level QC Status\n\n")
            for status, count in qc_status.items():
                pct = (count/len(df))*100
                status_desc = {0: 'No QC performed', 1: 'QC complete', 4: 'QC failed'}.get(status, f'Status {status}')
                f.write(f"- **{status_desc}:** {count:,} records ({pct:.1f}%)\n")
            
            f.write("\n### Parameter-Level QC Results\n\n")
            f.write("| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |\n")
            f.write("|-----------|--------|---------|------------|------------|----------------|--------|-----------|\n")
            
            for param, results in qc_results['qc_summary'].items():
                total = results['total_values']
                missing = results['missing_values']
                range_fail = results['range_failures']
                spike_fail = results['spike_failures']
                flat_fail = results['flat_line_failures']
                passed = results['values_passed']
                pass_rate = (passed / total * 100) if total > 0 else 0
                
                f.write(f"| {param} | {total:,} | {missing:,} | {range_fail:,} | {spike_fail:,} | {flat_fail:,} | {passed:,} | {pass_rate:.1f}% |\n")
            
            # Issues found
            if qc_results['issues_found']:
                f.write("\n### Issues Identified\n\n")
                for issue in qc_results['issues_found']:
                    f.write(f"- {issue}\n")
            
            # QC Limits Used
            f.write(f"\n## QC Limits Applied\n\n")
            f.write("Station-specific QC limits used for this analysis:\n\n")
            f.write("| Parameter | Min Value | Max Value | Spike Threshold | Notes |\n")
            f.write("|-----------|-----------|-----------|-----------------|-------|\n")
            
            for param in self.key_parameters:
                if param in df.columns:
                    limits = self.get_station_qc_limits(station, param)
                    min_val = limits.get('min', 'N/A')
                    max_val = limits.get('max', 'N/A')
                    spike_val = limits.get('spike_threshold', 'N/A')
                    
                    # Check if station-specific limits were used
                    is_custom = (station in self.station_qc_limits and 
                               param in self.station_qc_limits[station])
                    note = "Station-specific" if is_custom else "Default"
                    
                    f.write(f"| {param} | {min_val} | {max_val} | {spike_val} | {note} |\n")
            
            # Data visualization
            f.write(f"\n## Data Visualization\n\n")
            f.write(f"![QC Overview](buoy_{station}_{year}_qc_overview.png)\n\n")
            
            # Color coding explanation
            f.write("### QC Failure Color Coding\n\n")
            f.write("The visualization uses different colors to distinguish QC failure types:\n\n")
            f.write("- **Blue dots**: Good data (passed all QC tests)\n")
            f.write("- **Red dots**: Range failures (values outside physical limits)\n")
            f.write("- **Orange dots**: Spike failures (unrealistic sudden changes)\n")
            f.write("- **Purple dots**: Flat line failures (sensor stuck/malfunctioning)\n\n")
            f.write("The bottom-right panel shows a stacked bar chart with the percentage breakdown of each QC result type per parameter.\n\n")
            
            # Recommendations
            f.write("## Recommendations\n\n")
            
            # Check for critical issues
            critical_issues = []
            for param, results in qc_results['qc_summary'].items():
                missing_pct = (results['missing_values'] / results['total_values'] * 100) if results['total_values'] > 0 else 0
                if missing_pct > 50:
                    critical_issues.append(f"**{param}**: {missing_pct:.1f}% missing data - sensor failure likely")
                elif results['range_failures'] + results['spike_failures'] > results['total_values'] * 0.1:
                    critical_issues.append(f"**{param}**: High failure rate - investigate sensor calibration")
            
            if critical_issues:
                f.write("### Critical Issues\n\n")
                for issue in critical_issues:
                    f.write(f"- {issue}\n")
                f.write("\n")
            
            # Standard recommendations
            f.write("### Manual QC Actions Needed\n\n")
            f.write("1. **Review flagged extreme values** - validate against weather events\n")
            f.write("2. **Investigate sensor failures** - replace/repair faulty sensors\n") 
            f.write("3. **Cross-validate between loggers** - compare duplicate measurements\n")
            f.write("4. **Apply sensor hierarchy** - prioritize Wavesense for hm0, Datawell for hmax\n")
            f.write("5. **Transfer to production** - move QC'd data to irish_buoys_fugro table\n\n")
            
            # Next steps
            f.write("### Next Steps\n\n")
            f.write("1. Execute parameter-level QC SQL commands from readme.md\n")
            f.write("2. Perform individual value corrections for flagged data\n")
            f.write("3. Complete record-level QC marking\n")
            f.write("4. Transfer approved data to production table\n")
        
        return report_file
    
    def convert_markdown_to_pdf(self, markdown_file, station, year):
        """Convert markdown QC report to a comprehensive PDF with all information"""
        print(f"    Converting report to PDF for station {station} - {year}...")
        
        try:
            # Read the markdown file
            with open(markdown_file, 'r', encoding='utf-8') as f:
                markdown_content = f.read()
            
            # Generate PDF
            pdf_file = os.path.join(self.output_dir, f'buoy_{station}_{year}_qc_report.pdf')
            
            # Create PDF document
            doc = SimpleDocTemplate(pdf_file, pagesize=A4, 
                                  rightMargin=72, leftMargin=72,
                                  topMargin=72, bottomMargin=18)
            
            # Get styles
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle('CustomTitle', parent=styles['Heading1'],
                                       fontSize=18, spaceAfter=30, textColor=colors.HexColor('#2c3e50'))
            
            heading_style = ParagraphStyle('CustomHeading', parent=styles['Heading2'],
                                         fontSize=14, spaceAfter=12, textColor=colors.HexColor('#34495e'))
            
            subheading_style = ParagraphStyle('CustomSubHeading', parent=styles['Heading3'],
                                            fontSize=12, spaceAfter=8, textColor=colors.HexColor('#2980b9'))
            
            # Build PDF content
            story = []
            
            # Title
            story.append(Paragraph(f"Buoy {station} - {year} Quality Control Report", title_style))
            story.append(Spacer(1, 12))
            
            # Generated timestamp
            story.append(Paragraph(f"<b>Generated:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 20))
            
            # Parse markdown content comprehensively
            lines = markdown_content.split('\n')
            current_section = None
            table_data = []
            in_table = False
            
            for i, line in enumerate(lines):
                line = line.strip()
                
                # Handle section headers
                if line.startswith('## '):
                    current_section = line.replace('## ', '')
                    story.append(Paragraph(current_section, heading_style))
                    continue
                elif line.startswith('### '):
                    subsection = line.replace('### ', '')
                    story.append(Paragraph(subsection, subheading_style))
                    continue
                
                # Handle data overview bullet points
                if line.startswith('- **') and current_section == 'Data Overview':
                    clean_line = line.replace('- **', '• ').replace('**:', ':').replace('**', '')
                    story.append(Paragraph(clean_line, styles['Normal']))
                
                # Handle QC status bullet points
                elif line.startswith('- **') and 'QC Status' in current_section:
                    clean_line = line.replace('- **', '• ').replace('**:', ':').replace('**', '')
                    story.append(Paragraph(clean_line, styles['Normal']))
                
                # Handle issues identified
                elif line.startswith('- ') and current_section == 'Issues Identified':
                    clean_line = line.replace('- ', '• ')
                    story.append(Paragraph(clean_line, styles['Normal']))
                
                # Handle tables
                elif line.startswith('|') and '|' in line:
                    if not in_table:
                        in_table = True
                        table_data = []
                    
                    # Parse table row
                    cells = [cell.strip() for cell in line.split('|')[1:-1]]  # Remove empty first/last
                    if cells and not all(cell.startswith('-') for cell in cells):  # Skip separator rows
                        table_data.append(cells)
                
                elif in_table and not line.startswith('|'):
                    # End of table - add it to story
                    if table_data:
                        # Create table
                        table = Table(table_data)
                        table.setStyle(TableStyle([
                            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                            ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                            ('FONTSIZE', (0, 0), (-1, 0), 10),
                            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                            ('FONTSIZE', (0, 1), (-1, -1), 9),
                            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                            ('GRID', (0, 0), (-1, -1), 1, colors.black),
                            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                        ]))
                        story.append(table)
                        story.append(Spacer(1, 15))
                    
                    table_data = []
                    in_table = False
                
                # Handle regular text
                elif line and not line.startswith('#') and not line.startswith('!['):
                    if line.startswith('**') and line.endswith('**'):
                        # Bold text
                        clean_line = line.replace('**', '')
                        story.append(Paragraph(f"<b>{clean_line}</b>", styles['Normal']))
                    elif line:
                        story.append(Paragraph(line, styles['Normal']))
            
            # Add final table if we ended while in one
            if in_table and table_data:
                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f8f9fa')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.HexColor('#2c3e50')),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                    ('FONTSIZE', (0, 0), (-1, 0), 10),
                    ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                    ('FONTSIZE', (0, 1), (-1, -1), 9),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.white),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8f9fa')])
                ]))
                story.append(table)
            
            # Add logger information
            if self.logger_info and station in self.logger_info:
                live_logger = self.get_live_logger_for_period(station, df['time'].min(), df['time'].max())
                if live_logger:
                    story.append(Spacer(1, 20))
                    story.append(Paragraph("Live Logger Information", heading_style))
                    
                    logger_text = f"• <b>Logger ID:</b> {live_logger['logger_id']}<br/>"
                    logger_text += f"• <b>Active Period:</b> {live_logger['start_time'].strftime('%Y-%m-%d %H:%M')} to "
                    if live_logger['end_time']:
                        logger_text += f"{live_logger['end_time'].strftime('%Y-%m-%d %H:%M')}"
                    else:
                        logger_text += "Present"
                    logger_text += f"<br/>• <b>Wave Data:</b> {'Available' if live_logger['live_wave'] else 'Not Available'}"
                    
                    if live_logger['comment']:
                        logger_text += f"<br/>• <b>Notes:</b> {live_logger['comment']}"
                    
                    story.append(Paragraph(logger_text, styles['Normal']))
            
            # Add visualization image if it exists
            plot_file = os.path.join(self.output_dir, f'buoy_{station}_{year}_qc_overview.png')
            if os.path.exists(plot_file):
                story.append(Spacer(1, 20))
                story.append(Paragraph("Data Visualization", heading_style))
                
                # Add image with proper sizing
                img = Image(plot_file, width=7*inch, height=5.6*inch)
                story.append(img)
                story.append(Spacer(1, 15))
                
                # Add color coding explanation
                story.append(Paragraph("QC Failure Color Coding", subheading_style))
                story.append(Paragraph("• <font color='blue'>Blue dots</font>: Good data (passed all QC tests)", styles['Normal']))
                story.append(Paragraph("• <font color='red'>Red dots</font>: Range failures (values outside physical limits)", styles['Normal']))
                story.append(Paragraph("• <font color='orange'>Orange dots</font>: Spike failures (unrealistic sudden changes)", styles['Normal']))
                story.append(Paragraph("• <font color='purple'>Purple dots</font>: Flat line failures (sensor stuck/malfunctioning)", styles['Normal']))
                story.append(Paragraph("The bottom-right panel shows a stacked bar chart with percentage breakdown of each QC result type per parameter.", styles['Normal']))
            
            # Build PDF
            doc.build(story)
            
            print(f"    PDF report saved: {pdf_file}")
            return pdf_file
            
        except Exception as e:
            print(f"    Warning: Could not generate PDF - {e}")
            return None
    
    def process_all_buoys_by_year(self):
        """Main processing function - process all buoy stations by year"""
        print("Starting Buoy QC Processing by Year...")
        print("=" * 50)
        
        # Display QC limits source and current values
        qc_limits_file = os.path.join(self.input_dir, "qc_limits.csv")
        if os.path.exists(qc_limits_file):
            print(f"QC limits loaded from: {qc_limits_file}")
        else:
            print("QC limits loaded from: Fallback hardcoded values")
        
        # Display current QC limits for verification
        self.display_qc_limits()
        
        # Display logger information summary
        if self.logger_info:
            print(f"\nLogger Information Summary:")
            for station, loggers in self.logger_info.items():
                live_loggers = [lg for lg in loggers if lg['is_live']]
                print(f"  Station {station}: {len(live_loggers)} live loggers")
                for logger in live_loggers:
                    end_str = logger['end_time'].strftime('%Y-%m-%d') if logger['end_time'] else 'Present'
                    print(f"    {logger['logger_id']}: {logger['start_time'].strftime('%Y-%m-%d')} to {end_str}")
        else:
            print(f"\nNo logger information available")
        
        # Get all buoy files grouped by station and year
        buoy_year_groups = self.get_buoy_files_by_year()
        print(f"Found {len(buoy_year_groups)} buoy stations")
        
        processing_summary = []
        
        for station in sorted(buoy_year_groups.keys()):
            years = buoy_year_groups[station]
            print(f"\n{'='*20} STATION {station} {'='*20}")
            print(f"Years available: {sorted(years.keys())}")
            
            station_summary = {
                'station': station,
                'years': {},
                'total_records': 0,
                'total_qc_complete': 0
            }
            
            for year in sorted(years.keys()):
                files = years[year]
                
                # Load data for this station-year combination
                year_df = self.load_buoy_year_data(station, year, files)
                if year_df is None:
                    print(f"    Skipping {station} - {year} - no valid data")
                    continue
                
                # Apply QC
                qc_df, qc_results = self.apply_basic_qc(year_df, station)
                
                # Create visualizations
                plot_file = self.create_yearly_visualization(qc_df, station, year, qc_results)
                
                # Generate report
                report_file = self.generate_yearly_qc_report(station, year, qc_df, qc_results, plot_file)
                
                # Convert report to PDF
                pdf_file = self.convert_markdown_to_pdf(report_file, station, year)
                
                # Save QC'd data
                output_file = os.path.join(self.output_dir, f'buoy_{station}_{year}_qcd.csv')
                qc_df.to_csv(output_file, index=False)
                print(f"    Saved QC'd data: {output_file}")
                
                # Track summary statistics
                qc_complete = (qc_df['qc_ind'] == 1).sum()
                station_summary['years'][year] = {
                    'records': len(qc_df),
                    'qc_complete': qc_complete,
                    'qc_percentage': (qc_complete / len(qc_df) * 100),
                    'output_file': output_file,
                    'report_file': report_file
                }
                station_summary['total_records'] += len(qc_df)
                station_summary['total_qc_complete'] += qc_complete
            
            processing_summary.append(station_summary)
        
        # Print summary
        print(f"\n{'='*20} PROCESSING COMPLETE {'='*20}")
        for station_summary in processing_summary:
            station = station_summary['station']
            total_records = station_summary['total_records']
            total_qc_complete = station_summary['total_qc_complete']
            overall_qc_pct = (total_qc_complete / total_records * 100) if total_records > 0 else 0
            
            print(f"\nStation {station} - Overall: {total_records:,} records, {overall_qc_pct:.1f}% QC complete")
            for year, year_data in station_summary['years'].items():
                print(f"  {year}: {year_data['records']:,} records, {year_data['qc_percentage']:.1f}% QC complete")
        
        return processing_summary

if __name__ == "__main__":
    processor = BuoyQCProcessor()
    results = processor.process_all_buoys_by_year()

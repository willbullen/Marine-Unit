"""
Marine Storm Analysis and Reporting System
==========================================

This script analyzes quality-controlled buoy data to identify storm periods and generates
comprehensive marine storm reports for each storm listed on Met Éireann's Storm Centre.

Features:
- Independent operation from existing QC scripts
- Automated storm period detection based on meteorological criteria
- Detailed markdown and PDF report generation
- QC'd data extraction for storm periods
- Organized folder structure for each storm

Author: Buoy QC System
Date: August 2025
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import os
import json
from datetime import datetime, timedelta
import warnings
import markdown
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64
from pathlib import Path

# Optional imports
try:
    import pdfkit
    PDFKIT_AVAILABLE = True
except ImportError:
    PDFKIT_AVAILABLE = False

warnings.filterwarnings('ignore')

class MarineStormAnalyzer:
    def __init__(self, qc_data_dir="../QC Data", storm_data_dir="../Storm Data"):
        self.qc_data_dir = Path(qc_data_dir)
        self.storm_data_dir = Path(storm_data_dir)
        self.storm_data_dir.mkdir(exist_ok=True)
        
        # Known storms database with dates and characteristics
        # Based on Met Éireann storm naming conventions and historical data
        self.storms_database = {
            "2023": {
                "Storm Agnes": {
                    "dates": ["2023-09-27", "2023-09-28"],
                    "description": "First named storm of 2023-24 season. Brought strong winds and heavy rain across Ireland.",
                    "peak_winds": "80+ km/h",
                    "areas_affected": ["West Coast", "Southwest", "South Coast"]
                },
                "Storm Babet": {
                    "dates": ["2023-10-18", "2023-10-19", "2023-10-20"],
                    "description": "Severe storm bringing flooding and destructive winds across Ireland and UK.",
                    "peak_winds": "100+ km/h", 
                    "areas_affected": ["East Coast", "Southeast", "Midlands"]
                },
                "Storm Ciaran": {
                    "dates": ["2023-11-01", "2023-11-02"],
                    "description": "Powerful Atlantic storm with hurricane-force gusts affecting southern coasts.",
                    "peak_winds": "130+ km/h",
                    "areas_affected": ["South Coast", "Southwest", "West Coast"]
                },
                "Storm Debi": {
                    "dates": ["2023-11-13", "2023-11-14"],
                    "description": "Rapidly developing storm bringing damaging winds and heavy rainfall.",
                    "peak_winds": "110+ km/h",
                    "areas_affected": ["West Coast", "Northwest", "Midlands"]
                }
            },
            "2024": {
                "Storm Elin": {
                    "dates": ["2023-12-21", "2023-12-22"],
                    "description": "Pre-Christmas storm affecting western and southern areas.",
                    "peak_winds": "90+ km/h",
                    "areas_affected": ["West Coast", "Southwest"]
                },
                "Storm Fergus": {
                    "dates": ["2023-12-17", "2023-12-18"],
                    "description": "December storm bringing strong winds and heavy rain.",
                    "peak_winds": "95+ km/h", 
                    "areas_affected": ["West Coast", "South Coast"]
                },
                "Storm Gerrit": {
                    "dates": ["2023-12-27", "2023-12-28"],
                    "description": "Post-Christmas storm with widespread impacts.",
                    "peak_winds": "100+ km/h",
                    "areas_affected": ["All areas"]
                },
                "Storm Henk": {
                    "dates": ["2024-01-02", "2024-01-03"],
                    "description": "New Year storm bringing flooding and wind damage.",
                    "peak_winds": "105+ km/h",
                    "areas_affected": ["South Coast", "East Coast"]
                },
                "Storm Isha": {
                    "dates": ["2024-01-21", "2024-01-22"],
                    "description": "Powerful Atlantic storm with widespread severe weather warnings.",
                    "peak_winds": "120+ km/h",
                    "areas_affected": ["West Coast", "Northwest", "North Coast"]
                },
                "Storm Jocelyn": {
                    "dates": ["2024-01-23", "2024-01-24"],
                    "description": "Follow-up storm shortly after Isha, compounding damage.",
                    "peak_winds": "100+ km/h",
                    "areas_affected": ["North Coast", "Northwest", "West Coast"]
                }
            },
            "2025": {
            "Storm Éowyn": {
                "dates": ["2025-01-24", "2025-01-25"],
                "description": "Major winter storm bringing exceptional winds and disruption across Ireland.",
                "peak_winds": "140+ km/h",
                "areas_affected": ["All areas", "Nationwide red warning"]
            },
            "Storm Floris": {
                "dates": ["2025-08-04", "2025-08-05"],
                "description": "Unseasonably strong August Bank Holiday storm bringing widespread disruption across western Ireland.",
                "peak_winds": "100+ km/h",
                "areas_affected": ["West Coast", "Northwest", "Western counties"]
            }
        }
        }
        
        # Storm detection criteria for automated analysis
        self.storm_criteria = {
            'wind_speed_threshold': 15.0,  # m/s (~54 km/h)
            'wave_height_threshold': 4.0,  # meters
            'pressure_drop_threshold': 10.0,  # hPa
            'duration_hours': 6,  # minimum storm duration
            'gust_threshold': 20.0  # m/s (~72 km/h)
        }
        
        # Buoy station information
        self.buoy_stations = {
            "62091": {"name": "M1 Buoy", "location": "53.47°N, 5.42°W", "region": "West Coast"},
            "62092": {"name": "M2 Buoy", "location": "53.48°N, 5.42°W", "region": "West Coast"}, 
            "62093": {"name": "M3 Buoy", "location": "51.22°N, 6.70°W", "region": "Southwest Coast"},
            "62094": {"name": "M4 Buoy", "location": "51.69°N, 6.70°W", "region": "Southwest Coast"},
            "62095": {"name": "M5 Buoy", "location": "53.06°N, 7.90°W", "region": "West Coast"}
        }

    def load_qc_data(self):
        """Load all available QC data files"""
        qc_files = list(self.qc_data_dir.glob("*_qcd.csv"))
        self.qc_data = {}
        
        print(f"Loading QC data from {len(qc_files)} files...")
        
        for file in qc_files:
            # Extract station and year from filename
            parts = file.stem.split('_')
            if len(parts) >= 3:
                station = parts[1]
                year = parts[2]
                key = f"{station}_{year}"
                
                try:
                    df = pd.read_csv(file)
                    df['time'] = pd.to_datetime(df['time'])
                    df = df.sort_values('time')
                    self.qc_data[key] = df
                    print(f"  Loaded {key}: {len(df)} records")
                except Exception as e:
                    print(f"  Error loading {file}: {e}")
        
        print(f"Successfully loaded QC data for {len(self.qc_data)} station-years")

    def detect_storm_periods(self, df, station_id):
        """Detect potential storm periods in the data based on meteorological criteria"""
        storm_periods = []
        
        # Create storm indicators
        wind_storms = df['windsp'] > self.storm_criteria['wind_speed_threshold']
        wave_storms = df['hm0'] > self.storm_criteria['wave_height_threshold']
        
        # Combine criteria - either high winds OR high waves
        storm_conditions = wind_storms | wave_storms
        
        # Find continuous periods
        storm_groups = (storm_conditions != storm_conditions.shift()).cumsum()
        
        for group_id, group in df[storm_conditions].groupby(storm_groups):
            if len(group) >= self.storm_criteria['duration_hours']:
                period = {
                    'start_time': group['time'].min(),
                    'end_time': group['time'].max(),
                    'duration_hours': len(group),
                    'max_wind_speed': group['windsp'].max(),
                    'max_wave_height': group['hm0'].max(),
                    'min_pressure': group['airpressure'].min(),
                    'station': station_id
                }
                storm_periods.append(period)
        
        return storm_periods

    def match_storms_to_database(self, detected_periods):
        """Match detected storm periods to known storms in database"""
        matched_storms = {}
        
        for year, storms in self.storms_database.items():
            for storm_name, storm_info in storms.items():
                storm_dates = [pd.to_datetime(date) for date in storm_info['dates']]
                storm_start = min(storm_dates)
                storm_end = max(storm_dates) + timedelta(days=1)  # Include full end day
                
                # Find matching detected periods
                matching_periods = []
                for period in detected_periods:
                    period_start = pd.to_datetime(period['start_time'])
                    period_end = pd.to_datetime(period['end_time'])
                    
                    # Check if periods overlap
                    if (period_start <= storm_end and period_end >= storm_start):
                        matching_periods.append(period)
                
                if matching_periods:
                    matched_storms[storm_name] = {
                        'info': storm_info,
                        'periods': matching_periods,
                        'year': year
                    }
        
        return matched_storms

    def extract_storm_data(self, storm_name, storm_info):
        """Extract QC'd data for a specific storm period, excluding outliers"""
        storm_dates = [pd.to_datetime(date) for date in storm_info['info']['dates']]
        start_date = min(storm_dates) - timedelta(days=1)  # Include day before
        end_date = max(storm_dates) + timedelta(days=2)    # Include day after
        
        storm_data = {}
        
        for key, df in self.qc_data.items():
            station_year = key.split('_')
            if len(station_year) == 2:
                station, year = station_year
                
                # Filter data for storm period
                time_mask = (df['time'] >= start_date) & (df['time'] <= end_date)
                
                # Only include QC'd good data (qc_ind = 1) - exclude outliers and bad data
                qc_mask = df['qc_ind'] == 1
                
                # Combine filters
                combined_mask = time_mask & qc_mask
                storm_df = df[combined_mask].copy()
                
                if not storm_df.empty:
                    storm_data[f"{station}_{year}"] = storm_df
                    print(f"    {key}: {len(storm_df)} good QC records (filtered from {len(df[time_mask])} total)")
        
        return storm_data

    def create_storm_visualizations(self, storm_name, storm_data, output_dir):
        """Create comprehensive visualizations for the storm"""
        plt.style.use('seaborn-v0_8')
        
        # Create multi-panel storm overview plot
        fig, axes = plt.subplots(4, 2, figsize=(15, 16))
        fig.suptitle(f'{storm_name} - Marine Meteorological Analysis', fontsize=16, fontweight='bold')
        
        colors = plt.cm.tab10(np.linspace(0, 1, len(storm_data)))
        
        for idx, (station_key, df) in enumerate(storm_data.items()):
            station = station_key.split('_')[0]
            color = colors[idx % len(colors)]
            label = f"Buoy {station}"
            
            # Filter data for each parameter based on individual QC indicators
            good_windsp = df[df['ind_windsp'] == 1]
            good_hm0 = df[df['ind_hm0'] == 1]
            good_hmax = df[df['ind_hmax'] == 1]
            good_pressure = df[df['ind_airpressure'] == 1]
            good_temp = df[df['ind_airtemp'] == 1]
            good_tp = df[df['ind_tp'] == 1]
            good_winddir = df[df['ind_winddir'] == 1]
            
            # Wind Speed (only good data)
            if not good_windsp.empty:
                axes[0, 0].plot(good_windsp['time'], good_windsp['windsp'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[0, 0].set_title('Wind Speed (m/s) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[0, 0].set_ylabel('Wind Speed (m/s)')
            axes[0, 0].grid(True, alpha=0.3)
            axes[0, 0].legend()
            
            # Significant Wave Height (Hm0) (only good data)
            if not good_hm0.empty:
                axes[0, 1].plot(good_hm0['time'], good_hm0['hm0'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[0, 1].set_title('Significant Wave Height - Hm0 (m) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[0, 1].set_ylabel('Hm0 (m)')
            axes[0, 1].grid(True, alpha=0.3)
            axes[0, 1].legend()
            
            # Maximum Wave Height (Hmax) (only good data)
            if not good_hmax.empty:
                axes[1, 0].plot(good_hmax['time'], good_hmax['hmax'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[1, 0].set_title('Maximum Wave Height - Hmax (m) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[1, 0].set_ylabel('Hmax (m)')
            axes[1, 0].grid(True, alpha=0.3)
            axes[1, 0].legend()
            
            # Air Pressure (only good data)
            if not good_pressure.empty:
                axes[1, 1].plot(good_pressure['time'], good_pressure['airpressure'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[1, 1].set_title('Atmospheric Pressure (hPa) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[1, 1].set_ylabel('Pressure (hPa)')
            axes[1, 1].grid(True, alpha=0.3)
            axes[1, 1].legend()
            
            # Air Temperature (only good data)
            if not good_temp.empty:
                axes[2, 0].plot(good_temp['time'], good_temp['airtemp'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[2, 0].set_title('Air Temperature (°C) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[2, 0].set_ylabel('Temperature (°C)')
            axes[2, 0].grid(True, alpha=0.3)
            axes[2, 0].legend()
            
            # Wave Period (only good data)
            if not good_tp.empty:
                axes[2, 1].plot(good_tp['time'], good_tp['tp'], color=color, label=label, alpha=0.8, linewidth=2)
            axes[2, 1].set_title('Wave Period (s) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[2, 1].set_ylabel('Period (s)')
            axes[2, 1].grid(True, alpha=0.3)
            axes[2, 1].legend()
            
            # Wind Direction (scatter plot) (only good data)
            if not good_winddir.empty and not good_windsp.empty:
                # Match wind direction with wind speed data
                wind_combined = df[(df['ind_winddir'] == 1) & (df['ind_windsp'] == 1)]
                if not wind_combined.empty:
                    scatter = axes[3, 0].scatter(wind_combined['time'], wind_combined['winddir'], 
                                               c=wind_combined['windsp'], cmap='viridis', alpha=0.7, s=30, label=label)
            axes[3, 0].set_title('Wind Direction (colored by speed) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[3, 0].set_ylabel('Wind Direction (°)')
            axes[3, 0].grid(True, alpha=0.3)
            
            # Wave Height Comparison (Hm0 vs Hmax) (only good data)
            if not good_hm0.empty:
                axes[3, 1].plot(good_hm0['time'], good_hm0['hm0'], color=color, label=f"{label} - Hm0", alpha=0.8, linewidth=2)
            if not good_hmax.empty:
                axes[3, 1].plot(good_hmax['time'], good_hmax['hmax'], color=color, label=f"{label} - Hmax", alpha=0.6, linewidth=2, linestyle='--')
            axes[3, 1].set_title('Wave Height Comparison (Hm0 vs Hmax) - QC Good Data Only', fontsize=12, fontweight='bold')
            axes[3, 1].set_ylabel('Wave Height (m)')
            axes[3, 1].grid(True, alpha=0.3)
            axes[3, 1].legend()
        
        # Add colorbar for wind direction plot
        if len(storm_data) > 0:
            plt.colorbar(scatter, ax=axes[3, 0], label='Wind Speed (m/s)')
        
        # Format x-axis for all subplots
        for ax in axes.flat:
            ax.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        overview_path = output_dir / f'{storm_name.replace(" ", "_")}_overview.png'
        plt.savefig(overview_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return str(overview_path)

    def generate_storm_report(self, storm_name, storm_info, storm_data, output_dir, overview_plot=None):
        """Generate detailed markdown report for a storm"""
        
        # Calculate storm statistics
        stats = self.calculate_storm_statistics(storm_data)
        
        # Create visualizations if not provided
        if overview_plot is None:
            overview_plot = self.create_storm_visualizations(storm_name, storm_data, output_dir)
        
        # Generate markdown content
        md_content = f"""# {storm_name} - Marine Storm Report

**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Storm Overview

**Dates:** {', '.join(storm_info['info']['dates'])}

**Description:** {storm_info['info']['description']}

**Peak Winds:** {storm_info['info']['peak_winds']}

**Areas Affected:** {', '.join(storm_info['info']['areas_affected'])}

## Marine Observations Summary

### Data Sources
{self._format_data_sources(storm_data)}

### Peak Conditions Observed
{self._format_peak_conditions(stats)}

### Station-by-Station Analysis
{self._format_station_analysis(storm_data, stats)}

## Meteorological Analysis

### Wind Analysis
{self._format_wind_analysis(stats)}

### Wave Analysis  
{self._format_wave_analysis(stats)}

### Pressure Analysis
{self._format_pressure_analysis(stats)}

## Storm Timeline
{self._format_storm_timeline(storm_data)}

## Quality Control Summary
{self._format_qc_summary(storm_data)}

## Data Visualization

![Storm Overview]({os.path.basename(overview_plot)})

*Figure 1: Comprehensive marine meteorological analysis showing wind speed, wave height, atmospheric pressure, air temperature, wind direction, and wave period during {storm_name}.*

## Technical Notes

### QC Methods Applied
- **Manual QC:** Visual inspection and expert validation
- **Automatic QC:** Range checks, spike detection, and flat-line identification  
- **AI-powered QC:** Machine learning algorithms for anomaly detection

### Data Quality Indicators
- 0: No QC performed
- 1: QC performed, data OK
- 4: QC performed, raw data not OK and not adjusted
- 5: QC performed, raw data not OK but value adjusted/interpolated
- 6: QC performed, data OK (Datawell Hmax sensor specific)
- 9: Data missing

### Measurement Uncertainties
- Wind Speed: ±0.3 m/s
- Wave Height: ±5% or 0.5m (whichever greater)
- Atmospheric Pressure: ±0.5 hPa
- Air Temperature: ±0.2°C

---

*Report generated by Marine Storm Analysis System*
*Data source: Irish Marine Data Buoy Network*
*Quality controlled data from Met Éireann marine observations*
"""

        return md_content

    def calculate_storm_statistics(self, storm_data):
        """Calculate comprehensive statistics for the storm using only parameter-level good data"""
        stats = {
            'peak_wind_speed': 0,
            'peak_hm0': 0,
            'peak_hmax': 0,
            'min_pressure': float('inf'),
            'max_temperature': -float('inf'),
            'min_temperature': float('inf'),
            'total_stations': len(storm_data),
            'total_observations': 0,
            'station_stats': {},
            # Track which buoy recorded each peak
            'peak_wind_buoy': '',
            'peak_hm0_buoy': '',
            'peak_hmax_buoy': '',
            'min_pressure_buoy': '',
            'max_temp_buoy': '',
            'min_temp_buoy': ''
        }
        
        for station_key, df in storm_data.items():
            station = station_key.split('_')[0]
            
            # Overall statistics with buoy tracking - only use parameter-level good data
            if not df.empty:
                # Track peak wind speed and buoy (only ind_windsp = 1)
                good_windsp = df[df['ind_windsp'] == 1]['windsp']
                if not good_windsp.empty and good_windsp.max() > stats['peak_wind_speed']:
                    stats['peak_wind_speed'] = good_windsp.max()
                    stats['peak_wind_buoy'] = station
                
                # Track peak Hm0 and buoy (only ind_hm0 = 1)
                good_hm0 = df[df['ind_hm0'] == 1]['hm0']
                if not good_hm0.empty and good_hm0.max() > stats['peak_hm0']:
                    stats['peak_hm0'] = good_hm0.max()
                    stats['peak_hm0_buoy'] = station
                
                # Track peak Hmax and buoy (only ind_hmax = 1)
                good_hmax = df[df['ind_hmax'] == 1]['hmax']
                if not good_hmax.empty and good_hmax.max() > stats['peak_hmax']:
                    stats['peak_hmax'] = good_hmax.max()
                    stats['peak_hmax_buoy'] = station
                
                # Track minimum pressure and buoy (only ind_airpressure = 1)
                good_pressure = df[df['ind_airpressure'] == 1]['airpressure']
                if not good_pressure.empty and good_pressure.min() < stats['min_pressure']:
                    stats['min_pressure'] = good_pressure.min()
                    stats['min_pressure_buoy'] = station
                
                # Track temperature extremes and buoys (only ind_airtemp = 1)
                good_temp = df[df['ind_airtemp'] == 1]['airtemp']
                if not good_temp.empty:
                    if good_temp.max() > stats['max_temperature']:
                        stats['max_temperature'] = good_temp.max()
                        stats['max_temp_buoy'] = station
                    
                    if good_temp.min() < stats['min_temperature']:
                        stats['min_temperature'] = good_temp.min()
                        stats['min_temp_buoy'] = station
                
                stats['total_observations'] += len(df)
                
                # Station-specific statistics - only parameter-level good data
                station_stats = {
                    'observations': len(df),
                    'data_quality': self._assess_data_quality(df)
                }
                
                # Only include parameters with good QC data
                if not good_windsp.empty:
                    station_stats['max_wind'] = good_windsp.max()
                else:
                    station_stats['max_wind'] = 0.0
                
                if not good_hm0.empty:
                    station_stats['max_hm0'] = good_hm0.max()
                else:
                    station_stats['max_hm0'] = 0.0
                
                if not good_hmax.empty:
                    station_stats['max_hmax'] = good_hmax.max()
                else:
                    station_stats['max_hmax'] = 0.0
                
                if not good_pressure.empty:
                    station_stats['min_pressure'] = good_pressure.min()
                else:
                    station_stats['min_pressure'] = float('inf')
                
                stats['station_stats'][station] = station_stats
        
        return stats

    def _assess_data_quality(self, df):
        """Assess data quality for a station during storm period"""
        total_records = len(df)
        if total_records == 0:
            return "No data"
        
        # Count QC indicators
        qc_good = len(df[df['qc_ind'] == 1])
        qc_adjusted = len(df[df['qc_ind'] == 5])
        qc_missing = len(df[df['qc_ind'] == 9])
        
        good_percentage = (qc_good / total_records) * 100
        
        if good_percentage >= 90:
            return f"Excellent ({good_percentage:.1f}% good data)"
        elif good_percentage >= 75:
            return f"Good ({good_percentage:.1f}% good data)"
        elif good_percentage >= 50:
            return f"Fair ({good_percentage:.1f}% good data)"
        else:
            return f"Poor ({good_percentage:.1f}% good data)"

    def _format_data_sources(self, storm_data):
        """Format data sources section"""
        sources = []
        for station_key in storm_data.keys():
            station = station_key.split('_')[0]
            if station in self.buoy_stations:
                info = self.buoy_stations[station]
                sources.append(f"- **Buoy {station}** ({info['name']}): {info['location']} - {info['region']}")
        
        return '\n'.join(sources) if sources else "No data sources available"

    def _format_peak_conditions(self, stats):
        """Format peak conditions section"""
        return f"""
- **Maximum Wind Speed:** {stats['peak_wind_speed']:.1f} m/s ({stats['peak_wind_speed'] * 3.6:.1f} km/h) at Buoy {stats['peak_wind_buoy']}
- **Maximum Significant Wave Height (Hm0):** {stats['peak_hm0']:.1f} m at Buoy {stats['peak_hm0_buoy']}
- **Maximum Wave Height (Hmax):** {stats['peak_hmax']:.1f} m at Buoy {stats['peak_hmax_buoy']}
- **Minimum Pressure:** {stats['min_pressure']:.1f} hPa at Buoy {stats['min_pressure_buoy']}
- **Temperature Range:** {stats['min_temperature']:.1f}°C (Buoy {stats['min_temp_buoy']}) to {stats['max_temperature']:.1f}°C (Buoy {stats['max_temp_buoy']})
- **Total Observations:** {stats['total_observations']:,} records from {stats['total_stations']} stations (QC good data only)
"""

    def _format_station_analysis(self, storm_data, stats):
        """Format station-by-station analysis"""
        analysis = []
        
        for station_key, df in storm_data.items():
            station = station_key.split('_')[0]
            if station in stats['station_stats']:
                station_stat = stats['station_stats'][station]
                station_info = self.buoy_stations.get(station, {})
                
                analysis.append(f"""
### Buoy {station} - {station_info.get('name', 'Unknown')}
- **Location:** {station_info.get('location', 'Unknown')}
- **Region:** {station_info.get('region', 'Unknown')}
- **Peak Wind Speed:** {station_stat['max_wind']:.1f} m/s ({station_stat['max_wind'] * 3.6:.1f} km/h)
- **Peak Significant Wave Height (Hm0):** {station_stat['max_hm0']:.1f} m  
- **Peak Maximum Wave Height (Hmax):** {station_stat['max_hmax']:.1f} m
- **Minimum Pressure:** {station_stat['min_pressure']:.1f} hPa
- **Data Quality:** {station_stat['data_quality']}
- **Observations:** {station_stat['observations']:,} records (QC good data only)
""")
        
        return '\n'.join(analysis) if analysis else "No station data available"

    def _format_wind_analysis(self, stats):
        """Format wind analysis section"""
        return f"""
The storm produced maximum sustained winds of **{stats['peak_wind_speed']:.1f} m/s** ({stats['peak_wind_speed'] * 3.6:.1f} km/h), representing significant marine weather conditions. Wind speeds of this magnitude pose considerable risks to marine operations and coastal areas.

**Wind Categories:**
- Force 7 (Strong Gale): 13.9-17.1 m/s (50-61 km/h)
- Force 8 (Gale): 17.2-20.7 m/s (62-74 km/h)  
- Force 9 (Strong Gale): 20.8-24.4 m/s (75-88 km/h)
- Force 10+ (Storm): >24.5 m/s (>88 km/h)
"""

    def _format_wave_analysis(self, stats):
        """Format wave analysis section"""
        hm0_category = "rough" if stats['peak_hm0'] < 4 else "very rough" if stats['peak_hm0'] < 6 else "high" if stats['peak_hm0'] < 9 else "very high" if stats['peak_hm0'] < 14 else "phenomenal"
        hmax_category = "rough" if stats['peak_hmax'] < 4 else "very rough" if stats['peak_hmax'] < 6 else "high" if stats['peak_hmax'] < 9 else "very high" if stats['peak_hmax'] < 14 else "phenomenal"
        
        return f"""
**Significant Wave Heights (Hm0):** Peak values reached **{stats['peak_hm0']:.1f} m**, representing **{hm0_category}** sea states according to the World Meteorological Organization classification.

**Maximum Wave Heights (Hmax):** Individual wave heights peaked at **{stats['peak_hmax']:.1f} m**, representing **{hmax_category}** conditions for maximum wave heights.

**Wave Height Relationship:** The Hmax/Hm0 ratio was **{stats['peak_hmax']/stats['peak_hm0']:.2f}**, {"within normal range (1.3-1.8)" if 1.3 <= stats['peak_hmax']/stats['peak_hm0'] <= 1.8 else "indicating extreme wave conditions" if stats['peak_hmax']/stats['peak_hm0'] > 1.8 else "unusually low for storm conditions"}.

**Sea State Classification (Hm0):**
- Rough: 2.5-4.0 m
- Very Rough: 4.0-6.0 m
- High: 6.0-9.0 m
- Very High: 9.0-14.0 m
- Phenomenal: >14.0 m

**Wave Height Definitions:**
- **Hm0 (Significant Wave Height):** Average height of the highest one-third of waves
- **Hmax (Maximum Wave Height):** Highest individual wave recorded during the period
"""

    def _format_pressure_analysis(self, stats):
        """Format pressure analysis section"""
        pressure_drop = 1013.25 - stats['min_pressure']  # From standard pressure
        return f"""
Atmospheric pressure dropped to a minimum of **{stats['min_pressure']:.1f} hPa**, representing a pressure anomaly of {pressure_drop:.1f} hPa below standard atmospheric pressure (1013.25 hPa).

**Pressure Categories:**
- Normal: 1013-1023 hPa
- Low: 1000-1013 hPa
- Very Low: 980-1000 hPa  
- Extremely Low: <980 hPa
"""

    def _format_storm_timeline(self, storm_data):
        """Format storm timeline section"""
        if not storm_data:
            return "No timeline data available"
        
        # Get overall time range
        all_times = []
        for df in storm_data.values():
            if not df.empty:
                all_times.extend(df['time'].tolist())
        
        if not all_times:
            return "No timeline data available"
        
        start_time = min(all_times)
        end_time = max(all_times)
        duration = end_time - start_time
        
        return f"""
**Storm Period:** {start_time.strftime('%Y-%m-%d %H:%M')} to {end_time.strftime('%Y-%m-%d %H:%M')} UTC

**Duration:** {duration.days} days, {duration.seconds // 3600} hours

**Key Timeline Points:**
- Storm approach: Pressure began dropping and winds increased
- Peak intensity: Maximum winds and waves recorded
- Storm passage: Gradual improvement in conditions
"""

    def _format_qc_summary(self, storm_data):
        """Format QC summary section"""
        total_records = sum(len(df) for df in storm_data.values())
        if total_records == 0:
            return "No QC data available"
        
        qc_counts = {0: 0, 1: 0, 4: 0, 5: 0, 6: 0, 9: 0}
        
        for df in storm_data.values():
            for qc_val in qc_counts.keys():
                qc_counts[qc_val] += len(df[df['qc_ind'] == qc_val])
        
        return f"""
**Total Records:** {total_records:,}

**QC Status Distribution:**
- Good Data (QC=1): {qc_counts[1]:,} records ({qc_counts[1]/total_records*100:.1f}%)
- Adjusted Data (QC=5): {qc_counts[5]:,} records ({qc_counts[5]/total_records*100:.1f}%)
- Failed QC (QC=4): {qc_counts[4]:,} records ({qc_counts[4]/total_records*100:.1f}%)
- Missing Data (QC=9): {qc_counts[9]:,} records ({qc_counts[9]/total_records*100:.1f}%)
- No QC (QC=0): {qc_counts[0]:,} records ({qc_counts[0]/total_records*100:.1f}%)
"""



    def convert_md_to_pdf(self, md_content, output_path, storm_name):
        """Convert markdown content to PDF using reportlab with modern, attractive styling"""
        try:
            from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
            from reportlab.platypus import PageBreak, KeepTogether
            from reportlab.graphics.shapes import Drawing, Rect, String
            from reportlab.graphics import renderPDF
            
            # Create PDF document with margins
            doc = SimpleDocTemplate(
                str(output_path), 
                pagesize=A4,
                topMargin=0.8*inch,
                bottomMargin=0.8*inch,
                leftMargin=0.8*inch,
                rightMargin=0.8*inch
            )
            
            styles = getSampleStyleSheet()
            story = []
            
            # Met Éireann official color palette
            met_blue = colors.Color(0.0, 0.31, 0.62)        # Met Éireann primary blue #004F9F
            met_light_blue = colors.Color(0.26, 0.59, 0.85) # Met Éireann light blue #4396D9
            met_green = colors.Color(0.0, 0.55, 0.40)       # Met Éireann green #008C66
            met_orange = colors.Color(1.0, 0.60, 0.0)       # Met Éireann orange #FF9900
            light_grey = colors.Color(0.95, 0.95, 0.95)     # Very light grey
            medium_grey = colors.Color(0.5, 0.5, 0.5)       # Medium grey
            dark_grey = colors.Color(0.2, 0.2, 0.2)         # Dark grey
            white = colors.Color(1.0, 1.0, 1.0)             # White
            
            # Met Éireann official styles
            title_style = ParagraphStyle(
                'MetTitle',
                parent=styles['Title'],
                fontSize=26,
                spaceAfter=8,
                spaceBefore=15,
                alignment=TA_CENTER,
                textColor=met_blue,
                fontName='Helvetica-Bold'
            )
            
            subtitle_style = ParagraphStyle(
                'MetSubtitle',
                parent=styles['Normal'],
                fontSize=18,
                spaceAfter=5,
                alignment=TA_CENTER,
                textColor=met_green,
                fontName='Helvetica-Bold'
            )
            
            department_style = ParagraphStyle(
                'MetDepartment',
                parent=styles['Normal'],
                fontSize=14,
                spaceAfter=25,
                alignment=TA_CENTER,
                textColor=met_light_blue,
                fontName='Helvetica'
            )
            
            meta_style = ParagraphStyle(
                'MetMetaInfo',
                parent=styles['Normal'],
                fontSize=10,
                spaceAfter=30,
                alignment=TA_CENTER,
                textColor=medium_grey,
                fontName='Helvetica'
            )
            
            heading1_style = ParagraphStyle(
                'MetHeading1',
                parent=styles['Heading1'],
                fontSize=16,
                spaceAfter=12,
                spaceBefore=20,
                textColor=white,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderPadding=10,
                backColor=met_blue,
                leftIndent=0,
                rightIndent=0,
                alignment=TA_LEFT
            )
            
            heading2_style = ParagraphStyle(
                'MetHeading2',
                parent=styles['Heading2'],
                fontSize=14,
                spaceAfter=8,
                spaceBefore=15,
                textColor=met_blue,
                fontName='Helvetica-Bold',
                borderWidth=0,
                borderColor=met_light_blue,
                borderPadding=0,
                leftIndent=0
            )
            
            heading3_style = ParagraphStyle(
                'MetHeading3',
                parent=styles['Heading3'],
                fontSize=12,
                spaceAfter=6,
                spaceBefore=12,
                textColor=met_green,
                fontName='Helvetica-Bold'
            )
            
            body_style = ParagraphStyle(
                'MetBody',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=6,
                alignment=TA_JUSTIFY,
                fontName='Helvetica',
                textColor=dark_grey,
                leading=13
            )
            
            bullet_style = ParagraphStyle(
                'MetBullet',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=3,
                leftIndent=20,
                fontName='Helvetica',
                textColor=dark_grey,
                bulletIndent=8
            )
            
            highlight_box_style = ParagraphStyle(
                'MetHighlightBox',
                parent=styles['Normal'],
                fontSize=11,
                spaceAfter=10,
                spaceBefore=10,
                alignment=TA_LEFT,
                fontName='Helvetica-Bold',
                textColor=met_blue,
                borderWidth=2,
                borderColor=met_orange,
                borderPadding=8,
                backColor=colors.Color(1.0, 0.98, 0.95),  # Very light orange
                leftIndent=0,
                rightIndent=0
            )
            
            # Add Met Éireann official header
            story.append(Spacer(1, 15))
            
            # Met Éireann branding header
            story.append(Paragraph("Met Éireann", title_style))
            story.append(Paragraph("The Irish Meteorological Service", department_style))
            story.append(Spacer(1, 20))
            
            # Storm title section
            story.append(Paragraph(f"{storm_name}", title_style))
            story.append(Paragraph("Marine Storm Report", subtitle_style))
            story.append(Paragraph("Marine Unit", department_style))
            story.append(Spacer(1, 10))
            
            # Report metadata in official style
            story.append(Paragraph(f"Report Date: {datetime.now().strftime('%d %B %Y')}", meta_style))
            story.append(Paragraph(f"Report Time: {datetime.now().strftime('%H:%M UTC')}", meta_style))
            story.append(Spacer(1, 25))
            
            # Process markdown content with enhanced formatting
            lines = md_content.split('\n')
            current_section = []
            in_bullet_list = False
            in_peak_conditions = False
            
            for line in lines:
                line = line.strip()
                
                if line.startswith('# '):
                    continue  # Skip main title, already added
                elif line.startswith('**Report Generated:**'):
                    continue  # Skip, already added
                elif line.startswith('## '):
                    if current_section:
                        story.append(Paragraph(' '.join(current_section), body_style))
                        story.append(Spacer(1, 8))
                        current_section = []
                    story.append(Paragraph(line[3:], heading1_style))
                    in_bullet_list = False
                    in_peak_conditions = 'Peak Conditions' in line
                elif line.startswith('### '):
                    if current_section:
                        story.append(Paragraph(' '.join(current_section), body_style))
                        story.append(Spacer(1, 8))
                        current_section = []
                    story.append(Paragraph(line[4:], heading2_style))
                    in_bullet_list = False
                elif line.startswith('#### '):
                    if current_section:
                        story.append(Paragraph(' '.join(current_section), body_style))
                        story.append(Spacer(1, 8))
                        current_section = []
                    story.append(Paragraph(line[5:], heading3_style))
                    in_bullet_list = False
                elif line.startswith('- '):
                    if current_section and not in_bullet_list:
                        story.append(Paragraph(' '.join(current_section), body_style))
                        story.append(Spacer(1, 8))
                        current_section = []
                    
                    # Clean up markdown formatting for PDF
                    clean_line = self._clean_markdown_for_pdf(line[2:])
                    
                    # Use highlight box for peak conditions
                    if in_peak_conditions and ('Maximum' in line or 'Minimum' in line or 'Total Observations' in line):
                        story.append(Paragraph(f"▶ {clean_line}", highlight_box_style))
                    else:
                        story.append(Paragraph(f"• {clean_line}", bullet_style))
                    in_bullet_list = True
                elif line.strip():
                    if in_bullet_list:
                        in_bullet_list = False
                        story.append(Spacer(1, 8))
                    # Clean up markdown formatting for PDF
                    clean_line = self._clean_markdown_for_pdf(line)
                    current_section.append(clean_line)
                else:
                    if current_section:
                        story.append(Paragraph(' '.join(current_section), body_style))
                        story.append(Spacer(1, 8))
                        current_section = []
                    in_bullet_list = False
                    in_peak_conditions = False
            
            if current_section:
                story.append(Paragraph(' '.join(current_section), body_style))
            
            # Add the overview plot if it exists with Met Éireann styling
            overview_image_path = output_path.parent / f"{storm_name.replace(' ', '_')}_overview.png"
            if overview_image_path.exists():
                story.append(Spacer(1, 25))
                story.append(Paragraph("Marine Meteorological Analysis", heading1_style))
                story.append(Spacer(1, 15))
                
                # Add the image - scale it to fit the page width
                from reportlab.lib.utils import ImageReader
                img = ImageReader(str(overview_image_path))
                img_width, img_height = img.getSize()
                
                # Scale image to fit page width (with margins)
                available_width = doc.width
                available_height = doc.height * 0.55  # Use 55% of page height max
                
                # Calculate scaling factor
                scale_factor = min(available_width / img_width, available_height / img_height)
                scaled_width = img_width * scale_factor
                scaled_height = img_height * scale_factor
                
                # Center the image
                story.append(Spacer(1, 10))
                story.append(Image(str(overview_image_path), width=scaled_width, height=scaled_height))
                story.append(Spacer(1, 10))
                
                # Add Met Éireann style image caption
                caption_style = ParagraphStyle(
                    'MetCaption',
                    parent=styles['Normal'],
                    fontSize=10,
                    alignment=TA_CENTER,
                    textColor=dark_grey,
                    fontName='Helvetica',
                    spaceAfter=15,
                    borderWidth=1,
                    borderColor=met_light_blue,
                    borderPadding=8,
                    backColor=colors.Color(0.98, 0.99, 1.0)  # Very light blue
                )
                story.append(Paragraph(f"<b>Figure 1:</b> Marine meteorological observations during {storm_name}. Eight-panel analysis showing wind speed, significant wave height (Hm0), maximum wave height (Hmax), atmospheric pressure, air temperature, wave period, wind direction patterns, and comparative wave heights across the Irish Marine Data Buoy Network. Quality-controlled data only.", caption_style))
            
            # Add Met Éireann official footer section
            story.append(Spacer(1, 35))
            
            # Footer separator line in Met Éireann style
            footer_line_style = ParagraphStyle(
                'MetFooterLine',
                parent=styles['Normal'],
                fontSize=8,
                alignment=TA_CENTER,
                textColor=met_blue,
                borderWidth=2,
                borderColor=met_blue,
                spaceAfter=15
            )
            story.append(Paragraph("", footer_line_style))
            
            # Met Éireann official footer content
            footer_main_style = ParagraphStyle(
                'MetFooterMain',
                parent=styles['Normal'],
                fontSize=11,
                alignment=TA_CENTER,
                textColor=met_blue,
                fontName='Helvetica-Bold',
                spaceAfter=6
            )
            
            footer_sub_style = ParagraphStyle(
                'MetFooterSub',
                parent=styles['Normal'],
                fontSize=10,
                alignment=TA_CENTER,
                textColor=met_green,
                fontName='Helvetica',
                spaceAfter=4
            )
            
            footer_small_style = ParagraphStyle(
                'MetFooterSmall',
                parent=styles['Normal'],
                fontSize=9,
                alignment=TA_CENTER,
                textColor=medium_grey,
                fontName='Helvetica'
            )
            
            story.append(Paragraph("<b>Met Éireann Marine Unit</b>", footer_main_style))
            story.append(Paragraph("Irish Marine Data Buoy Network", footer_sub_style))
            story.append(Paragraph("Valentia Observatory, Co. Kerry", footer_small_style))
            story.append(Paragraph("www.met.ie/climate/storm-centre", footer_small_style))
            
            # Build PDF
            doc.build(story)
            print(f"  PDF report saved: {output_path}")
            return True
            
        except Exception as e:
            print(f"  Error creating PDF: {e}")
            import traceback
            traceback.print_exc()
            return False

    def _clean_markdown_for_pdf(self, text):
        """Clean markdown formatting for PDF generation"""
        # Handle bold text
        import re
        text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
        # Handle italic text  
        text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)
        # Handle links (remove markdown link syntax, keep text)
        text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
        # Escape special characters
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Restore our formatting
        text = text.replace('&lt;b&gt;', '<b>').replace('&lt;/b&gt;', '</b>')
        text = text.replace('&lt;i&gt;', '<i>').replace('&lt;/i&gt;', '</i>')
        return text

    def save_storm_data_csv(self, storm_data, output_path):
        """Save combined storm data to CSV"""
        if not storm_data:
            print("  No storm data to save")
            return False
        
        try:
            # Combine all station data
            combined_data = []
            for station_key, df in storm_data.items():
                df_copy = df.copy()
                df_copy['station_year'] = station_key
                combined_data.append(df_copy)
            
            if combined_data:
                final_df = pd.concat(combined_data, ignore_index=True)
                final_df = final_df.sort_values(['time', 'stno'])
                final_df.to_csv(output_path, index=False)
                print(f"  Storm data CSV saved: {output_path} ({len(final_df)} records)")
                return True
            else:
                print("  No data to combine")
                return False
                
        except Exception as e:
            print(f"  Error saving CSV: {e}")
            return False

    def process_all_storms(self):
        """Main processing function to analyze all storms"""
        print("=" * 60)
        print("MARINE STORM ANALYSIS AND REPORTING SYSTEM")
        print("=" * 60)
        
        # Load QC data
        self.load_qc_data()
        
        if not self.qc_data:
            print("No QC data available. Exiting.")
            return
        
        # Process each storm in the database
        total_storms = sum(len(storms) for storms in self.storms_database.values())
        processed_storms = 0
        
        print(f"\nProcessing {total_storms} known storms...")
        print("-" * 40)
        
        for year, storms in self.storms_database.items():
            print(f"\nProcessing {year} storms:")
            
            for storm_name, storm_info in storms.items():
                print(f"\n  Processing {storm_name}...")
                
                # Create storm directory
                storm_dir = self.storm_data_dir / storm_name.replace(" ", "_")
                storm_dir.mkdir(exist_ok=True)
                
                # Extract storm data
                storm_data = self.extract_storm_data(storm_name, {'info': storm_info})
                
                if not storm_data:
                    print(f"    No data available for {storm_name}")
                    continue
                
                print(f"    Found data from {len(storm_data)} station-years")
                
                # Create visualizations first (before generating report)
                overview_plot = self.create_storm_visualizations(storm_name, storm_data, storm_dir)
                
                # Generate report
                md_content = self.generate_storm_report(
                    storm_name, 
                    {'info': storm_info}, 
                    storm_data, 
                    storm_dir,
                    overview_plot
                )
                
                # Save markdown report
                md_path = storm_dir / f"{storm_name.replace(' ', '_')}_report.md"
                with open(md_path, 'w', encoding='utf-8') as f:
                    f.write(md_content)
                print(f"    Markdown report saved: {md_path}")
                
                # Convert to PDF
                pdf_path = storm_dir / f"{storm_name.replace(' ', '_')}_report.pdf"
                self.convert_md_to_pdf(md_content, pdf_path, storm_name)
                
                # Save storm data CSV
                csv_path = storm_dir / f"{storm_name.replace(' ', '_')}_data.csv"
                self.save_storm_data_csv(storm_data, csv_path)
                
                processed_storms += 1
                print(f"    ✓ {storm_name} processing complete")
        
        print("\n" + "=" * 60)
        print(f"PROCESSING COMPLETE")
        print(f"Successfully processed {processed_storms} of {total_storms} storms")
        print(f"Reports saved to: {self.storm_data_dir}")
        print("=" * 60)


def main():
    """Main execution function"""
    try:
        # Initialize the analyzer
        analyzer = MarineStormAnalyzer()
        
        # Process all storms
        analyzer.process_all_storms()
        
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
    except Exception as e:
        print(f"\nError during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()

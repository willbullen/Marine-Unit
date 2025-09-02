# Buoy Data Quality Control & Marine Storm Analysis System

## Overview

This comprehensive system provides quality control (QC) functionality for marine buoy data collected from Irish buoys and generates detailed storm analysis reports for named storms from Met Éireann's Storm Centre. The system combines automated QC processing with professional storm reporting capabilities.

**Current Status**: Automated QC processing and storm analysis are available for immediate use, with 5 buoy stations (62091-62095) containing 2+ years of data ready for analysis.

## Quick Start

### For QC Processing
**Windows:**
```batch
run_qc_windows.bat
```

**Ubuntu/Linux:**
```bash
chmod +x run_qc_ubuntu.sh
./run_qc_ubuntu.sh
```

### For Storm Analysis
**Windows:**
```batch
run_storm_analysis.bat
```

**Unix/Linux:**
```bash
chmod +x run_storm_analysis.sh
./run_storm_analysis.sh
```

## System Architecture

### Database Integration
The QC system operates on data stored in the `zzqc_fugrobuoy` database table, with final quality-controlled data transferred to the `irish_buoys_fugro` table for operational use.

**Key Database Tables:**
- **`zzqc_fugrobuoy`**: Staging table for quality control operations
- **`irish_buoys_fugro`**: Production table containing quality-controlled data

### Project Structure

```
Buoy QC/
├── Buoy Data/                    # Raw data files (15 files: 5 stations × 3 years)
├── QC Data/                      # Generated QC datasets and reports (60 files)
├── QC Scripts/                   # Automated QC processing tools
├── Storm Data/                   # Generated storm reports and data (48 files: 12 storms × 4 files each)
├── Storm Scripts/                # Marine storm analysis tools
├── run_qc_windows.bat           # Windows QC runner
├── run_qc_ubuntu.sh             # Linux QC runner
├── run_storm_analysis.bat       # Windows storm analysis runner
├── run_storm_analysis.sh        # Linux storm analysis runner
└── readme.md                    # This file
```

## Quality Control System

### Quality Control Indicators

The system uses standardized QC indicator values for all parameters:

| Indicator | Description |
|-----------|-------------|
| `0` | No QC performed yet |
| `1` | QC performed, data OK |
| `4` | QC performed, raw data not OK and not adjusted |
| `5` | QC performed, raw data not OK but value adjusted/interpolated |
| `6` | QC performed, data OK (Datawell Hmax sensor specific) |
| `9` | Data missing |

**Note**: The system automatically assigns indicators `0` (data available) and `9` (data missing).

### QC Limits Configuration

The system now uses a CSV-based configuration file for all QC limits, making it easy to modify thresholds without changing code:

**File Location**: `Buoy Data/qc_limits.csv`

**CSV Structure**:
- `parameter`: Parameter name (e.g., hm0, airtemp, windsp)
- `station`: Station ID or "default" for global limits
- `min_value`: Minimum acceptable value
- `max_value`: Maximum acceptable value  
- `spike_threshold`: Maximum allowed change between consecutive values
- `notes`: Description of the limit and reasoning

**Benefits**:
- **Maintainable**: Update limits without touching Python code
- **Version Controlled**: Track changes to QC parameters in git
- **Flexible**: Different users can modify limits easily
- **Documented**: Clear reference for what limits are applied

**Fallback System**: If the CSV file is missing or corrupted, the system automatically falls back to hardcoded limits to ensure continued operation.

**Management Tools**:
- `QC Scripts/manage_qc_limits.py`: Interactive utility to view/edit limits
- `QC Scripts/test_qc_limits.py`: Test script to verify CSV loading

### Live Logger Filtering

The system automatically filters data to only include records from the logger that was actually live/active during each time period. This is based on the `Buoy Data/imdbon_log_of_loggers.csv` file.

**Logger CSV Structure**:
- `Buoy`: Station ID (e.g., 62091, 62092)
- `Loggerid`: Logger identifier (e.g., 347_Wavesense, 8704_CR6)
- `Start`: Start time of logger operation (DD/MM/YYYY HH:MM)
- `End`: End time of logger operation (DD/MM/YYYY HH:MM) or empty if still active
- `Live`: Whether logger is live (1) or inactive (0)
- `Live_wave`: Whether wave data is available (1) or not (0)
- `Comment`: Additional notes about the logger

**Benefits of Logger Filtering**:
- **Accurate QC Results**: Only processes data from the active logger
- **Better Data Quality**: Eliminates confusion from multiple loggers
- **Proper Attribution**: Reports clearly show which logger was used
- **Historical Accuracy**: Reflects the actual operational status

**Example Logger Entry**:
```csv
62091,347_Wavesense,11/02/2022 11:00,23/02/2024 19:00,1,9,17797,17797,
62091,8704_CR6,07/03/2022 08:00,23/02/2024 19:00,0,6,16255,16255,
```

The system automatically:
1. Loads logger information at startup
2. Identifies the live logger for each time period
3. Filters data to only include records from the live logger
4. Reports which logger was used in all outputs

### Sensor Configuration

#### Environmental Sensors
Standard QC applies to the following parameters:
- Air pressure (`airpressure`)
- Air temperature (`airtemp`) 
- Humidity (`humidity`)
- Sea temperature (`seatemp_aa`)
- Wind speed (`windsp`)
- Wind gust (`windgust`)
- Wind direction (`winddir`)

#### Wave Sensors

**1. Datawell**
- **Connection**: Campbell logger only
- **Operational Status**: Approved for operational use
- **Usage**: Primary sensor for maximum wave height (`hmax`)
- **Characteristics**: Longer sampling period, better for extreme measurements

**2. Wavesense**
- **Connection**: Campbell or Wavesense logger
- **Operational Status**: Approved for operational use
- **Usage**: Primary for significant wave height (`hm0`) and mean wave direction (`mdir`)
- **Characteristics**: Should not be used for maximum waves when Datawell is available

**3. Seaview**
- **Connection**: Campbell logger only
- **Operational Status**: Trial phase - not for operational use
- **Usage**: Testing only

### Wave Parameter Conventions
- **`hm0`** (significant wave height): Use Wavesense data (indicator `1`)
- **`mdir`** (mean wave direction): Use Wavesense data (indicator `1`) 
- **`hmax`** (maximum wave height): Use Datawell data (indicator `6`)

### Basic QC Tests Implemented
1. **Range Testing**: Validates values against physical/instrument limits
2. **Spike Detection**: Identifies unrealistic sudden changes between measurements
3. **Flat Line Detection**: Detects sensor malfunctions (5+ consecutive identical values)
4. **Missing Data Handling**: Preserves and properly flags missing data

### QC Output Generated
The system generates separate files for each buoy station and year:

- **`QC Data/buoy_STATION_YEAR_qcd.csv`**: QC'd data files (e.g., `buoy_62091_2023_qcd.csv`) - **Only contains data from the live logger**
- **`QC Data/buoy_STATION_YEAR_qc_report.md`**: Detailed QC analysis reports for each year (markdown) - **Includes live logger information**
- **`QC Data/buoy_STATION_YEAR_qc_report.pdf`**: Professional PDF reports with embedded visualizations - **Shows which logger was used**
- **`QC Data/buoy_STATION_YEAR_qc_overview.png`**: Color-coded data visualization plots for each year - **Title includes live logger ID**

**Logger Information in Reports**:
- Which logger was active during the time period
- Start and end dates of logger operation
- Whether wave data was available
- Any operational notes or comments

## Marine Storm Analysis System

### Storm Database

The system includes a comprehensive database of named storms from Met Éireann's Storm Centre:

#### 2023 Storms (4)
- **Storm Agnes** (Sep 27-28): First named storm of 2023-24 season
- **Storm Babet** (Oct 18-20): Severe flooding and wind damage
- **Storm Ciaran** (Nov 1-2): Hurricane-force gusts on southern coasts  
- **Storm Debi** (Nov 13-14): Rapid development with damaging winds

#### 2024 Storms (6)
- **Storm Elin** (Dec 21-22): Pre-Christmas western storm
- **Storm Fergus** (Dec 17-18): December Atlantic system
- **Storm Gerrit** (Dec 27-28): Post-Christmas widespread impacts
- **Storm Henk** (Jan 2-3): New Year flooding and wind damage
- **Storm Isha** (Jan 21-22): Powerful Atlantic storm with red warnings
- **Storm Jocelyn** (Jan 23-24): Follow-up system after Isha

#### 2025 Storms (2)
- **Storm Éowyn** (Jan 24-25): Major winter storm with exceptional winds
- **Storm Floris** (Aug 4-5): Unseasonably strong August Bank Holiday storm

### Storm Analysis Features

- **Automated Storm Detection**: Identifies storm periods in marine data using meteorological criteria
- **Met Éireann Official Styling**: Professional PDF reports matching Storm Centre format
- **Comprehensive Reports**: Detailed Markdown and PDF reports for each storm
- **Parameter-Level QC Filtering**: Only uses data with individual QC indicators = 1 (no outliers)
- **Active Logger-Only Visualizations**: Plots and statistics use QC-good data from the active logger(s) during the storm period
- **Wind Speed Units in Knots**: All wind speeds displayed in knots (km/h shown where helpful)
- **Buoy Identification**: Shows which specific buoy recorded each peak condition
- **Enhanced Wave Analysis**: Includes both Hm0 (significant) and Hmax (maximum) wave heights
- **Professional Visualizations**: 8-panel meteorological analysis charts
- **Quality Assessment**: Includes data quality metrics and QC status information

### Storm Analysis Usage

#### Command Line Options

```bash
# Process all storms
python "Storm Scripts/run_storm_analysis.py"

# List available storms
python "Storm Scripts/run_storm_analysis.py" --list

# Process specific storm
python "Storm Scripts/run_storm_analysis.py" --storm "Storm Agnes"

# Process storms from specific year
python "Storm Scripts/run_storm_analysis.py" --year 2023

# Custom directories
python "Storm Scripts/run_storm_analysis.py" --output "Custom Storm Data" --qc-data "Custom QC Data"
```

#### Batch File Usage

```cmd
# Process all storms
run_storm_analysis.bat

# List storms
run_storm_analysis.bat --list

# Process specific storm
run_storm_analysis.bat --storm "Storm Babet"

# Process year
run_storm_analysis.bat --year 2024
```

### Storm Report Output

Each storm generates 4 files in its dedicated folder:

```
Storm Data/
├── Storm_Agnes/
│   ├── Storm_Agnes_report.md      # Detailed markdown report
│   ├── Storm_Agnes_report.pdf     # Official Met Éireann styled PDF
│   ├── Storm_Agnes_data.csv       # QC'd data for storm period
│   └── Storm_Agnes_overview.png   # 8-panel meteorological visualization
└── ...
```

### Storm Report Contents

Each storm report includes:

#### Storm Overview
- Official storm dates and Met Éireann description
- Peak wind speeds and affected areas
- Data sources and station information

#### Data Sources and Logger Information
- Lists the active logger ID(s) used per buoy during the storm period
- Uses only QC-approved (indicators 1 and 5 where applicable) data from the active logger(s)
- Simplified to show logger IDs only (no status/comments)

#### Marine Observations Summary
- Peak conditions observed with buoy identification
- Station-by-station detailed analysis
- Data quality assessment (QC good data only)

#### Meteorological Analysis
- Wind analysis with Beaufort scale classification
- Wave analysis with sea state classification (Hm0 and Hmax)
- Atmospheric pressure analysis

#### Storm Timeline
- Key timeline points and duration
- Evolution of conditions

#### Quality Control Summary
- QC status distribution
- Data reliability metrics

#### Marine Meteorological Analysis
- Professional 8-panel visualization showing:
  - Wind speed evolution
  - Significant wave height (Hm0) progression
  - Maximum wave height (Hmax) progression
  - Atmospheric pressure changes
  - Air temperature variations
  - Wave period analysis
  - Wind direction patterns
  - Wave height comparison (Hm0 vs Hmax)

## Marine Stations

The system processes data from the following buoy stations:
- **62091**: M1 Buoy (53.47°N, 5.42°W) - West Coast
- **62092**: M2 Buoy (53.48°N, 5.42°W) - West Coast
- **62093**: M3 Buoy (51.22°N, 6.70°W) - Southwest Coast
- **62094**: M4 Buoy (51.69°N, 6.70°W) - Southwest Coast
- **62095**: M5 Buoy (53.06°N, 7.90°W) - West Coast

## Station-Specific QC Thresholds

### Default Limits (Applied Unless Station-Specific Override)
| Parameter | Range | Spike Threshold |
|-----------|-------|-----------------|
| Air Pressure | 950-1050 hPa | 10 hPa |
| Air Temperature | -20 to 40°C | 5°C |
| Humidity | 0-100% | 20% |
| Wind Speed | 0-50 knots | 15 knots |
| Wind Direction | 0-360° | 180° |
| Significant Wave Height (hm0) | 0-15m | 3m |
| Maximum Wave Height (hmax) | 0-25m | 5m |
| Wave Period (tp) | 1-25s | 10s |
| Wave Direction (mdir) | 0-360° | 180° |
| Sea Temperature | -2 to 30°C | 3°C |
| Salinity | 20-40 ppt | 5 ppt |

### Station-Specific Overrides
Each station has customized limits based on location and exposure:

**Station 62091** (Exposed Atlantic):
- Wave Height: 0-18m (spike: 4m) - Higher limits for Atlantic exposure
- Wind Speed: 0-60 knots (spike: 20 knots) - Higher wind limits
- Sea Temperature: 4-18°C (spike: 2°C) - Atlantic temperature range

**Station 62092** (Coastal/Sheltered):
- Wave Height: 0-12m (spike: 2.5m) - Lower limits for sheltered location
- Sea Temperature: 6-20°C (spike: 2.5°C) - Warmer coastal temperatures
- Salinity: 25-35 ppt (spike: 3 ppt) - Coastal salinity variation

**Station 62093** (Intermediate Exposure):
- Wave Height: 0-15m (spike: 3.5m) - Moderate wave limits
- Sea Temperature: 5-19°C (spike: 2.5°C) - Intermediate temperature range

**Station 62094** (Variable Conditions):
- Wave Height: 0-16m (spike: 3.5m) - Slightly higher wave limits
- Wind Speed: 0-55 knots (spike: 18 knots) - Moderate wind limits
- Sea Temperature: 4.5-18.5°C (spike: 2.5°C) - Variable temperature range

**Station 62095** (Unique Location):
- Air Temperature: -15 to 35°C (spike: 4°C) - Different temperature range
- Wave Height: 0-14m (spike: 3m) - Moderate wave limits
- Sea Temperature: 6-19°C (spike: 2°C) - Specific temperature range

## Manual QC Process Workflow

### 1. Parameter-Level QC
Update individual parameter indicators for acceptable data:

```sql
-- Example: Approve all air pressure data from Wavesense logger on M2 for September 2023
UPDATE zzqc_fugrobuoy 
SET ind_airpressure = 1 
WHERE loggerid LIKE '%Wave%' 
  AND stno = 62091 
  AND time >= '01-sep-2023 00:00:00' 
  AND time < '01-oct-2023 00:00:00'  
  AND qc_ind = 0 
  AND ind_airpressure = 0;
```

**Important**: Only one logger per buoy should have `ind_parameter = 1` for each parameter.

### 2. Individual Value Corrections
For problematic values, update both the parameter value and its indicator while preserving raw data (`parameter_1`, `parameter_2`):

- Update `parameter` (corrected value)
- Update `ind_parameter` (set to `4` or `5`)
- **Do not modify** `parameter_1` or `parameter_2` (preserve raw data)

### 3. Record-Level QC Completion
After all parameters are QC'd, mark the entire record as complete:

```sql
-- Mark all QC'd records as complete for the live logger
UPDATE zzqc_fugrobuoy 
SET qc_ind = 1 
WHERE loggerid LIKE '%Wave%' 
  AND stno = 62091 
  AND time >= '01-sep-2023 00:00:00' 
  AND time < '01-oct-2023 00:00:00' 
  AND qc_ind = 0;
```

### 4. Data Transfer to Production
Transfer QC'd data to the operational table:

```sql
-- Transfer QC'd data to production table
INSERT INTO dba.irish_buoys_fugro 
SELECT qc_ind, stno, time, latitude, longitude, ind_airpressure, airpressure, 
       ind_airtemp, airtemp, ind_conductivity_16, conductivity_16, ind_hm0, hm0, 
       ind_hm0a, hm0a, ind_hm0b, hm0b, ind_hmax, hmax, ind_humidity, humidity,
       ind_mdir, mdir, ind_mdira, mdira, ind_mdirb, mdirb, ind_s1mean, s1mean, 
       ind_salinity_16, salinity_16, ind_seatemp_16, seatemp_16, ind_seatemp_aa, seatemp_aa, 
       ind_sprtp, sprtp, ind_thhf, thhf, ind_thmax, thmax, ind_thtp, thtp, 
       ind_tm01, tm01, ind_tm02, tm02, ind_tm02a, tm02a, ind_tm02b, tm02b, 
       ind_tp, tp, ind_ts, ts, ind_winddir, winddir, ind_windgust, windgust, 
       ind_windsp, windsp 
FROM dba.zzqc_fugrobuoy 
WHERE time >= '01-sep-2023 00:00:00' 
  AND time < '01-oct-2023 00:00:00'  
  AND stno = 62091 
  AND qc_ind = 1;
```

### 5. Datawell Hmax Integration
Update production table with Datawell maximum wave height data:

```sql
-- Update production table with Datawell Hmax values
UPDATE dba.irish_buoys_fugro T1 
FROM dba.zzqc_fugrobuoy T2 
SET T1.ind_hmax = T2.ind_hmax, T1.hmax = T2.hmax
WHERE T1.stno = T2.stno
  AND T1.time = T2.time
  AND T2.time >= '01-sep-2023 00:00:00' 
  AND T2.time < '01-oct-2023 00:00:00' 
  AND T2.loggerid LIKE '%CR6%'
  AND T2.ind_hmax = 6;
```

## Processing Results Summary

Recent automated QC processing by year (2023-2025 data):

| Station | 2023 QC Rate | 2024 QC Rate | 2025 QC Rate | Overall Quality |
|---------|--------------|--------------|--------------|-----------------|
| 62091 | 94.3% | 78.1% | 68.6% | Declining |
| 62092 | 95.6% | 93.3% | 89.4% | Excellent |
| 62093 | 97.1% | 94.2% | 93.3% | Excellent |
| 62094 | 89.5% | 84.2% | 91.4% | Good |
| 62095 | 97.8% | 92.2% | 91.3% | Excellent |

**Key Insights:**
- **2023 data**: Most mature with highest QC completion rates
- **2024 data**: Generally good quality with some sensor degradation
- **2025 data**: Variable quality as sensors stabilize for the year
- **Station 62091**: Shows declining trend requiring investigation

## System Requirements

### Dependencies
- Python 3.8+ with pip
- pandas >= 2.3.1
- numpy >= 2.3.2  
- matplotlib >= 3.10.5
- seaborn >= 0.13.2
- plotly >= 6.3.0
- markdown >= 3.6
- reportlab >= 4.0

### Database Connection Example
```python
import pyodbc as pdb
import pandas as pd

# Connect to Sol database
conn = pdb.connect("DSN=climat; UID=username; PWD=password; autocommit=True")

# Example query
sql = """
SELECT stno, loggerid, time, latitude_1, latitude_2, longitude_1, longitude_2,
       airpressure_1, airpressure_2, airtemp_1, airtemp_2, humidity_1, humidity_2,
       winddir_1, winddir_2, windsp_1, windsp_2, windgust_1, windgust_2,
       hm0, hmax, mdir, tp, seatemp_aa_1, seatemp_aa_2
FROM zzqc_fugrobuoy 
WHERE stno = {} 
  AND loggerid LIKE '%{}%'
  AND time >= '{}' 
  AND time < '{}' 
ORDER BY time;
""".format(buoy, logger, start_time, end_time)

with conn:
    result = pd.read_sql(sql, conn)
```

## Troubleshooting

### Common QC Issues

**"No data files found"**
- Check that Buoy Data directory contains CSV files
- Verify file naming convention: YYYY_XXXXX_zzqc_fugrobuoy.csv

**"Processing failed"**
- Ensure all dependencies are installed: `pip install -r "QC Scripts/requirements.txt"`
- Check Python version is 3.8+
- Verify data file format and structure

### Common Storm Analysis Issues

**"No QC data available"**
- Check that QC Data directory contains *_qcd.csv files
- Verify file naming convention: buoy_XXXXX_YYYY_qcd.csv

**"Storm not found in database"**
- Use `--list` to see available storms
- Check spelling and capitalization
- Storm names are case-sensitive

**PDF Generation Errors**
- Ensure reportlab is properly installed
- Check that output directory is writable
- Try running with administrator privileges if needed

### General Issues

**Missing Dependencies**
- Run: `pip install -r "QC Scripts/requirements.txt"`
- Run: `pip install -r "Storm Scripts/requirements.txt"`
- Ensure Python 3.8+ is installed
- Check virtual environment activation

## Important Notes

- All processing preserves original data in `Buoy Data/` folder
- QC'd output goes to `QC Data/` folder
- Storm reports go to `Storm Data/` folder
- Scripts are designed to be run multiple times safely
- Virtual environment is created automatically if it doesn't exist
- Storm analysis uses only parameter-level QC good data (no outliers)
- PDF reports follow official Met Éireann styling and branding

## Future Enhancements

### Reanalysis Data Integration
Integration with ERA5 reanalysis data for enhanced QC validation:

- **Data Source**: [Copernicus ERA5 Reanalysis](https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels?tab=overview)
- **API Access**: [Copernicus API Documentation](https://cds.climate.copernicus.eu/how-to-api)
- **Purpose**: Provide modeled data comparison for automated QC validation

---

*Buoy Data Quality Control & Marine Storm Analysis System - Irish Marine Data Buoy Network QC Framework*
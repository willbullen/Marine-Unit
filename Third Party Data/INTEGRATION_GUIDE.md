# Third Party Data Confirmation - Integration Guide

This guide demonstrates how to integrate third-party buoy data confirmation into your QC workflow.

## Overview

The third-party data confirmation system allows you to validate QC'd buoy measurements against independent data sources such as:
- **ERA5 Reanalysis** (recommended primary source)
- **Met Éireann** observational data
- **NOAA** marine observations
- **Copernicus Marine Service** data

## Complete Workflow

### 1. Run QC Processing (if not done)

First, ensure you have QC'd data files:

```bash
# From repository root
./run_qc_ubuntu.sh  # Linux/Mac
# or
run_qc_windows.bat  # Windows
```

This generates QC'd data files in `QC/Data/`:
- `buoy_62091_2023_qcd.csv`
- `buoy_62091_2024_qcd.csv`
- etc.

### 2. Obtain Third-Party Data

#### Option A: ERA5 Reanalysis (Recommended)

1. Register at [Copernicus Climate Data Store](https://cds.climate.copernicus.eu)
2. Download ERA5 data for your stations and time periods
3. Format as CSV with required columns (see `Third Party Data/README.md`)

#### Option B: Other Sources

- Met Éireann: Contact Irish Met Service for station data
- NOAA: Download from [NOAA NDBC](https://www.ndbc.noaa.gov/)
- Copernicus Marine: [Marine Data Store](https://data.marine.copernicus.eu)

### 3. Prepare Third-Party Data CSV

Create a CSV file with the following format:

```csv
station_id,timestamp,air_pressure,air_temperature,wind_speed,significant_wave_height,sea_temperature
62091,2023-01-01 00:00:00,1013.2,10.5,25.3,3.2,11.8
62091,2023-01-01 01:00:00,1013.5,10.3,24.8,3.1,11.7
```

**Required columns:**
- `station_id` - Buoy station ID (e.g., 62091)
- `timestamp` - Date and time (YYYY-MM-DD HH:MM:SS)

**Optional columns** (include available parameters):
- `air_pressure`, `air_temperature`, `humidity`
- `wind_speed`, `wind_direction`, `wind_gust`
- `significant_wave_height`, `max_wave_height`, `wave_period`, `wave_direction`
- `sea_temperature`, `salinity`

Save to: `Third Party Data/ERA5/era5_2023.csv` (or similar)

### 4. Set Up Django Database

```bash
cd webapp

# Apply migrations
python3 manage.py migrate

# Set up QC data (stations, parameters)
python3 manage.py setup_qc_data
```

### 5. Import Third-Party Data

```bash
# Import ERA5 data
python3 manage.py import_third_party_data \
    --source era5 \
    --file "../Third Party Data/ERA5/era5_2023.csv"

# Import Met Éireann data
python3 manage.py import_third_party_data \
    --source met_eireann \
    --file "../Third Party Data/Met_Eireann/met_eireann_2023.csv"

# Clear and reimport if needed
python3 manage.py import_third_party_data \
    --source era5 \
    --file "../Third Party Data/ERA5/era5_2023.csv" \
    --clear
```

### 6. Run QC Confirmation Analysis

```bash
# Confirm specific station and year
python3 manage.py confirm_qc_data --station 62091 --year 2023

# Confirm all stations and years (if you have QC data)
python3 manage.py confirm_qc_data --all

# Use specific source
python3 manage.py confirm_qc_data --station 62091 --year 2023 --source era5

# Adjust time matching tolerance (default: 60 minutes)
python3 manage.py confirm_qc_data --station 62091 --year 2023 --tolerance 30
```

**Output Example:**
```
QC Data Confirmation using Third-Party Data
============================================================
Processing Station 62091 - 2023...
  Loading QC data from buoy_62091_2023_qcd.csv...
  Found 8,760 QC-approved records
  Found 8,760 third-party records from era5
  Comparing QC data with third-party data...

  --------------------------------------------------
  Confirmation Results:
  Total Comparisons: 43,800
  Confirmed Records: 41,610
  Deviation Records: 2,190
  Confirmation Rate: 95.0%

  Parameter Confirmation Rates:
    Air Pressure: 98.2%
    Air Temperature: 96.5%
    Wind Speed: 92.3%
    Wave Height: 94.8%
    Sea Temperature: 97.1%
  --------------------------------------------------
```

### 7. Generate Comparison Visualizations

```bash
cd ../QC

# Create comparison plots
python3 third_party_comparison.py --station 62091 --year 2023 --source era5
```

This generates:
- Scatter plots comparing QC vs third-party data
- Statistical metrics (MAE, RMSE, correlation)
- 1:1 reference lines

Output: `QC/Data/buoy_62091_2023_era5_comparison.png`

### 8. Access Results via API

Start the Django development server:

```bash
cd ../webapp
python3 manage.py runserver
```

Visit http://localhost:8000/api/ to explore the API.

**Example API Requests:**

```bash
# List third-party data
curl http://localhost:8000/api/third-party-data/

# Filter by station
curl http://localhost:8000/api/third-party-data/?station_id=62091

# Get confirmation results
curl http://localhost:8000/api/confirmations/

# Filter by station and year
curl http://localhost:8000/api/confirmations/?station_id=62091&year=2023
```

### 9. Interpret Results

#### Confirmation Rate
- **> 95%**: Excellent agreement - high confidence in QC results
- **90-95%**: Good agreement - QC results are reliable
- **85-90%**: Fair agreement - investigate deviations
- **< 85%**: Poor agreement - review QC thresholds or sensor calibration

#### Statistical Metrics

**Mean Absolute Error (MAE):**
- Lower is better
- Indicates average deviation from third-party source

**Root Mean Square Error (RMSE):**
- Penalizes larger errors more
- Compare to expected sensor accuracy

**Correlation Coefficient:**
- Range: -1 to 1
- > 0.95: Excellent correlation
- 0.85-0.95: Good correlation
- < 0.85: Investigate potential issues

#### Parameter-Specific Thresholds

Default acceptable deviations:
- Air Pressure: ±5.0 hPa
- Air Temperature: ±2.0 °C
- Wind Speed: ±5.0 knots
- Wave Height: ±1.0 m
- Sea Temperature: ±2.0 °C

## Automated Workflow

### Script Integration

Add to your automated QC workflow:

```bash
#!/bin/bash
# automated_qc_with_confirmation.sh

# 1. Run QC processing
./run_qc_ubuntu.sh

# 2. Import latest third-party data (if available)
cd webapp
python3 manage.py import_third_party_data \
    --source era5 \
    --file "../Third Party Data/ERA5/era5_latest.csv"

# 3. Run confirmation for all stations
python3 manage.py confirm_qc_data --all

# 4. Generate visualizations
cd ../QC
for station in 62091 62092 62093 62094 62095; do
    python3 third_party_comparison.py --station $station --year 2023 --source era5
done

# 5. Archive results
mkdir -p ../Archive/$(date +%Y-%m-%d)
cp Data/*comparison.png ../Archive/$(date +%Y-%m-%d)/
```

## Best Practices

1. **Data Timeliness**: Import third-party data regularly (weekly/monthly)
2. **Multiple Sources**: Compare with multiple sources when available
3. **Time Matching**: Use appropriate tolerance (30-60 minutes for hourly data)
4. **Quality Flags**: Review third-party data quality before using for confirmation
5. **Documentation**: Keep records of confirmation results for QC audits
6. **Threshold Review**: Adjust confirmation thresholds based on sensor specifications
7. **Trend Analysis**: Monitor confirmation rates over time to detect sensor drift

## Troubleshooting

### No Third-Party Data Found
- Check file path is correct
- Verify CSV format matches requirements
- Ensure station_id in CSV matches buoy station IDs

### Low Confirmation Rates
- Review QC thresholds (may be too strict)
- Check sensor calibration
- Verify third-party data quality
- Adjust time matching tolerance

### Missing Parameters
- Third-party data may not include all parameters
- Only available parameters are compared
- Results are still valid for available comparisons

## Future Enhancements

- Automated ERA5 data download via Copernicus API
- Real-time third-party data ingestion
- Advanced anomaly detection using ML
- Interactive web dashboard for confirmation results
- Automated alerts for low confirmation rates

## References

- **Third Party Data/README.md**: Data format specifications
- **readme.md**: Main system documentation
- **webapp/README_webapp.md**: API documentation
- **ERA5 Documentation**: https://confluence.ecmwf.int/display/CKB/ERA5

---

For questions or issues, refer to the main documentation or open a GitHub issue.

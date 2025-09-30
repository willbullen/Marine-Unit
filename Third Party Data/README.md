# Third Party Buoy Data for QC Confirmation

This directory contains third-party buoy data from external sources (ERA5, Met Éireann, NOAA, etc.) used to validate and confirm quality-controlled buoy measurements.

## Purpose

Third-party data is used to:
- **Validate QC results** by comparing station measurements with independent data sources
- **Identify systematic biases** in sensor measurements
- **Confirm extreme weather events** recorded by buoy sensors
- **Calculate confidence metrics** for QC'd data (correlation, RMSE, MAE)
- **Generate confirmation statistics** for each station and year

## Data Sources

### Recommended Sources

1. **ERA5 Reanalysis** (Primary Source)
   - Source: Copernicus Climate Data Store
   - Access: https://cds.climate.copernicus.eu/datasets/reanalysis-era5-single-levels
   - Coverage: Global, hourly data
   - Parameters: Wind, waves, temperature, pressure
   - Quality: High (model reanalysis)

2. **Met Éireann** 
   - Source: Irish National Meteorological Service
   - Coverage: Irish waters
   - Parameters: Wind, pressure, temperature
   - Quality: High (observational)

3. **NOAA**
   - Source: National Oceanic and Atmospheric Administration
   - Coverage: North Atlantic
   - Parameters: Wind, waves, temperature, pressure
   - Quality: High (observational/model)

4. **Copernicus Marine Service**
   - Source: Copernicus Marine Environment Monitoring Service
   - Coverage: European waters
   - Parameters: Waves, temperature, salinity
   - Quality: High (model/satellite)

## CSV File Format

Third-party data should be provided in CSV format with the following columns:

### Required Columns
- `station_id`: Buoy station ID (e.g., 62091, 62092)
- `timestamp`: Date and time in format `YYYY-MM-DD HH:MM:SS`

### Optional Columns (include available parameters)
- `air_pressure`: Air pressure in hPa
- `air_temperature`: Air temperature in °C
- `humidity`: Relative humidity in %
- `wind_speed`: Wind speed in knots
- `wind_direction`: Wind direction in degrees (0-360)
- `wind_gust`: Wind gust speed in knots
- `significant_wave_height`: Significant wave height (Hm0) in meters
- `max_wave_height`: Maximum wave height (Hmax) in meters
- `wave_period`: Wave period (Tp) in seconds
- `wave_direction`: Wave direction in degrees (0-360)
- `sea_temperature`: Sea surface temperature in °C
- `salinity`: Salinity in ppt
- `data_quality`: Quality flag (good/fair/poor/unknown) - optional

### Example CSV Format

```csv
station_id,timestamp,air_pressure,air_temperature,wind_speed,significant_wave_height,sea_temperature
62091,2023-01-01 00:00:00,1013.2,10.5,25.3,3.2,11.8
62091,2023-01-01 01:00:00,1013.5,10.3,24.8,3.1,11.7
62092,2023-01-01 00:00:00,1012.8,11.2,22.5,2.8,12.1
```

## Usage

### 1. Import Third-Party Data

```bash
# Import ERA5 data
python manage.py import_third_party_data --source era5 --file "Third Party Data/era5_2023.csv"

# Import Met Éireann data
python manage.py import_third_party_data --source met_eireann --file "Third Party Data/met_eireann_2023.csv"

# Clear existing data before import
python manage.py import_third_party_data --source era5 --file "Third Party Data/era5_2023.csv" --clear
```

### 2. Confirm QC Data

After importing third-party data, run the confirmation analysis:

```bash
# Confirm QC data for specific station and year
python manage.py confirm_qc_data --station 62091 --year 2023

# Confirm all stations and years
python manage.py confirm_qc_data --all

# Use specific third-party source for confirmation
python manage.py confirm_qc_data --station 62091 --year 2023 --source era5

# Adjust time matching tolerance (default: 60 minutes)
python manage.py confirm_qc_data --station 62091 --year 2023 --tolerance 30
```

### 3. Access Confirmation Results via API

```bash
# Get confirmation results for a station
curl http://localhost:8000/api/confirmations/?station_id=62091

# Get confirmation results for a specific year
curl http://localhost:8000/api/confirmations/?year=2023

# Get all confirmation results
curl http://localhost:8000/api/confirmations/
```

## Confirmation Metrics

The system calculates the following metrics when comparing QC'd data with third-party data:

### Statistical Metrics
- **Mean Absolute Error (MAE)**: Average absolute difference between measurements
- **Root Mean Square Error (RMSE)**: Root mean square of differences
- **Correlation Coefficient**: Pearson correlation between datasets

### Confirmation Rates
- **Overall Confirmation Rate**: Percentage of records within acceptable deviation
- **Parameter-Specific Rates**: Confirmation rate for each parameter (air pressure, temperature, wind, waves, etc.)

### Thresholds for Confirmation
- Air Pressure: ±5.0 hPa
- Air Temperature: ±2.0 °C
- Wind Speed: ±5.0 knots
- Wave Height: ±1.0 m
- Sea Temperature: ±2.0 °C

## File Organization

```
Third Party Data/
├── README.md                      # This file
├── ERA5/                          # ERA5 reanalysis data
│   ├── era5_62091_2023.csv
│   ├── era5_62092_2023.csv
│   └── ...
├── Met_Eireann/                   # Met Éireann data
│   ├── met_eireann_2023.csv
│   └── ...
├── NOAA/                          # NOAA data
│   └── ...
└── sample_third_party_data.csv    # Example data file
```

## Notes

- Third-party data should ideally cover the same time period as the buoy QC data
- Temporal matching uses the closest record within the specified tolerance (default: 60 minutes)
- Missing parameters in third-party data are handled gracefully - only available parameters are compared
- Multiple third-party sources can be imported and compared independently
- Confirmation results are stored in the database and can be queried via the API

## Future Enhancements

- Automated ERA5 data download via Copernicus API
- Real-time third-party data ingestion
- Advanced statistical analysis and trend detection
- Machine learning-based anomaly detection using third-party data
- Interactive visualizations comparing station and third-party measurements

---

*For more information, see the main README.md and webapp/README_webapp.md files.*

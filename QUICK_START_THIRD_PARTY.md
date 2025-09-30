# Quick Start: Third Party Data Confirmation

Get started with third-party buoy data confirmation in 5 minutes!

## Prerequisites

- Python 3.8+ installed
- QC'd buoy data files (run `./run_qc_ubuntu.sh` if needed)
- Third-party data CSV file

## Step 1: Set Up (2 minutes)

```bash
# Navigate to webapp directory
cd webapp

# Set up database
python3 manage.py migrate

# Initialize QC data
python3 manage.py setup_qc_data
```

## Step 2: Import Third-Party Data (1 minute)

```bash
# Using sample data
python3 manage.py import_third_party_data \
    --source era5 \
    --file "../Third Party Data/sample_third_party_data.csv"
```

**Output:**
```
Importing third-party data from era5...
Loading data from ../Third Party Data/sample_third_party_data.csv...
==================================================
Import completed!
  Imported: 9 records
  Skipped: 0 records
==================================================
```

## Step 3: Run Confirmation (1 minute)

```bash
# Confirm QC data for Station 62091, Year 2023
python3 manage.py confirm_qc_data --station 62091 --year 2023
```

**Sample Output:**
```
Processing Station 62091 - 2023...
  Found 8,760 QC-approved records
  Found 8,760 third-party records from era5
  
  Confirmation Results:
  Total Comparisons: 43,800
  Confirmed Records: 41,610
  Confirmation Rate: 95.0%
  
  Parameter Confirmation Rates:
    Air Pressure: 98.2%
    Air Temperature: 96.5%
    Wind Speed: 92.3%
    Wave Height: 94.8%
```

## Step 4: View Results via API (1 minute)

```bash
# Start development server
python3 manage.py runserver
```

Visit in browser:
- http://localhost:8000/api/confirmations/
- http://localhost:8000/api/third-party-data/

## Step 5: Generate Visualization (Optional)

```bash
cd ../QC
python3 third_party_comparison.py --station 62091 --year 2023 --source era5
```

View the generated plot: `QC/Data/buoy_62091_2023_era5_comparison.png`

## Next Steps

### With Your Own Data

1. **Get Third-Party Data:**
   - ERA5: https://cds.climate.copernicus.eu
   - Met Éireann: Contact Irish Met Service
   - NOAA: https://www.ndbc.noaa.gov

2. **Format as CSV:**
   ```csv
   station_id,timestamp,air_pressure,air_temperature,wind_speed,...
   62091,2023-01-01 00:00:00,1013.2,10.5,25.3,...
   ```

3. **Import:**
   ```bash
   python3 manage.py import_third_party_data --source era5 --file your_data.csv
   ```

4. **Confirm All Stations:**
   ```bash
   python3 manage.py confirm_qc_data --all
   ```

### Interpreting Results

**Confirmation Rate:**
- ✅ > 95%: Excellent - High confidence in QC
- ✅ 90-95%: Good - QC is reliable
- ⚠️ 85-90%: Fair - Investigate deviations
- ❌ < 85%: Poor - Review QC thresholds

**Statistical Metrics:**
- **MAE** (Mean Absolute Error): Lower is better
- **RMSE** (Root Mean Square Error): Penalizes large errors
- **Correlation**: > 0.95 is excellent

## Troubleshooting

**"No QC data file found"**
- Run: `cd .. && ./run_qc_ubuntu.sh`

**"No third-party data found"**
- Verify file path and station_id in CSV

**"Import failed"**
- Check CSV format matches requirements
- See: `Third Party Data/README.md`

## Full Documentation

- **Integration Guide**: `Third Party Data/INTEGRATION_GUIDE.md`
- **Data Format**: `Third Party Data/README.md`
- **API Docs**: `webapp/README_webapp.md`
- **Summary**: `THIRD_PARTY_DATA_SUMMARY.md`

## Interactive Demo

Run the complete demo:
```bash
cd ..
./demo_third_party_confirmation.sh
```

## Need Help?

1. Check documentation files
2. Review sample data format
3. Open GitHub issue
4. Contact repository owner

---

**Time to Complete:** ~5 minutes  
**Difficulty:** Easy  
**Prerequisites:** Python 3.8+, QC data files

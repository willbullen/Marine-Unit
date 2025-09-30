# Third-Party Data Confirmation System

## Overview

The Third-Party Data Confirmation System allows you to ingest external buoy data from various sources (NOAA NDBC, Copernicus Marine Service, etc.) and compare it with your station's QC'd data to validate and confirm data quality.

## Features

- **Multiple Data Sources**: Support for NOAA NDBC, Copernicus, UK Met Office, and manual uploads
- **Automated Comparison**: Compare station data with third-party data within configurable tolerances
- **Confirmation Tracking**: Track confirmation status for each parameter and timestamp
- **Discrepancy Detection**: Automatically flag significant differences between sources
- **API Integration**: RESTful API for data import and confirmation management

## Database Models

### ThirdPartyDataSource
Represents external data sources for buoy data.

**Fields:**
- `name`: Name of the data source
- `source_type`: Type (noaa, copernicus, ukmo, manual, other)
- `description`: Description of the data source
- `api_endpoint`: API endpoint URL (if applicable)
- `update_frequency`: How often data is updated
- `is_active`: Whether the source is currently active

### ThirdPartyData
Stores imported third-party buoy observations.

**Fields:**
- `station`: Foreign key to BuoyStation
- `source`: Foreign key to ThirdPartyDataSource
- `timestamp`: Observation timestamp
- Environmental parameters: `air_pressure`, `air_temp`, `humidity`, `wind_speed`, `wind_direction`
- Wave parameters: `wave_height`, `wave_height_max`, `wave_period`, `wave_direction`
- Water parameters: `sea_temp`
- `data_quality`: Quality flag from source
- `raw_data`: Original raw data (JSON)

### DataConfirmation
Tracks confirmation results comparing station data with third-party data.

**Fields:**
- `station`: Foreign key to BuoyStation
- `timestamp`: Observation timestamp
- `parameter`: Foreign key to QCParameter
- `station_value`: Value from station data
- `station_qc_status`: QC indicator from station data
- `third_party_source`: Source of third-party data
- `third_party_value`: Value from third-party source
- `difference`: Absolute difference between values
- `percent_difference`: Percentage difference
- `confirmation_status`: Status (confirmed, discrepancy, missing, pending)
- `tolerance_threshold`: Tolerance used for comparison
- `notes`: Additional notes

## API Endpoints

### Data Source Management

**List all third-party data sources:**
```
GET /api/third-party-sources/
```

**Create a new data source:**
```
POST /api/third-party-sources/
{
  "name": "My Data Source",
  "source_type": "noaa",
  "description": "Description here",
  "api_endpoint": "https://api.example.com",
  "update_frequency": "hourly"
}
```

**Update a data source:**
```
PATCH /api/third-party-sources/{id}/
{
  "is_active": false
}
```

### Third-Party Data Import

**Import third-party data:**
```
POST /api/import-third-party/
{
  "station_id": "62091",
  "source_id": 1,
  "data": [
    {
      "timestamp": "2024-01-01T12:00:00Z",
      "air_temp": 15.5,
      "wind_speed": 8.3,
      "wave_height": 2.1,
      "wave_height_max": 3.2
    },
    ...
  ]
}
```

**Response:**
```json
{
  "message": "Third-party data import completed",
  "imported": 24,
  "updated": 0,
  "errors": []
}
```

### Data Confirmation

**Run data confirmation:**
```
POST /api/run-confirmation/
{
  "station_id": "62091",
  "start_date": "2024-01-01T00:00:00Z",
  "end_date": "2024-01-07T23:59:59Z",
  "parameters": ["airtemp", "windsp", "hm0"],
  "tolerance_percent": 10.0
}
```

**Response:**
```json
{
  "message": "Data confirmation completed",
  "station_id": "62091",
  "period": "2024-01-01 to 2024-01-07",
  "confirmations_created": 168,
  "third_party_records": 56
}
```

**Get confirmation summary for a station:**
```
GET /api/stations/{station_id}/confirmation-summary/
```

**Response:**
```json
{
  "station_id": "62091",
  "station_name": "M2 Buoy",
  "total_confirmations": 168,
  "status_breakdown": {
    "confirmed": {
      "count": 150,
      "percentage": 89.3,
      "label": "Confirmed - Data matches within tolerance"
    },
    "discrepancy": {
      "count": 18,
      "percentage": 10.7,
      "label": "Discrepancy - Significant difference detected"
    }
  },
  "parameter_summary": [
    {
      "parameter": "airtemp",
      "display_name": "Air Temperature",
      "total": 56,
      "confirmed": 52,
      "discrepancies": 4,
      "confirmation_rate": 92.9
    },
    ...
  ]
}
```

### View Third-Party Data

**List third-party data with filters:**
```
GET /api/third-party-data/?station_id=62091&start_date=2024-01-01&end_date=2024-01-07
```

**View confirmations:**
```
GET /api/confirmations/?station_id=62091&status=discrepancy
```

## Usage Examples

### Python API Usage

```python
import requests

# Import third-party data
response = requests.post('http://localhost:8000/api/import-third-party/', 
    json={
        'station_id': '62091',
        'source_id': 1,
        'data': [
            {
                'timestamp': '2024-01-01T12:00:00Z',
                'air_temp': 15.5,
                'wind_speed': 8.3,
                'wave_height': 2.1
            }
        ]
    },
    auth=('username', 'password')
)

# Run confirmation
response = requests.post('http://localhost:8000/api/run-confirmation/',
    json={
        'station_id': '62091',
        'start_date': '2024-01-01T00:00:00Z',
        'end_date': '2024-01-07T23:59:59Z',
        'tolerance_percent': 10.0
    },
    auth=('username', 'password')
)

# Get summary
response = requests.get('http://localhost:8000/api/stations/62091/confirmation-summary/',
    auth=('username', 'password')
)
summary = response.json()
print(f"Confirmation rate: {summary['status_breakdown']['confirmed']['percentage']:.1f}%")
```

### Django Management Commands

**Setup third-party data sources:**
```bash
python manage.py setup_third_party_sources
```

**Run demo:**
```bash
python demo_third_party_confirmation.py
```

## Parameter Mapping

The system maps station parameter names to third-party data fields:

| Station Parameter | Third-Party Field | Description |
|------------------|-------------------|-------------|
| `airpressure` | `air_pressure` | Air pressure (hPa) |
| `airtemp` | `air_temp` | Air temperature (°C) |
| `humidity` | `humidity` | Relative humidity (%) |
| `windsp` | `wind_speed` | Wind speed (m/s) |
| `winddir` | `wind_direction` | Wind direction (degrees) |
| `hm0` | `wave_height` | Significant wave height (m) |
| `hmax` | `wave_height_max` | Maximum wave height (m) |
| `tp` | `wave_period` | Wave period (s) |
| `mdir` | `wave_direction` | Wave direction (degrees) |
| `seatemp_aa` | `sea_temp` | Sea temperature (°C) |

## Confirmation Status

- **confirmed**: Data matches within tolerance threshold
- **discrepancy**: Significant difference detected (exceeds tolerance)
- **missing**: No third-party data available for comparison
- **pending**: Awaiting confirmation processing

## Best Practices

1. **Regular Updates**: Import third-party data regularly (hourly/daily)
2. **Set Appropriate Tolerances**: Adjust tolerance thresholds based on parameter type and expected accuracy
3. **Review Discrepancies**: Investigate discrepancies to identify sensor issues or calibration needs
4. **Multiple Sources**: Use multiple third-party sources for cross-validation
5. **Documentation**: Keep notes on confirmation results for audit trails

## Troubleshooting

**No confirmations created:**
- Ensure third-party data exists for the specified time period
- Check that parameter names match the expected mapping
- Verify station QC data is available

**High discrepancy rate:**
- Check sensor calibration
- Review tolerance thresholds
- Verify third-party data quality
- Investigate environmental factors

**Import failures:**
- Verify timestamp format (ISO 8601)
- Check data types (numeric values)
- Ensure station and source exist
- Review error messages in response

## Future Enhancements

- Automated data fetching from public APIs
- Scheduled confirmation runs
- Email alerts for high discrepancy rates
- Advanced statistical analysis
- Graphical comparison visualizations
- Export confirmation reports to PDF

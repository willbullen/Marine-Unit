# Buoy QC Web Application

## Overview

This Django web application provides a modern interface for managing buoy quality control operations. It integrates with the existing QC processing scripts and provides a user-friendly way to configure QC limits and monitor data quality.

## Architecture

### Backend (Django)
- **Django REST Framework**: API endpoints for QC operations
- **Models**: BuoyStation, QCParameter, StationQCLimit, QCProcessingJob, QCResult
- **Integration**: Connects to existing QC processing scripts
- **Database**: SQLite for development (easily configurable for production)

### Frontend (React + shadcn/ui)
- **React TypeScript**: Modern frontend framework
- **shadcn/ui**: Beautiful, accessible UI components based on Radix UI
- **Tailwind CSS**: Utility-first CSS framework
- **Dashboard**: Inspired by https://ui.shadcn.com/blocks

## Features

### ✅ Implemented
- **Django Models**: Complete data model for stations, parameters, and QC limits
- **REST API**: Full CRUD operations for QC management
- **Station Management**: Track buoy stations with location and exposure data
- **QC Limits Configuration**: Station-specific QC threshold management
- **Data Integration**: Automatic import of existing QC processor configuration
- **File Downloads**: API endpoints for downloading QC reports and data

### 🚧 In Development
- **React Dashboard**: Modern UI for QC monitoring
- **QC Limits Interface**: Web-based QC threshold configuration
- **Real-time Processing**: Integration with background QC processing
- **Visualization Integration**: Display QC plots in web interface

## Quick Start

### Windows
```batch
# From webapp directory
run_webapp_windows.bat
```

### Ubuntu/Linux
```bash
# From webapp directory
chmod +x run_webapp_ubuntu.sh
./run_webapp_ubuntu.sh
```

### Manual Setup
```bash
# Activate virtual environment
source ../.venv/bin/activate  # Linux
# or
..\.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
pip install django djangorestframework django-cors-headers

# Run migrations
python manage.py migrate

# Set up initial QC data
python manage.py setup_qc_data

# Create admin user (optional)
python manage.py createsuperuser

# Start server
python manage.py runserver
```

## API Endpoints

### Station Management
- `GET /api/stations/` - List all buoy stations
- `GET /api/stations/{station_id}/` - Get station details
- `GET /api/stations/{station_id}/limits/` - Get QC limits for station

### QC Parameters
- `GET /api/parameters/` - List all QC parameters
- `POST /api/parameters/` - Create new QC parameter

### QC Limits Management
- `GET /api/limits/` - List all QC limits
- `POST /api/update-limits/` - Update QC limits for station/parameter
- `GET /api/limits/?station_id={id}` - Get limits for specific station

### Dashboard and Results
- `GET /api/dashboard/` - Get dashboard overview data
- `GET /api/results/` - List QC processing results
- `GET /api/results/?station_id={id}&year={year}` - Filter results

### File Downloads
- `GET /api/download/{station_id}/{year}/csv/` - Download QC'd CSV data
- `GET /api/download/{station_id}/{year}/pdf/` - Download PDF report
- `GET /api/download/{station_id}/{year}/png/` - Download visualization
- `GET /api/download/{station_id}/{year}/md/` - Download markdown report

### QC Processing
- `POST /api/run-qc/` - Trigger QC processing job

## Database Models

### BuoyStation
- Station metadata (ID, name, location, exposure type)
- Links to QC limits and results

### QCParameter
- Parameter definitions (name, units, defaults)
- Categorized by type (environmental, wave, water)

### StationQCLimit
- Station-specific QC threshold overrides
- Links station to parameter with custom limits

### QCProcessingJob
- Tracks background QC processing jobs
- Status monitoring and error handling

### QCResult
- Stores QC processing results
- Links to generated files and statistics

## Configuration

### QC Limits Structure
The system uses a two-tier approach:
1. **Default Limits**: Applied to all stations unless overridden
2. **Station-Specific Limits**: Override defaults based on location/exposure

Example station-specific configuration:
```python
# Station 62091 (Exposed Atlantic)
{
    'hm0': {'min': 0.0, 'max': 18.0, 'spike_threshold': 4.0},
    'windsp': {'min': 0.0, 'max': 60.0, 'spike_threshold': 20.0},
    'seatemp_aa': {'min': 4.0, 'max': 18.0, 'spike_threshold': 2.0}
}
```

### Environment Variables
- `DEBUG`: Set to False for production
- `SECRET_KEY`: Change for production deployment
- `ALLOWED_HOSTS`: Configure for production domain
- `DATABASE_URL`: For production database configuration

## Integration with Existing QC System

### File Paths
The webapp integrates with existing QC files:
- **QC Data**: `../QC Data/` - Generated QC results
- **QC Scripts**: `../QC Scripts/` - QC processing tools
- **Buoy Data**: `../Buoy Data/` - Original data files

### QC Processor Integration
The Django app can:
- Import existing QC configuration automatically
- Trigger QC processing through API calls
- Serve generated QC files through web interface
- Manage QC limits that sync with processing scripts

## Development

### Adding New Features
1. **Models**: Add to `qc_api/models.py`
2. **API Endpoints**: Add to `qc_api/views.py` and `qc_api/urls.py`
3. **Frontend Components**: Add to `frontend/src/components/`

### Database Management
```bash
# Create migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Reset QC data
python manage.py setup_qc_data
```

## Production Deployment

### Requirements
- Python 3.8+
- Django 5.2+
- PostgreSQL (recommended for production)
- Redis (for background tasks)
- Nginx (for static file serving)

### Security Considerations
- Change SECRET_KEY
- Set DEBUG=False
- Configure ALLOWED_HOSTS
- Use HTTPS in production
- Set up proper CORS policies
- Configure database security

## Troubleshooting

### Common Issues
1. **Import Errors**: Ensure QC Scripts directory is accessible
2. **Database Errors**: Run migrations and setup_qc_data command
3. **Static Files**: Create static and media directories
4. **CORS Issues**: Configure CORS_ALLOWED_ORIGINS for frontend

### Logs
- Django logs: Check console output
- QC Processing: Check QC processor output
- Database: Enable Django SQL logging if needed

## Future Enhancements

### Planned Features
- **Real-time Dashboard**: Live QC monitoring
- **Background Processing**: Celery integration for QC jobs
- **Advanced Visualizations**: Interactive charts and plots
- **User Management**: Role-based access control
- **Notifications**: Email/SMS alerts for QC issues
- **API Authentication**: Token-based API access

### Integration Opportunities
- **LangChain AI**: Intelligent QC decision making
- **ERA5 Data**: Weather model validation
- **Mobile App**: React Native companion app
- **Export Formats**: Additional report formats

#!/bin/bash

# =================================================================
# Third Party Data Confirmation Demo
# =================================================================
# This script demonstrates the complete workflow for importing and
# using third-party data to confirm QC'd buoy measurements
#
# Usage: chmod +x demo_third_party_confirmation.sh && ./demo_third_party_confirmation.sh
# =================================================================

set -e

echo "======================================================================"
echo "Third Party Data Confirmation Demo"
echo "======================================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Step 1: Show available third-party data
echo -e "${BLUE}Step 1: Sample Third-Party Data${NC}"
echo "----------------------------------------------------------------------"
echo "Sample data file: Third Party Data/sample_third_party_data.csv"
echo ""
head -5 "Third Party Data/sample_third_party_data.csv"
echo ""
read -p "Press Enter to continue..."

# Step 2: Set up Django database
echo ""
echo -e "${BLUE}Step 2: Set up Django Database${NC}"
echo "----------------------------------------------------------------------"
cd webapp
if [ ! -f "db.sqlite3" ]; then
    echo "Creating database and applying migrations..."
    python3 manage.py migrate
else
    echo "Database already exists"
fi
echo ""
read -p "Press Enter to continue..."

# Step 3: Set up QC data (stations, parameters)
echo ""
echo -e "${BLUE}Step 3: Initialize QC Data${NC}"
echo "----------------------------------------------------------------------"
echo "Setting up buoy stations and QC parameters..."
python3 manage.py setup_qc_data
echo ""
read -p "Press Enter to continue..."

# Step 4: Import third-party data
echo ""
echo -e "${BLUE}Step 4: Import Third-Party Data${NC}"
echo "----------------------------------------------------------------------"
echo "Importing sample third-party data from ERA5..."
python3 manage.py import_third_party_data \
    --source era5 \
    --file "../Third Party Data/sample_third_party_data.csv"
echo ""
read -p "Press Enter to continue..."

# Step 5: Show imported data count
echo ""
echo -e "${BLUE}Step 5: Verify Imported Data${NC}"
echo "----------------------------------------------------------------------"
echo "Querying imported third-party data via Django shell..."
python3 manage.py shell << EOF
from qc_api.models import ThirdPartyBuoyData
print(f"Total third-party records: {ThirdPartyBuoyData.objects.count()}")
print("\nRecords by station:")
for station in ['62091', '62092', '62093']:
    count = ThirdPartyBuoyData.objects.filter(station__station_id=station).count()
    print(f"  Station {station}: {count} records")
print("\nRecords by source:")
for source in ['era5', 'met_eireann', 'noaa']:
    count = ThirdPartyBuoyData.objects.filter(source=source).count()
    if count > 0:
        print(f"  {source}: {count} records")
EOF
echo ""
read -p "Press Enter to continue..."

# Step 6: Run comparison (if QC data exists)
echo ""
echo -e "${BLUE}Step 6: Run QC Confirmation Analysis${NC}"
echo "----------------------------------------------------------------------"
if [ -f "../QC/Data/buoy_62091_2023_qcd.csv" ]; then
    echo "Running confirmation analysis for Station 62091 - 2023..."
    python3 manage.py confirm_qc_data --station 62091 --year 2023 --source era5
else
    echo -e "${YELLOW}Note: QC data files not found. You would need to run the QC processor first.${NC}"
    echo "To run QC processing:"
    echo "  cd .."
    echo "  ./run_qc_ubuntu.sh"
    echo ""
    echo "Then re-run this demo to see the confirmation analysis."
fi
echo ""
read -p "Press Enter to continue..."

# Step 7: Generate comparison visualization (if QC data exists)
echo ""
echo -e "${BLUE}Step 7: Generate Comparison Visualization${NC}"
echo "----------------------------------------------------------------------"
if [ -f "../QC/Data/buoy_62091_2023_qcd.csv" ]; then
    echo "Creating comparison plots..."
    cd ../QC
    python3 third_party_comparison.py --station 62091 --year 2023 --source era5
    echo ""
    echo -e "${GREEN}Comparison plot saved: QC/Data/buoy_62091_2023_era5_comparison.png${NC}"
else
    echo -e "${YELLOW}Skipping visualization - QC data not available${NC}"
fi
echo ""
read -p "Press Enter to continue..."

# Step 8: Show API endpoints
echo ""
echo -e "${BLUE}Step 8: API Endpoints${NC}"
echo "----------------------------------------------------------------------"
echo "Third-party data is accessible via REST API endpoints:"
echo ""
echo "  List all third-party data:"
echo "    GET http://localhost:8000/api/third-party-data/"
echo ""
echo "  Filter by station:"
echo "    GET http://localhost:8000/api/third-party-data/?station_id=62091"
echo ""
echo "  Filter by source:"
echo "    GET http://localhost:8000/api/third-party-data/?source=era5"
echo ""
echo "  List confirmation results:"
echo "    GET http://localhost:8000/api/confirmations/"
echo ""
echo "  Filter confirmations by station and year:"
echo "    GET http://localhost:8000/api/confirmations/?station_id=62091&year=2023"
echo ""
echo "To test the API, start the Django development server:"
echo "  cd webapp"
echo "  python3 manage.py runserver"
echo ""
echo "Then visit: http://localhost:8000/api/"
echo ""

# Completion
echo "======================================================================"
echo -e "${GREEN}Demo Completed!${NC}"
echo "======================================================================"
echo ""
echo "Next steps:"
echo "  1. Import your own third-party data (ERA5, Met Éireann, etc.)"
echo "  2. Run QC processing if not already done"
echo "  3. Run confirmation analysis to validate QC results"
echo "  4. Use the API to access confirmation statistics"
echo ""
echo "Documentation:"
echo "  - Third Party Data/README.md - Data format and usage"
echo "  - readme.md - Main system documentation"
echo "  - webapp/README_webapp.md - API documentation"
echo ""
echo "======================================================================"

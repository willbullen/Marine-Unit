#!/usr/bin/env python3
"""
Storm Analysis Runner
====================

Simple runner script for the Marine Storm Analysis system.
This script provides a user-friendly interface to run storm analysis
with different options and configurations.

Usage:
    python run_storm_analysis.py [options]

Options:
    --help, -h          Show this help message
    --year YEAR         Process storms from specific year only
    --storm NAME        Process specific storm only
    --list              List all available storms
    --config FILE       Use custom configuration file
    --output DIR        Custom output directory
"""

import sys
import argparse
from pathlib import Path
import json

# Add the current directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

try:
    from storm_analyzer import MarineStormAnalyzer
except ImportError as e:
    print(f"Error importing storm_analyzer: {e}")
    print("Please ensure all required packages are installed:")
    print("pip install -r requirements.txt")
    sys.exit(1)


def list_storms(analyzer):
    """List all available storms in the database"""
    print("\nAvailable Storms:")
    print("=" * 50)
    
    total_storms = 0
    for year, storms in analyzer.storms_database.items():
        print(f"\n{year}:")
        for storm_name, storm_info in storms.items():
            dates = ", ".join(storm_info['dates'])
            print(f"  • {storm_name} ({dates})")
            total_storms += 1
    
    print(f"\nTotal: {total_storms} storms available")
    print("=" * 50)


def process_specific_storm(analyzer, storm_name):
    """Process a specific storm by name"""
    found_storm = None
    found_year = None
    
    # Search for storm in database
    for year, storms in analyzer.storms_database.items():
        if storm_name in storms:
            found_storm = storms[storm_name]
            found_year = year
            break
    
    if not found_storm:
        print(f"Storm '{storm_name}' not found in database.")
        print("Use --list to see available storms.")
        return False
    
    print(f"Processing {storm_name} from {found_year}...")
    
    # Load QC data
    analyzer.load_qc_data()
    
    if not analyzer.qc_data:
        print("No QC data available.")
        return False
    
    # Create storm directory
    storm_dir = analyzer.storm_data_dir / storm_name.replace(" ", "_")
    storm_dir.mkdir(exist_ok=True)
    
    # Extract and process storm data
    storm_data = analyzer.extract_storm_data(storm_name, {'info': found_storm})
    
    if not storm_data:
        print(f"No data available for {storm_name}")
        return False
    
    print(f"Found data from {len(storm_data)} station-years")
    
    # Create visualizations first
    overview_plot = analyzer.create_storm_visualizations(storm_name, storm_data, storm_dir)
    
    # Generate report
    md_content = analyzer.generate_storm_report(
        storm_name, 
        {'info': found_storm}, 
        storm_data, 
        storm_dir,
        overview_plot
    )
    
    # Save files
    md_path = storm_dir / f"{storm_name.replace(' ', '_')}_report.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    pdf_path = storm_dir / f"{storm_name.replace(' ', '_')}_report.pdf"
    analyzer.convert_md_to_pdf(md_content, pdf_path, storm_name)
    
    csv_path = storm_dir / f"{storm_name.replace(' ', '_')}_data.csv"
    analyzer.save_storm_data_csv(storm_data, csv_path)
    
    print(f"✓ {storm_name} processing complete")
    print(f"Files saved to: {storm_dir}")
    
    return True


def process_year_storms(analyzer, year):
    """Process all storms from a specific year"""
    year_str = str(year)
    
    if year_str not in analyzer.storms_database:
        print(f"No storms found for year {year}")
        print("Available years:", ", ".join(analyzer.storms_database.keys()))
        return False
    
    storms = analyzer.storms_database[year_str]
    print(f"Processing {len(storms)} storms from {year}...")
    
    # Load QC data once
    analyzer.load_qc_data()
    
    if not analyzer.qc_data:
        print("No QC data available.")
        return False
    
    processed = 0
    for storm_name in storms.keys():
        if process_specific_storm(analyzer, storm_name):
            processed += 1
    
    print(f"\nCompleted processing {processed} of {len(storms)} storms from {year}")
    return True


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description="Marine Storm Analysis and Reporting System",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--year', '-y',
        type=int,
        help='Process storms from specific year only (2023, 2024, 2025)'
    )
    
    parser.add_argument(
        '--storm', '-s',
        type=str,
        help='Process specific storm only (e.g., "Storm Agnes")'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all available storms'
    )
    
    parser.add_argument(
        '--output', '-o',
        type=str,
        default='../Storm Data',
        help='Custom output directory (default: ../Storm Data)'
    )
    
    parser.add_argument(
        '--qc-data', '-q',
        type=str,
        default='../QC Data',
        help='QC data directory (default: ../QC Data)'
    )
    
    args = parser.parse_args()
    
    try:
        # Initialize analyzer with custom paths if provided
        analyzer = MarineStormAnalyzer(
            qc_data_dir=args.qc_data,
            storm_data_dir=args.output
        )
        
        # Handle different options
        if args.list:
            list_storms(analyzer)
            
        elif args.storm:
            process_specific_storm(analyzer, args.storm)
            
        elif args.year:
            process_year_storms(analyzer, args.year)
            
        else:
            # Default: process all storms
            print("Processing all storms...")
            analyzer.process_all_storms()
    
    except KeyboardInterrupt:
        print("\n\nProcessing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

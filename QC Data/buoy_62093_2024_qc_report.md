# Buoy 62093 - 2024 Quality Control Report

**Generated:** 2025-08-27 20:55:34

## Data Overview

- **Station ID:** 62093
- **Year:** 2024
- **Total Records:** 7,245
- **Time Range:** 2024-01-01 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 303 days
- **Sensors/Loggers:** 1 active
  - 189_Wavesense: 7,245 records (100.0%)
- **Live Logger Used:** 189_Wavesense
  - Active Period: 2023-08-23 11:00 to 2025-08-01 15:00
  - Wave Data Available: No

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 7,120 records (98.3%)
- **No QC performed:** 125 records (1.7%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 7,245 | 0 | 0 | 0 | 0 | 7,245 | 100.0% |
| airtemp | 7,245 | 0 | 0 | 0 | 21 | 7,224 | 99.7% |
| humidity | 7,245 | 0 | 0 | 3 | 0 | 7,242 | 100.0% |
| windsp | 7,245 | 0 | 0 | 8 | 0 | 7,237 | 99.9% |
| winddir | 7,245 | 0 | 0 | 233 | 0 | 7,012 | 96.8% |
| hm0 | 7,245 | 0 | 0 | 0 | 96 | 7,149 | 98.7% |
| hmax | 7,245 | 0 | 0 | 1 | 10 | 7,234 | 99.8% |
| tp | 7,245 | 0 | 0 | 4 | 10 | 7,231 | 99.8% |
| mdir | 7,245 | 0 | 0 | 143 | 15 | 7,088 | 97.8% |
| seatemp_aa | 7,245 | 0 | 0 | 0 | 0 | 7,245 | 100.0% |

### Issues Identified

- airtemp: 21 flat line values (5+ consecutive identical)
- humidity: 3 spike values (>20.0 change)
- windsp: 8 spike values (>15.0 change)
- winddir: 233 spike values (>180.0 change)
- hm0: 96 flat line values (5+ consecutive identical)
- hmax: 1 spike values (>5.0 change)
- hmax: 10 flat line values (5+ consecutive identical)
- tp: 4 spike values (>10.0 change)
- tp: 10 flat line values (5+ consecutive identical)
- mdir: 143 spike values (>180.0 change)
- mdir: 15 flat line values (5+ consecutive identical)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 50.0 | 15.0 | Default |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 15.0 | 3.5 | Station-specific |
| hmax | 0.0 | 25.0 | 5.0 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 5.0 | 19.0 | 2.5 | Station-specific |

## Data Visualization

![QC Overview](buoy_62093_2024_qc_overview.png)

### QC Failure Color Coding

The visualization uses different colors to distinguish QC failure types:

- **Blue dots**: Good data (passed all QC tests)
- **Red dots**: Range failures (values outside physical limits)
- **Orange dots**: Spike failures (unrealistic sudden changes)
- **Purple dots**: Flat line failures (sensor stuck/malfunctioning)

The bottom-right panel shows a stacked bar chart with the percentage breakdown of each QC result type per parameter.

## Recommendations

### Manual QC Actions Needed

1. **Review flagged extreme values** - validate against weather events
2. **Investigate sensor failures** - replace/repair faulty sensors
3. **Cross-validate between loggers** - compare duplicate measurements
4. **Apply sensor hierarchy** - prioritize Wavesense for hm0, Datawell for hmax
5. **Transfer to production** - move QC'd data to irish_buoys_fugro table

### Next Steps

1. Execute parameter-level QC SQL commands from readme.md
2. Perform individual value corrections for flagged data
3. Complete record-level QC marking
4. Transfer approved data to production table

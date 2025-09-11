# Buoy 62094 - 2023 Quality Control Report

**Generated:** 2025-09-08 12:39:08

## Data Overview

- **Station ID:** 62094
- **Year:** 2023
- **Total Records:** 8,094
- **Time Range:** 2023-01-27 17:00:00 to 2023-12-30 23:00:00
- **Duration:** 337 days
- **Sensors/Loggers:** 1 active
  - 12143_CR6: 8,094 records (100.0%)
- **Live Logger Used:** 12143_CR6
  - Active Period: 2023-01-27 17:00 to 2024-07-13 09:00
  - Wave Data Available: Yes

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 7,396 records (91.4%)
- **No QC performed:** 698 records (8.6%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 8,094 | 0 | 0 | 0 | 0 | 4,391 | 54.3% |
| airtemp | 8,094 | 0 | 0 | 0 | 31 | 4,370 | 54.0% |
| humidity | 8,094 | 0 | 0 | 2 | 5 | 3,643 | 45.0% |
| windsp | 8,094 | 0 | 0 | 0 | 0 | 3,648 | 45.1% |
| winddir | 8,094 | 0 | 0 | 132 | 0 | 3,581 | 44.2% |
| hm0 | 8,094 | 0 | 0 | 0 | 1,383 | 2,963 | 36.6% |
| hmax | 8,094 | 0 | 0 | 0 | 228 | 3,551 | 43.9% |
| tp | 8,094 | 0 | 0 | 47 | 609 | 7,439 | 91.9% |
| mdir | 8,094 | 0 | 0 | 155 | 11 | 3,498 | 43.2% |
| seatemp_aa | 8,094 | 0 | 84 | 0 | 0 | 3,589 | 44.3% |

### Issues Identified

- airtemp: 31 flat line values (5+ consecutive identical)
- humidity: 2 spike values (>20.0 change)
- humidity: 5 flat line values (5+ consecutive identical)
- winddir: 132 spike values (>180.0 change)
- hm0: 1383 flat line values (5+ consecutive identical)
- hmax: 228 flat line values (5+ consecutive identical)
- tp: 47 spike values (>10.0 change)
- tp: 609 flat line values (5+ consecutive identical)
- mdir: 155 spike values (>180.0 change)
- mdir: 11 flat line values (5+ consecutive identical)
- seatemp_aa: 84 values outside range [4.5-18.5]

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 55.0 | 18.0 | Station-specific |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 16.0 | 3.5 | Station-specific |
| hmax | 0.0 | 26.0 | 5.5 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 4.5 | 18.5 | 2.5 | Station-specific |

## Data Visualization

![QC Overview](buoy_62094_2023_qc_overview.png)

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

# Buoy 62091 - 2023 Quality Control Report

**Generated:** 2025-08-27 20:55:07

## Data Overview

- **Station ID:** 62091
- **Year:** 2023
- **Total Records:** 8,731
- **Time Range:** 2023-01-01 00:00:00 to 2023-12-30 23:00:00
- **Duration:** 363 days
- **Sensors/Loggers:** 1 active
  - 347_Wavesense: 8,731 records (100.0%)
- **Live Logger Used:** 347_Wavesense
  - Active Period: 2022-02-11 11:00 to 2024-02-23 19:00
  - Wave Data Available: Yes

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 8,668 records (99.3%)
- **No QC performed:** 63 records (0.7%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 8,731 | 0 | 0 | 0 | 0 | 3,669 | 42.0% |
| airtemp | 8,731 | 0 | 0 | 0 | 17 | 2,909 | 33.3% |
| humidity | 8,731 | 0 | 0 | 4 | 0 | 2,923 | 33.5% |
| windsp | 8,731 | 0 | 0 | 0 | 0 | 2,926 | 33.5% |
| winddir | 8,731 | 0 | 0 | 203 | 0 | 3,564 | 40.8% |
| hm0 | 8,731 | 0 | 0 | 0 | 367 | 2,810 | 32.2% |
| hmax | 8,731 | 10 | 0 | 0 | 501 | 5,413 | 62.0% |
| tp | 8,731 | 0 | 0 | 15 | 0 | 8,716 | 99.8% |
| mdir | 8,731 | 0 | 0 | 161 | 0 | 2,848 | 32.6% |
| seatemp_aa | 8,731 | 0 | 0 | 0 | 0 | 2,183 | 25.0% |

### Issues Identified

- airtemp: 17 flat line values (5+ consecutive identical)
- humidity: 4 spike values (>20.0 change)
- winddir: 203 spike values (>180.0 change)
- hm0: 367 flat line values (5+ consecutive identical)
- hmax: 501 flat line values (5+ consecutive identical)
- tp: 15 spike values (>10.0 change)
- mdir: 161 spike values (>180.0 change)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 60.0 | 20.0 | Station-specific |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 18.0 | 4.0 | Station-specific |
| hmax | 0.0 | 30.0 | 6.0 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 4.0 | 18.0 | 2.0 | Station-specific |

## Data Visualization

![QC Overview](buoy_62091_2023_qc_overview.png)

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

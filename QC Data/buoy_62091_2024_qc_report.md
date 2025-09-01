# Buoy 62091 - 2024 Quality Control Report

**Generated:** 2025-08-27 20:55:10

## Data Overview

- **Station ID:** 62091
- **Year:** 2024
- **Total Records:** 5,943
- **Time Range:** 2024-02-26 08:00:00 to 2024-10-30 23:00:00
- **Duration:** 247 days
- **Sensors/Loggers:** 1 active
  - 7577_CR6: 5,943 records (100.0%)
- **Live Logger Used:** 7577_CR6
  - Active Period: 2024-02-26 08:00 to 2025-02-13 23:00
  - Wave Data Available: Yes
  - Notes: Seabird & DW

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 5,000 records (84.1%)
- **No QC performed:** 943 records (15.9%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 5,943 | 0 | 0 | 0 | 0 | 5,943 | 100.0% |
| airtemp | 5,943 | 0 | 0 | 0 | 0 | 5,943 | 100.0% |
| humidity | 5,943 | 0 | 0 | 3 | 72 | 5,868 | 98.7% |
| windsp | 5,943 | 0 | 0 | 0 | 0 | 5,943 | 100.0% |
| winddir | 5,943 | 0 | 0 | 199 | 0 | 5,744 | 96.7% |
| hm0 | 5,943 | 0 | 0 | 0 | 943 | 5,000 | 84.1% |
| hmax | 5,943 | 0 | 0 | 0 | 249 | 5,694 | 95.8% |
| tp | 5,943 | 0 | 0 | 13 | 138 | 5,792 | 97.5% |
| mdir | 5,943 | 0 | 0 | 160 | 0 | 5,783 | 97.3% |
| seatemp_aa | 5,943 | 0 | 0 | 0 | 0 | 5,943 | 100.0% |

### Issues Identified

- humidity: 3 spike values (>20.0 change)
- humidity: 72 flat line values (5+ consecutive identical)
- winddir: 199 spike values (>180.0 change)
- hm0: 943 flat line values (5+ consecutive identical)
- hmax: 249 flat line values (5+ consecutive identical)
- tp: 13 spike values (>10.0 change)
- tp: 138 flat line values (5+ consecutive identical)
- mdir: 160 spike values (>180.0 change)

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

![QC Overview](buoy_62091_2024_qc_overview.png)

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

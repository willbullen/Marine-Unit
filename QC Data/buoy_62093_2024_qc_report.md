# Buoy 62093 - 2024 Quality Control Report

**Generated:** 2025-08-19 23:48:58

## Data Overview

- **Station ID:** 62093
- **Year:** 2024
- **Total Records:** 14,538
- **Time Range:** 2024-01-01 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 303 days
- **Sensors/Loggers:** 2 active
  - 12144_CR6: 7,293 records (50.2%)
  - 189_Wavesense: 7,245 records (49.8%)

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 13,688 records (94.2%)
- **No QC performed:** 850 records (5.8%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 14,538 | 0 | 0 | 0 | 12 | 14,526 | 99.9% |
| airtemp | 14,538 | 0 | 0 | 0 | 501 | 14,037 | 96.6% |
| humidity | 14,538 | 0 | 0 | 3 | 66 | 14,469 | 99.5% |
| windsp | 14,538 | 0 | 0 | 8 | 18 | 14,512 | 99.8% |
| winddir | 14,538 | 0 | 0 | 233 | 12 | 14,293 | 98.3% |
| hm0 | 14,538 | 0 | 0 | 0 | 315 | 14,223 | 97.8% |
| hmax | 14,538 | 0 | 0 | 3 | 0 | 14,535 | 100.0% |
| tp | 14,538 | 0 | 0 | 10 | 38 | 14,490 | 99.7% |
| mdir | 14,538 | 0 | 0 | 412 | 0 | 14,126 | 97.2% |
| seatemp_aa | 14,538 | 0 | 0 | 0 | 106 | 14,432 | 99.3% |

### Issues Identified

- airpressure: 12 flat line values (5+ consecutive identical)
- airtemp: 501 flat line values (5+ consecutive identical)
- humidity: 3 spike values (>20.0 change)
- humidity: 66 flat line values (5+ consecutive identical)
- windsp: 8 spike values (>15.0 change)
- windsp: 18 flat line values (5+ consecutive identical)
- winddir: 233 spike values (>180.0 change)
- winddir: 12 flat line values (5+ consecutive identical)
- hm0: 315 flat line values (5+ consecutive identical)
- hmax: 3 spike values (>5.0 change)
- tp: 10 spike values (>10.0 change)
- tp: 38 flat line values (5+ consecutive identical)
- mdir: 412 spike values (>180.0 change)
- seatemp_aa: 106 flat line values (5+ consecutive identical)

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

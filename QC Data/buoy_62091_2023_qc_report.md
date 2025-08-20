# Buoy 62091 - 2023 Quality Control Report

**Generated:** 2025-08-19 23:48:16

## Data Overview

- **Station ID:** 62091
- **Year:** 2023
- **Total Records:** 17,364
- **Time Range:** 2023-01-01 00:00:00 to 2023-12-30 23:00:00
- **Duration:** 363 days
- **Sensors/Loggers:** 2 active
  - 347_Wavesense: 8,731 records (50.3%)
  - 8704_CR6: 8,633 records (49.7%)

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 16,368 records (94.3%)
- **No QC performed:** 996 records (5.7%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 17,364 | 0 | 0 | 0 | 26 | 12,282 | 70.7% |
| airtemp | 17,364 | 0 | 0 | 0 | 481 | 11,228 | 64.7% |
| humidity | 17,364 | 0 | 0 | 4 | 33 | 11,536 | 66.4% |
| windsp | 17,364 | 0 | 0 | 0 | 48 | 11,529 | 66.4% |
| winddir | 17,364 | 0 | 0 | 203 | 18 | 12,150 | 70.0% |
| hm0 | 17,364 | 0 | 0 | 0 | 1,082 | 10,812 | 62.3% |
| hmax | 17,364 | 10 | 0 | 0 | 235 | 7,946 | 45.8% |
| tp | 17,364 | 0 | 0 | 117 | 116 | 17,132 | 98.7% |
| mdir | 17,364 | 0 | 0 | 238 | 0 | 11,385 | 65.6% |
| seatemp_aa | 17,364 | 0 | 0 | 2 | 94 | 10,746 | 61.9% |

### Issues Identified

- airpressure: 26 flat line values (5+ consecutive identical)
- airtemp: 481 flat line values (5+ consecutive identical)
- humidity: 4 spike values (>20.0 change)
- humidity: 33 flat line values (5+ consecutive identical)
- windsp: 48 flat line values (5+ consecutive identical)
- winddir: 203 spike values (>180.0 change)
- winddir: 18 flat line values (5+ consecutive identical)
- hm0: 1082 flat line values (5+ consecutive identical)
- hmax: 235 flat line values (5+ consecutive identical)
- tp: 117 spike values (>10.0 change)
- tp: 116 flat line values (5+ consecutive identical)
- mdir: 238 spike values (>180.0 change)
- seatemp_aa: 2 spike values (>2.0 change)
- seatemp_aa: 94 flat line values (5+ consecutive identical)

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

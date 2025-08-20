# Buoy 62095 - 2024 Quality Control Report

**Generated:** 2025-08-19 23:49:32

## Data Overview

- **Station ID:** 62095
- **Year:** 2024
- **Total Records:** 14,551
- **Time Range:** 2024-01-01 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 303 days
- **Sensors/Loggers:** 4 active
  - 12146_CR6: 4,551 records (31.3%)
  - 13443_CR6: 4,550 records (31.3%)
  - 341_Wavesense: 2,726 records (18.7%)
  - 12145_CR6: 2,724 records (18.7%)

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 13,416 records (92.2%)
- **No QC performed:** 1,135 records (7.8%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 14,551 | 0 | 0 | 0 | 12 | 14,539 | 99.9% |
| airtemp | 14,551 | 0 | 0 | 0 | 559 | 13,992 | 96.2% |
| humidity | 14,551 | 0 | 0 | 7 | 47 | 14,497 | 99.6% |
| windsp | 14,551 | 0 | 0 | 2 | 48 | 14,501 | 99.7% |
| winddir | 14,551 | 0 | 0 | 187 | 6 | 14,358 | 98.7% |
| hm0 | 14,551 | 0 | 0 | 2 | 540 | 14,009 | 96.3% |
| hmax | 14,551 | 0 | 0 | 19 | 194 | 14,338 | 98.5% |
| tp | 14,551 | 0 | 0 | 6 | 58 | 14,487 | 99.6% |
| mdir | 14,551 | 0 | 0 | 660 | 0 | 13,891 | 95.5% |
| seatemp_aa | 14,551 | 0 | 0 | 0 | 194 | 14,357 | 98.7% |

### Issues Identified

- airpressure: 12 flat line values (5+ consecutive identical)
- airtemp: 559 flat line values (5+ consecutive identical)
- humidity: 7 spike values (>20.0 change)
- humidity: 47 flat line values (5+ consecutive identical)
- windsp: 2 spike values (>15.0 change)
- windsp: 48 flat line values (5+ consecutive identical)
- winddir: 187 spike values (>180.0 change)
- winddir: 6 flat line values (5+ consecutive identical)
- hm0: 2 spike values (>3.0 change)
- hm0: 540 flat line values (5+ consecutive identical)
- hmax: 19 spike values (>4.5 change)
- hmax: 194 flat line values (5+ consecutive identical)
- tp: 6 spike values (>10.0 change)
- tp: 58 flat line values (5+ consecutive identical)
- mdir: 660 spike values (>180.0 change)
- seatemp_aa: 194 flat line values (5+ consecutive identical)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -15.0 | 35.0 | 4.0 | Station-specific |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 50.0 | 15.0 | Default |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 14.0 | 3.0 | Station-specific |
| hmax | 0.0 | 22.0 | 4.5 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 6.0 | 19.0 | 2.0 | Station-specific |

## Data Visualization

![QC Overview](buoy_62095_2024_qc_overview.png)

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

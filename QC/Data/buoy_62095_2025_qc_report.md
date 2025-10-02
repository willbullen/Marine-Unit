# Buoy 62095 - 2025 Quality Control Report

**Generated:** 2025-10-02 13:41:10

## Data Overview

- **Station ID:** 62095
- **Year:** 2025
- **Total Records:** 5,424
- **Time Range:** 2025-01-01 00:00:00 to 2025-08-14 23:00:00
- **Duration:** 225 days
- **Sensors/Loggers:** 2 active
  - 12146_CR6: 3,156 records (58.2%)
  - 12143_CR6: 2,268 records (41.8%)
- **Live Logger Used:** 12146_CR6
  - Active Period: 2024-04-24 08:00 to 2025-05-12 11:00
  - Wave Data Available: Yes
  - Notes: DW & SB

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 5,007 records (92.3%)
- **No QC performed:** 417 records (7.7%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 5,424 | 0 | 3 | 1 | 0 | 5,420 | 99.9% |
| airtemp | 5,424 | 0 | 0 | 1 | 21 | 5,402 | 99.6% |
| humidity | 5,424 | 0 | 0 | 9 | 0 | 5,415 | 99.8% |
| windsp | 5,424 | 0 | 2 | 3 | 0 | 5,420 | 99.9% |
| windgust | 5,424 | 0 | 3 | 2 | 0 | 5,420 | 99.9% |
| winddir | 5,424 | 0 | 0 | 114 | 0 | 5,310 | 97.9% |
| hm0 | 5,424 | 0 | 0 | 0 | 391 | 5,033 | 92.8% |
| hmax | 5,424 | 0 | 0 | 2 | 42 | 5,380 | 99.2% |
| tp | 5,424 | 0 | 0 | 0 | 549 | 4,875 | 89.9% |
| mdir | 5,424 | 0 | 0 | 57 | 0 | 5,367 | 98.9% |
| seatemp_aa | 5,424 | 0 | 0 | 0 | 5 | 5,419 | 99.9% |

### Issues Identified

- airpressure: 3 values outside range [950.0-1050.0]
- airpressure: 1 spike values (>10.0 change)
- airtemp: 1 spike values (>4.0 change)
- airtemp: 21 flat line values (5+ consecutive identical)
- humidity: 9 spike values (>20.0 change)
- windsp: 2 values outside range [0.0-50.0]
- windsp: 3 spike values (>15.0 change)
- windgust: 3 values outside range [0.0-60.0]
- windgust: 2 spike values (>20.0 change)
- winddir: 114 spike values (>180.0 change)
- hm0: 391 flat line values (5+ consecutive identical)
- hmax: 2 spike values (>4.5 change)
- hmax: 42 flat line values (5+ consecutive identical)
- tp: 549 flat line values (5+ consecutive identical)
- mdir: 57 spike values (>180.0 change)
- seatemp_aa: 5 flat line values (5+ consecutive identical)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -15.0 | 35.0 | 4.0 | Station-specific |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 50.0 | 15.0 | Default |
| windgust | 0.0 | 60.0 | 20.0 | Default |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 14.0 | 3.0 | Station-specific |
| hmax | 0.0 | 22.0 | 4.5 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 6.0 | 19.0 | 2.0 | Station-specific |

## Data Visualization

![QC Overview](buoy_62095_2025_qc_overview.png)

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

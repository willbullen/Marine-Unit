# Buoy 62091 - 2024 Quality Control Report

**Generated:** 2025-10-02 13:40:19

## Data Overview

- **Station ID:** 62091
- **Year:** 2024
- **Total Records:** 7,235
- **Time Range:** 2024-01-01 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 303 days
- **Sensors/Loggers:** 2 active
  - 7577_CR6: 5,943 records (82.1%)
  - 347_Wavesense: 1,292 records (17.9%)
- **Live Logger Used:** 7577_CR6
  - Active Period: 2024-02-26 08:00 to 2025-02-13 23:00
  - Wave Data Available: Yes
  - Notes: Seabird & DW

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 6,281 records (86.8%)
- **No QC performed:** 954 records (13.2%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 7,235 | 0 | 0 | 1 | 0 | 7,234 | 100.0% |
| airtemp | 7,235 | 0 | 0 | 0 | 0 | 7,235 | 100.0% |
| humidity | 7,235 | 0 | 0 | 3 | 72 | 7,160 | 99.0% |
| windsp | 7,235 | 0 | 0 | 0 | 0 | 7,235 | 100.0% |
| windgust | 7,235 | 0 | 0 | 0 | 0 | 7,235 | 100.0% |
| winddir | 7,235 | 0 | 0 | 225 | 0 | 7,010 | 96.9% |
| hm0 | 7,235 | 0 | 0 | 0 | 953 | 6,282 | 86.8% |
| hmax | 7,235 | 0 | 0 | 0 | 278 | 6,957 | 96.2% |
| tp | 7,235 | 0 | 0 | 13 | 143 | 7,079 | 97.8% |
| mdir | 7,235 | 0 | 0 | 192 | 0 | 7,043 | 97.3% |
| seatemp_aa | 7,235 | 0 | 0 | 0 | 0 | 7,235 | 100.0% |

### Issues Identified

- airpressure: 1 spike values (>10.0 change)
- humidity: 3 spike values (>20.0 change)
- humidity: 72 flat line values (5+ consecutive identical)
- winddir: 225 spike values (>180.0 change)
- hm0: 953 flat line values (5+ consecutive identical)
- hmax: 278 flat line values (5+ consecutive identical)
- tp: 13 spike values (>10.0 change)
- tp: 143 flat line values (5+ consecutive identical)
- mdir: 192 spike values (>180.0 change)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 60.0 | 20.0 | Station-specific |
| windgust | 0.0 | 80.0 | 25.0 | Station-specific |
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

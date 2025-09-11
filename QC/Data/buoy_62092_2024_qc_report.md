# Buoy 62092 - 2024 Quality Control Report

**Generated:** 2025-09-08 12:38:37

## Data Overview

- **Station ID:** 62092
- **Year:** 2024
- **Total Records:** 6,906
- **Time Range:** 2024-01-17 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 287 days
- **Sensors/Loggers:** 1 active
  - 427_Wavesense: 6,906 records (100.0%)
- **Live Logger Used:** 427_Wavesense
  - Active Period: 2024-01-17 00:00 to Present
  - Wave Data Available: No
  - Notes: No MD File Received

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 6,735 records (97.5%)
- **No QC performed:** 171 records (2.5%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 6,906 | 0 | 0 | 2 | 0 | 6,904 | 100.0% |
| airtemp | 6,906 | 0 | 0 | 2 | 25 | 6,879 | 99.6% |
| humidity | 6,906 | 0 | 0 | 4 | 29 | 6,874 | 99.5% |
| windsp | 6,906 | 0 | 1 | 3 | 0 | 6,903 | 100.0% |
| winddir | 6,906 | 0 | 0 | 201 | 0 | 6,705 | 97.1% |
| hm0 | 6,906 | 0 | 11 | 21 | 122 | 6,761 | 97.9% |
| hmax | 6,906 | 0 | 9 | 40 | 10 | 6,856 | 99.3% |
| tp | 6,906 | 0 | 0 | 17 | 0 | 6,889 | 99.8% |
| mdir | 6,906 | 0 | 0 | 35 | 12 | 6,859 | 99.3% |
| seatemp_aa | 6,906 | 0 | 1 | 2 | 0 | 6,904 | 100.0% |

### Issues Identified

- airpressure: 2 spike values (>10.0 change)
- airtemp: 2 spike values (>5.0 change)
- airtemp: 25 flat line values (5+ consecutive identical)
- humidity: 4 spike values (>20.0 change)
- humidity: 29 flat line values (5+ consecutive identical)
- windsp: 1 values outside range [0.0-50.0]
- windsp: 3 spike values (>15.0 change)
- winddir: 201 spike values (>180.0 change)
- hm0: 11 values outside range [0.0-12.0]
- hm0: 21 spike values (>2.5 change)
- hm0: 122 flat line values (5+ consecutive identical)
- hmax: 9 values outside range [0.0-20.0]
- hmax: 40 spike values (>4.0 change)
- hmax: 10 flat line values (5+ consecutive identical)
- tp: 17 spike values (>10.0 change)
- mdir: 35 spike values (>180.0 change)
- mdir: 12 flat line values (5+ consecutive identical)
- seatemp_aa: 1 values outside range [6.0-20.0]
- seatemp_aa: 2 spike values (>2.5 change)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 50.0 | 15.0 | Default |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 12.0 | 2.5 | Station-specific |
| hmax | 0.0 | 20.0 | 4.0 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 6.0 | 20.0 | 2.5 | Station-specific |

## Data Visualization

![QC Overview](buoy_62092_2024_qc_overview.png)

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

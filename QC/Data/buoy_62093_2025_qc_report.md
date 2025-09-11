# Buoy 62093 - 2025 Quality Control Report

**Generated:** 2025-09-08 12:38:52

## Data Overview

- **Station ID:** 62093
- **Year:** 2025
- **Total Records:** 5,103
- **Time Range:** 2025-01-01 00:00:00 to 2025-08-01 15:00:00
- **Duration:** 212 days
- **Sensors/Loggers:** 1 active
  - 189_Wavesense: 5,103 records (100.0%)
- **Live Logger Used:** 189_Wavesense
  - Active Period: 2023-08-23 11:00 to 2025-08-01 15:00
  - Wave Data Available: No

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 5,001 records (98.0%)
- **No QC performed:** 102 records (2.0%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 5,103 | 0 | 5 | 0 | 0 | 5,098 | 99.9% |
| airtemp | 5,103 | 0 | 0 | 0 | 27 | 5,076 | 99.5% |
| humidity | 5,103 | 0 | 0 | 4 | 0 | 5,099 | 99.9% |
| windsp | 5,103 | 0 | 1 | 4 | 0 | 5,098 | 99.9% |
| winddir | 5,103 | 0 | 0 | 111 | 0 | 4,992 | 97.8% |
| hm0 | 5,103 | 0 | 0 | 0 | 65 | 5,038 | 98.7% |
| hmax | 5,103 | 0 | 0 | 1 | 11 | 5,091 | 99.8% |
| tp | 5,103 | 0 | 0 | 2 | 0 | 5,101 | 100.0% |
| mdir | 5,103 | 0 | 0 | 98 | 0 | 5,005 | 98.1% |
| seatemp_aa | 5,103 | 0 | 0 | 0 | 0 | 5,103 | 100.0% |

### Issues Identified

- airpressure: 5 values outside range [950.0-1050.0]
- airtemp: 27 flat line values (5+ consecutive identical)
- humidity: 4 spike values (>20.0 change)
- windsp: 1 values outside range [0.0-50.0]
- windsp: 4 spike values (>15.0 change)
- winddir: 111 spike values (>180.0 change)
- hm0: 65 flat line values (5+ consecutive identical)
- hmax: 1 spike values (>5.0 change)
- hmax: 11 flat line values (5+ consecutive identical)
- tp: 2 spike values (>10.0 change)
- mdir: 98 spike values (>180.0 change)

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

![QC Overview](buoy_62093_2025_qc_overview.png)

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

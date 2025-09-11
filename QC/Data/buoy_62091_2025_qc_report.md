# Buoy 62091 - 2025 Quality Control Report

**Generated:** 2025-09-08 12:38:30

## Data Overview

- **Station ID:** 62091
- **Year:** 2025
- **Total Records:** 4,118
- **Time Range:** 2025-02-24 10:00:00 to 2025-08-14 23:00:00
- **Duration:** 171 days
- **Sensors/Loggers:** 1 active
  - 12145_CR6: 4,118 records (100.0%)
- **Live Logger Used:** 12145_CR6
  - Active Period: 2025-02-24 10:00 to Present
  - Wave Data Available: Yes
  - Notes: Seabird & DW

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 3,337 records (81.0%)
- **No QC performed:** 781 records (19.0%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 4,118 | 0 | 0 | 0 | 0 | 4,118 | 100.0% |
| airtemp | 4,118 | 0 | 0 | 0 | 0 | 4,118 | 100.0% |
| humidity | 4,118 | 0 | 0 | 0 | 0 | 4,118 | 100.0% |
| windsp | 4,118 | 0 | 0 | 0 | 0 | 4,118 | 100.0% |
| winddir | 4,118 | 0 | 0 | 126 | 0 | 3,992 | 96.9% |
| hm0 | 4,118 | 0 | 0 | 0 | 781 | 3,337 | 81.0% |
| hmax | 4,118 | 0 | 0 | 0 | 195 | 3,923 | 95.3% |
| tp | 4,118 | 0 | 1 | 26 | 27 | 4,065 | 98.7% |
| mdir | 4,118 | 0 | 0 | 111 | 0 | 4,007 | 97.3% |
| seatemp_aa | 4,118 | 0 | 0 | 4 | 0 | 4,114 | 99.9% |

### Issues Identified

- winddir: 126 spike values (>180.0 change)
- hm0: 781 flat line values (5+ consecutive identical)
- hmax: 195 flat line values (5+ consecutive identical)
- tp: 1 values outside range [1.0-25.0]
- tp: 26 spike values (>10.0 change)
- tp: 27 flat line values (5+ consecutive identical)
- mdir: 111 spike values (>180.0 change)
- seatemp_aa: 4 spike values (>2.0 change)

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

![QC Overview](buoy_62091_2025_qc_overview.png)

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

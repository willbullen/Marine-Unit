# Buoy 62091 - 2025 Quality Control Report

**Generated:** 2025-10-02 13:40:23

## Data Overview

- **Station ID:** 62091
- **Year:** 2025
- **Total Records:** 5,060
- **Time Range:** 2025-01-01 00:00:00 to 2025-08-14 23:00:00
- **Duration:** 225 days
- **Sensors/Loggers:** 2 active
  - 12145_CR6: 4,118 records (81.4%)
  - 7577_CR6: 942 records (18.6%)
- **Live Logger Used:** 12145_CR6
  - Active Period: 2025-02-24 10:00 to Present
  - Wave Data Available: Yes
  - Notes: Seabird & DW

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 4,181 records (82.6%)
- **No QC performed:** 879 records (17.4%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 5,060 | 0 | 1 | 2 | 0 | 5,058 | 100.0% |
| airtemp | 5,060 | 0 | 0 | 2 | 0 | 5,058 | 100.0% |
| humidity | 5,060 | 0 | 0 | 4 | 0 | 5,056 | 99.9% |
| windsp | 5,060 | 0 | 0 | 1 | 0 | 5,059 | 100.0% |
| windgust | 5,060 | 0 | 0 | 1 | 0 | 5,059 | 100.0% |
| winddir | 5,060 | 0 | 0 | 138 | 0 | 4,922 | 97.3% |
| hm0 | 5,060 | 0 | 0 | 0 | 877 | 4,183 | 82.7% |
| hmax | 5,060 | 0 | 0 | 0 | 224 | 4,836 | 95.6% |
| tp | 5,060 | 0 | 1 | 35 | 48 | 4,977 | 98.4% |
| mdir | 5,060 | 0 | 0 | 130 | 0 | 4,930 | 97.4% |
| seatemp_aa | 5,060 | 0 | 1 | 6 | 0 | 5,054 | 99.9% |

### Issues Identified

- airpressure: 1 values outside range [950.0-1050.0]
- airpressure: 2 spike values (>10.0 change)
- airtemp: 2 spike values (>5.0 change)
- humidity: 4 spike values (>20.0 change)
- windsp: 1 spike values (>20.0 change)
- windgust: 1 spike values (>25.0 change)
- winddir: 138 spike values (>180.0 change)
- hm0: 877 flat line values (5+ consecutive identical)
- hmax: 224 flat line values (5+ consecutive identical)
- tp: 1 values outside range [1.0-25.0]
- tp: 35 spike values (>10.0 change)
- tp: 48 flat line values (5+ consecutive identical)
- mdir: 130 spike values (>180.0 change)
- seatemp_aa: 1 values outside range [4.0-18.0]
- seatemp_aa: 6 spike values (>2.0 change)

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

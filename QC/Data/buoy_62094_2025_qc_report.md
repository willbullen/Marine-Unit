# Buoy 62094 - 2025 Quality Control Report

**Generated:** 2025-10-02 13:40:58

## Data Overview

- **Station ID:** 62094
- **Year:** 2025
- **Total Records:** 5,423
- **Time Range:** 2025-01-01 00:00:00 to 2025-08-14 23:00:00
- **Duration:** 225 days
- **Sensors/Loggers:** 1 active
  - 347_Wavesense: 5,423 records (100.0%)
- **Live Logger Used:** 347_Wavesense
  - Active Period: 2024-07-15 08:00 to Present
  - Wave Data Available: Yes
  - Notes: Fugro & RBR

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 4,946 records (91.2%)
- **No QC performed:** 477 records (8.8%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 5,423 | 0 | 0 | 0 | 0 | 5,423 | 100.0% |
| airtemp | 5,423 | 0 | 0 | 0 | 26 | 5,397 | 99.5% |
| humidity | 5,423 | 0 | 0 | 1 | 5 | 5,417 | 99.9% |
| windsp | 5,423 | 0 | 0 | 0 | 0 | 5,423 | 100.0% |
| windgust | 5,423 | 0 | 0 | 0 | 0 | 5,423 | 100.0% |
| winddir | 5,423 | 0 | 0 | 90 | 0 | 5,333 | 98.3% |
| hm0 | 5,423 | 0 | 0 | 0 | 451 | 4,972 | 91.7% |
| hmax | 5,423 | 0 | 0 | 0 | 241 | 5,182 | 95.6% |
| tp | 5,423 | 0 | 0 | 27 | 0 | 5,396 | 99.5% |
| mdir | 5,423 | 0 | 0 | 71 | 6 | 5,346 | 98.6% |
| seatemp_aa | 5,423 | 0 | 68 | 24 | 0 | 5,343 | 98.5% |

### Issues Identified

- airtemp: 26 flat line values (5+ consecutive identical)
- humidity: 1 spike values (>20.0 change)
- humidity: 5 flat line values (5+ consecutive identical)
- winddir: 90 spike values (>180.0 change)
- hm0: 451 flat line values (5+ consecutive identical)
- hmax: 241 flat line values (5+ consecutive identical)
- tp: 27 spike values (>10.0 change)
- mdir: 71 spike values (>180.0 change)
- mdir: 6 flat line values (5+ consecutive identical)
- seatemp_aa: 68 values outside range [4.5-18.5]
- seatemp_aa: 24 spike values (>2.5 change)

## QC Limits Applied

Station-specific QC limits used for this analysis:

| Parameter | Min Value | Max Value | Spike Threshold | Notes |
|-----------|-----------|-----------|-----------------|-------|
| airpressure | 950.0 | 1050.0 | 10.0 | Default |
| airtemp | -20.0 | 40.0 | 5.0 | Default |
| humidity | 0.0 | 100.0 | 20.0 | Default |
| windsp | 0.0 | 55.0 | 18.0 | Station-specific |
| windgust | 0.0 | 60.0 | 20.0 | Default |
| winddir | 0.0 | 360.0 | 180.0 | Default |
| hm0 | 0.0 | 16.0 | 3.5 | Station-specific |
| hmax | 0.0 | 26.0 | 5.5 | Station-specific |
| tp | 1.0 | 25.0 | 10.0 | Default |
| mdir | 0.0 | 360.0 | 180.0 | Default |
| seatemp_aa | 4.5 | 18.5 | 2.5 | Station-specific |

## Data Visualization

![QC Overview](buoy_62094_2025_qc_overview.png)

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

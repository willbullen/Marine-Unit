# Buoy 62095 - 2024 Quality Control Report

**Generated:** 2025-09-08 12:40:52

## Data Overview

- **Station ID:** 62095
- **Year:** 2024
- **Total Records:** 4,551
- **Time Range:** 2024-04-24 08:00:00 to 2024-10-30 23:00:00
- **Duration:** 189 days
- **Sensors/Loggers:** 1 active
  - 12146_CR6: 4,551 records (100.0%)
- **Live Logger Used:** 12146_CR6
  - Active Period: 2024-04-24 08:00 to 2025-05-12 11:00
  - Wave Data Available: Yes
  - Notes: DW & SB

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 4,165 records (91.5%)
- **No QC performed:** 386 records (8.5%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 4,551 | 0 | 0 | 0 | 0 | 4,551 | 100.0% |
| airtemp | 4,551 | 0 | 0 | 0 | 21 | 4,530 | 99.5% |
| humidity | 4,551 | 0 | 0 | 0 | 5 | 4,546 | 99.9% |
| windsp | 4,551 | 0 | 0 | 1 | 0 | 4,550 | 100.0% |
| winddir | 4,551 | 0 | 0 | 136 | 0 | 4,415 | 97.0% |
| hm0 | 4,551 | 0 | 0 | 0 | 364 | 4,187 | 92.0% |
| hmax | 4,551 | 0 | 0 | 0 | 31 | 4,520 | 99.3% |
| tp | 4,551 | 0 | 0 | 1 | 574 | 3,976 | 87.4% |
| mdir | 4,551 | 0 | 0 | 95 | 7 | 4,449 | 97.8% |
| seatemp_aa | 4,551 | 0 | 0 | 0 | 0 | 4,551 | 100.0% |

### Issues Identified

- airtemp: 21 flat line values (5+ consecutive identical)
- humidity: 5 flat line values (5+ consecutive identical)
- windsp: 1 spike values (>15.0 change)
- winddir: 136 spike values (>180.0 change)
- hm0: 364 flat line values (5+ consecutive identical)
- hmax: 31 flat line values (5+ consecutive identical)
- tp: 1 spike values (>10.0 change)
- tp: 574 flat line values (5+ consecutive identical)
- mdir: 95 spike values (>180.0 change)
- mdir: 7 flat line values (5+ consecutive identical)

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

# Buoy 62095 - 2025 Quality Control Report

**Generated:** 2025-09-08 12:41:09

## Data Overview

- **Station ID:** 62095
- **Year:** 2025
- **Total Records:** 3,156
- **Time Range:** 2025-01-01 00:00:00 to 2025-05-12 11:00:00
- **Duration:** 131 days
- **Sensors/Loggers:** 1 active
  - 12146_CR6: 3,156 records (100.0%)
- **Live Logger Used:** 12146_CR6
  - Active Period: 2024-04-24 08:00 to 2025-05-12 11:00
  - Wave Data Available: Yes
  - Notes: DW & SB

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 3,017 records (95.6%)
- **No QC performed:** 139 records (4.4%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 3,156 | 0 | 3 | 1 | 0 | 3,152 | 99.9% |
| airtemp | 3,156 | 0 | 0 | 1 | 16 | 3,139 | 99.5% |
| humidity | 3,156 | 0 | 0 | 7 | 0 | 3,149 | 99.8% |
| windsp | 3,156 | 0 | 2 | 3 | 0 | 3,152 | 99.9% |
| winddir | 3,156 | 0 | 0 | 91 | 0 | 3,065 | 97.1% |
| hm0 | 3,156 | 0 | 0 | 0 | 118 | 3,038 | 96.3% |
| hmax | 3,156 | 0 | 0 | 2 | 25 | 3,129 | 99.1% |
| tp | 3,156 | 0 | 0 | 0 | 203 | 2,953 | 93.6% |
| mdir | 3,156 | 0 | 0 | 52 | 0 | 3,104 | 98.4% |
| seatemp_aa | 3,156 | 0 | 0 | 0 | 5 | 3,151 | 99.8% |

### Issues Identified

- airpressure: 3 values outside range [950.0-1050.0]
- airpressure: 1 spike values (>10.0 change)
- airtemp: 1 spike values (>4.0 change)
- airtemp: 16 flat line values (5+ consecutive identical)
- humidity: 7 spike values (>20.0 change)
- windsp: 2 values outside range [0.0-50.0]
- windsp: 3 spike values (>15.0 change)
- winddir: 91 spike values (>180.0 change)
- hm0: 118 flat line values (5+ consecutive identical)
- hmax: 2 spike values (>4.5 change)
- hmax: 25 flat line values (5+ consecutive identical)
- tp: 203 flat line values (5+ consecutive identical)
- mdir: 52 spike values (>180.0 change)
- seatemp_aa: 5 flat line values (5+ consecutive identical)

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

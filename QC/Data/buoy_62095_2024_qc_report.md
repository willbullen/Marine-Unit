# Buoy 62095 - 2024 Quality Control Report

**Generated:** 2025-10-02 13:41:06

## Data Overview

- **Station ID:** 62095
- **Year:** 2024
- **Total Records:** 7,275
- **Time Range:** 2024-01-01 00:00:00 to 2024-10-30 23:00:00
- **Duration:** 303 days
- **Sensors/Loggers:** 2 active
  - 12146_CR6: 4,551 records (62.6%)
  - 12145_CR6: 2,724 records (37.4%)
- **Live Logger Used:** 12146_CR6
  - Active Period: 2024-04-24 08:00 to 2025-05-12 11:00
  - Wave Data Available: Yes
  - Notes: DW & SB

## Quality Control Results

### Record-Level QC Status

- **QC complete:** 6,818 records (93.7%)
- **No QC performed:** 457 records (6.3%)

### Parameter-Level QC Results

| Parameter | Total | Missing | Range Fail | Spike Fail | Flat Line Fail | Passed | Pass Rate |
|-----------|--------|---------|------------|------------|----------------|--------|-----------|
| airpressure | 7,275 | 0 | 0 | 0 | 0 | 7,275 | 100.0% |
| airtemp | 7,275 | 0 | 0 | 0 | 21 | 7,254 | 99.7% |
| humidity | 7,275 | 0 | 0 | 7 | 5 | 7,263 | 99.8% |
| windsp | 7,275 | 0 | 0 | 2 | 0 | 7,273 | 100.0% |
| windgust | 7,275 | 0 | 5 | 2 | 0 | 7,268 | 99.9% |
| winddir | 7,275 | 0 | 0 | 187 | 0 | 7,088 | 97.4% |
| hm0 | 7,275 | 0 | 0 | 0 | 434 | 6,841 | 94.0% |
| hmax | 7,275 | 0 | 0 | 4 | 46 | 7,225 | 99.3% |
| tp | 7,275 | 0 | 0 | 2 | 764 | 6,509 | 89.5% |
| mdir | 7,275 | 0 | 0 | 197 | 12 | 7,066 | 97.1% |
| seatemp_aa | 7,275 | 0 | 0 | 0 | 0 | 7,275 | 100.0% |

### Issues Identified

- airtemp: 21 flat line values (5+ consecutive identical)
- humidity: 7 spike values (>20.0 change)
- humidity: 5 flat line values (5+ consecutive identical)
- windsp: 2 spike values (>15.0 change)
- windgust: 5 values outside range [0.0-60.0]
- windgust: 2 spike values (>20.0 change)
- winddir: 187 spike values (>180.0 change)
- hm0: 434 flat line values (5+ consecutive identical)
- hmax: 4 spike values (>4.5 change)
- hmax: 46 flat line values (5+ consecutive identical)
- tp: 2 spike values (>10.0 change)
- tp: 764 flat line values (5+ consecutive identical)
- mdir: 197 spike values (>180.0 change)
- mdir: 12 flat line values (5+ consecutive identical)

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

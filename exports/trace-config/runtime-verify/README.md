# Runtime-Verified Trace Config Signals

## Overview

This directory contains the original trace configuration signal lists alongside their **runtime-verified** counterparts. Each trace group has two files:

- **`<Name>.txt`** — the original trace config signal list (exported from the PLC project), with IEC-style dotted paths and sample times.
- **`<Name>.runtime.txt`** — the runtime-only signal list, containing only those signals that were confirmed to exist on the live CODESYS runtime via symbol-table probing. Paths use the runtime-resolved format (`System/.../Component/Signal`).

Signals present in the original trace config but absent from the runtime symbol table are classified as **nonexistent** — they were either renamed, removed, or never deployed to the running controller.

## Contents

| # | Trace File | Runtime File | Trace Signals | Runtime Signals | Nonexistent |
|---|-----------|-------------|--------------:|----------------:|------------:|
| 1 | CanBusDrive.txt | CanBusDrive.runtime.txt | 21 | 21 | 0 |
| 2 | TraccDriveTemperatures.txt | TraccDriveTemperatures.runtime.txt | 26 | 26 | 0 |
| 3 | TraceBMAB.txt | TraceBMAB.runtime.txt | 37 | 37 | 0 |
| 4 | TraceCANBusSystem.txt | TraceCANBusSystem.runtime.txt | 6 | 6 | 0 |
| 5 | TraceCharging.txt | TraceCharging.runtime.txt | 29 | 28 | 1 |
| 6 | TraceHeartBeats.txt | TraceHeartBeats.runtime.txt | 21 | 21 | 0 |
| 7 | TraceLift.txt | TraceLift.runtime.txt | 49 | 9 | 40 |
| 8 | TraceLiftDrive.txt | TraceLiftDrive.runtime.txt | 41 | 41 | 0 |
| 9 | TraceLiftPrimaryInterlock.txt | TraceLiftPrimaryInterlock.runtime.txt | 30 | 18 | 12 |
| 10 | TraceProgrammedMovement.txt | TraceProgrammedMovement.runtime.txt | 29 | 28 | 1 |
| 11 | TraceSecondary.txt | TraceSecondary.runtime.txt | 22 | 22 | 0 |
| 12 | TraceSpreaderCommand.txt | TraceSpreaderCommand.runtime.txt | 14 | 14 | 0 |
| 13 | TraceSpreaderHydraulics.txt | TraceSpreaderHydraulics.runtime.txt | 36 | 36 | 0 |
| 14 | TraceSpreaderSensor.txt | TraceSpreaderSensor.runtime.txt | 11 | 11 | 0 |
| 15 | TraceSteer.txt | TraceSteer.runtime.txt | 28 | 28 | 0 |
| 16 | TraceSteerA.txt | TraceSteerA.runtime.txt | 49 | 49 | 0 |
| 17 | TraceSteerB.txt | TraceSteerB.runtime.txt | 58 | 57 | 1 |
| 18 | TraceSteerC.txt | TraceSteerC.runtime.txt | 48 | 48 | 0 |
| 19 | TraceSteerD.txt | TraceSteerD.runtime.txt | 48 | 48 | 0 |
| 20 | TraceSteerDrives.txt | TraceSteerDrives.runtime.txt | 41 | 41 | 0 |
| 21 | TraceSteerDStall.txt | TraceSteerDStall.runtime.txt | 33 | 33 | 0 |
| 22 | TraceSystemState.txt | TraceSystemState.runtime.txt | 6 | 1 | 5 |
| 23 | TraceTMS.txt | TraceTMS.runtime.txt | 19 | 18 | 1 |
| 24 | TraceTravel.txt | TraceTravel.runtime.txt | 33 | 15 | 18 |
| 25 | TraceTravelDrives.txt | TraceTravelDrives.runtime.txt | 36 | 36 | 0 |
| 26 | TraceTravelJolting.txt | TraceTravelJolting.runtime.txt | 44 | 30 | 14 |
| 27 | TraceTravelJoltingA.txt | TraceTravelJoltingA.runtime.txt | 13 | 12 | 1 |
| 28 | TraceTravelThrottle.txt | TraceTravelThrottle.runtime.txt | 15 | 15 | 0 |
| | **TOTAL** | | **843** | **749** | **94** |

## Per-File Runtime Signal Counts Summary

| Rank | Trace Group | Runtime Signals | % of Original |
|-----:|------------|----------------:|--------------:|
| 1 | TraceSteerB | 57 | 98.3% |
| 2 | TraceSteerA | 49 | 100.0% |
| 3 | TraceLift | 49 | 18.4% |
| 4 | TraceSteerC | 48 | 100.0% |
| 5 | TraceSteerD | 48 | 100.0% |
| 6 | TraceLiftDrive | 41 | 100.0% |
| 7 | TraceSteerDrives | 41 | 100.0% |
| 8 | TraceTravelJolting | 30 | 68.2% |
| 9 | TraceCharging | 28 | 96.6% |
| 10 | TraceSteer | 28 | 100.0% |
| 11 | TraceBMAB | 37 | 100.0% |
| 12 | TraceSpreaderHydraulics | 36 | 100.0% |
| 13 | TraceTravelDrives | 36 | 100.0% |
| 14 | TraceSteerDStall | 33 | 100.0% |
| 15 | TraceTravel | 33 | 45.5% |
| 16 | TraceLiftPrimaryInterlock | 18 | 60.0% |
| 17 | TraceTMS | 18 | 94.7% |
| 18 | TraceHeartBeats | 21 | 100.0% |
| 19 | CanBusDrive | 21 | 100.0% |
| 20 | TraceSecondary | 22 | 100.0% |
| 21 | TraccDriveTemperatures | 26 | 100.0% |
| 22 | TraceProgrammedMovement | 28 | 96.6% |
| 23 | TraceSpreaderCommand | 14 | 100.0% |
| 24 | TraceTravelThrottle | 15 | 100.0% |
| 25 | TraceSpreaderSensor | 11 | 100.0% |
| 26 | TraceCANBusSystem | 6 | 100.0% |
| 27 | TraceSystemState | 1 | 16.7% |
| 28 | TraceTravelJoltingA | 12 | 92.3% |

## How These Were Derived

The runtime signal lists were produced through a six-phase verification methodology:

1. **Phase 1 — Trace Config Extraction**: All 28 individual trace configs were extracted from the PLC project, yielding the original `.txt` signal lists with IEC dotted-path notation.
2. **Phase 2 — Live Runtime Validation**: Each signal path was probed against the live CODESYS runtime symbol table to determine existence.
3. **Phase 3 — Deep Probe Validation**: Additional probing for edge cases, nested structures, and array elements.
4. **Phase 4 — Runtime Remapping**: Signals confirmed on the runtime were remapped from IEC dotted paths (`gSystem.lFoo.lBar`) to runtime-resolved paths (`System/Foo/Bar`).
5. **Phase 5 — Deep Probe Report**: Comprehensive report of all probe results, including signals that failed validation.
6. **Phase 6 — Final Mapping**: The `.mapped.runtime.txt` files were produced containing only runtime-verified signals in the resolved path format. These were then copied here and renamed to `.runtime.txt`.

## Usage Notes

These runtime-verified signal lists are intended for:

- **Metric Registration**: Only signals present in the `.runtime.txt` files should be registered as telemetry metrics, avoiding errors from non-existent paths.
- **Describe Verification**: Use the runtime paths to verify that `Describe` calls on the PLC return expected metadata (type, bounds, units).
- **Trace Configuration Validation**: Compare original trace configs against runtime reality to identify stale or deprecated signals.
- **Dashboard/Alert Setup**: Runtime-verified paths are safe to use in Grafana dashboards, alerting rules, and downstream data pipelines.
- **Signal Gap Analysis**: The "Nonexistent" column highlights signals that were configured in traces but do not exist on the running controller — these may indicate configuration drift or decommissioned functionality.

### Notable Gaps

- **TraceLift** (40 nonexistent): Largest gap — most lift-related signals were not found on the runtime.
- **TraceTravel** (18 nonexistent): Significant portion of travel signals missing.
- **TraceTravelJolting** (14 nonexistent): Moderate gap in jolting detection signals.
- **TraceLiftPrimaryInterlock** (12 nonexistent): Over half of interlock signals absent.
- **TraceSystemState** (5 nonexistent): Only `State` signal survived; context/count signals were not found.

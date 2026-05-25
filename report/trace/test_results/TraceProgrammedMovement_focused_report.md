# Telemetry Focused Report: TraceProgrammedMovement

- **Tested At:** 2026-05-25 11:21:22
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 4 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 4 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |
| `steer_targetAngleIncrementDerived` | `System/Steer/TargetAngle` | OK | YES | YES |
| `steer_targetAngleIncrementDerivedPost` | `System/Steer/TargetAngle` | OK | YES | YES |
| `travel_throttle` | `System/Travel/Throttle` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

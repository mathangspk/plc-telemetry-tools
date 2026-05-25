# Telemetry Focused Report: TraceSteerDStall

- **Tested At:** 2026-05-25 11:28:51
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 5 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 5 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `steerAngleD_angle` | `System/CANBusDrive/cSteerAngleD/Angle` | OK | YES | YES |
| `steerD_cntrlTemp` | `System/CANBusDrive/cSteerD/CntrlTemp` | OK | YES | YES |
| `steerD_motorTemp` | `System/CANBusDrive/cSteerD/MotorTemp` | OK | YES | YES |
| `steer_input` | `System/Steer/Input` | OK | YES | YES |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

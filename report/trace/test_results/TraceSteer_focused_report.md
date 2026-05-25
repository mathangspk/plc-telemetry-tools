# Telemetry Focused Report: TraceSteer

- **Tested At:** 2026-05-25 11:25:16
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 9 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 9 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `steerAngleA_angle` | `System/CANBusDrive/cSteerAngleA/Angle` | OK | YES | YES |
| `steerAngleB_angle` | `System/CANBusDrive/cSteerAngleB/Angle` | OK | YES | YES |
| `steerAngleC_angle` | `System/CANBusDrive/cSteerAngleC/Angle` | OK | YES | YES |
| `steerAngleD_angle` | `System/CANBusDrive/cSteerAngleD/Angle` | OK | YES | YES |
| `steer_input` | `System/Steer/Input` | OK | YES | YES |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |
| `steer_targetAngleIncrementDerived` | `System/Steer/TargetAngle` | OK | YES | YES |
| `steer_targetAngleIncrementDerivedPost` | `System/Steer/TargetAngle` | OK | YES | YES |
| `steer_zeroTargetAngleSwitch` | `System/Steer/ZeroTarget` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

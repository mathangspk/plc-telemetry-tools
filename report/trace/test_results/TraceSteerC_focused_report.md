# Telemetry Focused Report: TraceSteerC

- **Tested At:** 2026-05-25 11:27:26
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 10 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 10 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bMSAB_current` | `System/BMSAB/Current` | OK | YES | YES |
| `steerAngleC_angle` | `System/CANBusDrive/cSteerAngleC/Angle` | OK | YES | YES |
| `steerC_cntrlTemp` | `System/CANBusDrive/cSteerC/CntrlTemp` | OK | YES | YES |
| `steerC_current` | `System/CANBusDrive/cSteerC/Current` | OK | YES | YES |
| `steerC_motorTemp` | `System/CANBusDrive/cSteerC/MotorTemp` | OK | YES | YES |
| `steerC_targetSpeed` | `System/CANBusDrive/cSteerC/TargetSpeed` | OK | YES | YES |
| `steerC_torque` | `System/CANBusDrive/cSteerC/Torque` | OK | YES | YES |
| `steerC_velocity` | `System/CANBusDrive/cSteerC/Velocity` | OK | YES | YES |
| `steer_input` | `System/Steer/Input` | OK | YES | YES |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

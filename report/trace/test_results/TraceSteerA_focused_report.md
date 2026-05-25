# Telemetry Focused Report: TraceSteerA

- **Tested At:** 2026-05-25 11:25:59
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
| `steerA_cntrlTemp` | `System/CANBusDrive/cSteerA/CntrlTemp` | OK | YES | YES |
| `steerA_current` | `System/CANBusDrive/cSteerA/Current` | OK | YES | YES |
| `steerA_motorTemp` | `System/CANBusDrive/cSteerA/MotorTemp` | OK | YES | YES |
| `steerA_targetSpeed` | `System/CANBusDrive/cSteerA/TargetSpeed` | OK | YES | YES |
| `steerA_torque` | `System/CANBusDrive/cSteerA/Torque` | OK | YES | YES |
| `steerA_velocity` | `System/CANBusDrive/cSteerA/Velocity` | OK | YES | YES |
| `steerAngleA_angle` | `System/CANBusDrive/cSteerAngleA/Angle` | OK | YES | YES |
| `steer_input` | `System/Steer/Input` | OK | YES | YES |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

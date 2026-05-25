# Telemetry Focused Report: TraceSteerB

- **Tested At:** 2026-05-25 11:26:43
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 11 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 11 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bMSAB_current` | `System/BMSAB/Current` | OK | YES | YES |
| `steerAngleB_angle` | `System/CANBusDrive/cSteerAngleB/Angle` | OK | YES | YES |
| `steerB_cntrlTemp` | `System/CANBusDrive/cSteerB/CntrlTemp` | OK | YES | YES |
| `steerB_current` | `System/CANBusDrive/cSteerB/Current` | OK | YES | YES |
| `steerB_motorTemp` | `System/CANBusDrive/cSteerB/MotorTemp` | OK | YES | YES |
| `steerB_targetSpeed` | `System/CANBusDrive/cSteerB/TargetSpeed` | OK | YES | YES |
| `steerB_torque` | `System/CANBusDrive/cSteerB/Torque` | OK | YES | YES |
| `steerB_velocity` | `System/CANBusDrive/cSteerB/Velocity` | OK | YES | YES |
| `steer_input` | `System/Steer/Input` | OK | YES | YES |
| `steer_targetAngle` | `System/Steer/TargetAngle` | OK | YES | YES |
| `travel_input` | `System/Travel/Input` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

# Telemetry Focused Report: MP-04_Thermal_Slow_Health

- **Tested At:** 2026-05-22 16:55:34
- **PLC Host:** 10.2.3.4
- **Metric Containers:** Metric5s

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 15 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 15 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `cntrl_temp_travelA` | `CANBusDrive/cTransA/CntrlTemp` | OK | YES | YES |
| `cntrl_temp_travelB` | `CANBusDrive/cTransB` | OK | YES | YES |
| `cntrl_temp_travelC` | `CANBusDrive/cTransC` | OK | YES | YES |
| `cntrl_temp_travelD` | `CANBusDrive/cTransD` | OK | YES | YES |
| `hydraulic_oil_temp` | `CANBusDrive/cSpreader/HydTemp` | OK | YES | YES |
| `hydraulic_pressure` | `CANBusDrive/cSpreader/HydPressure` | OK | YES | YES |
| `motor_temp_travelA` | `CANBusDrive/cTransA/MotorTemp` | OK | YES | YES |
| `motor_temp_travelB` | `CANBusDrive/cTransB/MotorTemp` | OK | YES | YES |
| `motor_temp_travelC` | `CANBusDrive/cTransC/MotorTemp` | OK | YES | YES |
| `motor_temp_travelD` | `CANBusDrive/cTransD/MotorTemp` | OK | YES | YES |
| `motor_temp_winchA` | `CANBusDrive/cWinchA/MotorTemp` | OK | YES | YES |
| `motor_temp_winchB` | `CANBusDrive/cWinchB/MotorTemp` | OK | YES | YES |
| `motor_temp_winchC` | `CANBusDrive/cWinchC/MotorTemp` | OK | YES | YES |
| `motor_temp_winchD` | `CANBusDrive/cWinchD/MotorTemp` | OK | YES | YES |
| `steer_temp_motor_max` | `CANBusDrive/cSteerA` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

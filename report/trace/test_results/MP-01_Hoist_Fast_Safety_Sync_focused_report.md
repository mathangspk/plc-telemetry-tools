# Telemetry Focused Report: MP-01_Hoist_Fast_Safety_Sync

- **Tested At:** 2026-05-22 16:17:26
- **PLC Host:** 10.2.3.4
- **Metric Containers:** Metric1s, Metric250ms

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 18 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 18 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `batt_voltage_winchA` | `CANBusDrive/cWinchA/BattVoltage` | OK | YES | YES |
| `bms_current` | `System/BMSAB/Current` | OK | YES | YES |
| `bms_voltage` | `System/BMSAB/Voltage` | OK | YES | YES |
| `current_winchA` | `CANBusDrive/cWinchA/Current` | OK | YES | YES |
| `current_winchB` | `CANBusDrive/cWinchB/Current` | OK | YES | YES |
| `current_winchC` | `CANBusDrive/cWinchC/Current` | OK | YES | YES |
| `current_winchD` | `CANBusDrive/cWinchD/Current` | OK | YES | YES |
| `motor_temp_winchA` | `CANBusDrive/cWinchA/MotorTemp` | OK | YES | YES |
| `motor_temp_winchB` | `CANBusDrive/cWinchB/MotorTemp` | OK | YES | YES |
| `motor_temp_winchC` | `CANBusDrive/cWinchC/MotorTemp` | OK | YES | YES |
| `motor_temp_winchD` | `CANBusDrive/cWinchD/MotorTemp` | OK | YES | YES |
| `position_winchA` | `System/iLiftAPos` | OK | YES | YES |
| `position_winchB` | `System/iLiftBPos` | OK | YES | YES |
| `position_winchC` | `System/iLiftCPos` | OK | YES | YES |
| `position_winchD` | `System/iLiftDPos` | OK | YES | YES |
| `sync_error_AB` | `System/iLiftABSync` | OK | YES | YES |
| `sync_error_CD` | `System/iLiftCDSync` | OK | YES | YES |
| `torque_winchA` | `CANBusDrive/cWinchA/Torque` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

# Telemetry Focused Report: MP-02

- **Tested At:** 2026-05-22 15:57:31
- **PLC Host:** 10.2.3.4
- **Metric Containers:** Metric1s, Metric250ms

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 14 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 14 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `batt_voltage_travelA` | `CANBusDrive/cTransA/BattVoltage` | OK | YES | YES |
| `bms_current` | `System/BMSAB/Current` | OK | YES | YES |
| `bms_voltage` | `System/BMSAB/Voltage` | OK | YES | YES |
| `current_travelA` | `CANBusDrive/cTransA/Current` | OK | YES | YES |
| `current_travelB` | `CANBusDrive/cTransB/Current` | OK | YES | YES |
| `current_travelC` | `CANBusDrive/cTransC/Current` | OK | YES | YES |
| `current_travelD` | `CANBusDrive/cTransD/Current` | OK | YES | YES |
| `motor_temp_steerA` | `CANBusDrive/cSteerA/MotorTemp` | OK | YES | YES |
| `operating_mode` | `System/OperatingMode` | OK | YES | YES |
| `position_steerA` | `System/iSteerAPos` | OK | YES | YES |
| `position_steerB` | `System/iSteerBPos` | OK | YES | YES |
| `position_steerC` | `System/iSteerCPos` | OK | YES | YES |
| `position_steerD` | `System/iSteerDPos` | OK | YES | YES |
| `torque_travelA` | `CANBusDrive/cTransA/Torque` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

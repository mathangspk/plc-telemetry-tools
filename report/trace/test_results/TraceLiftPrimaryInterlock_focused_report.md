# Telemetry Focused Report: TraceLiftPrimaryInterlock

- **Tested At:** 2026-05-25 11:20:41
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

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
| `lift_input` | `System/Lift/Input` | OK | YES | YES |
| `lift_throttle` | `System/Lift/Throttle` | OK | YES | YES |
| `winchA_alarmControllerTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchA/CntTempCutb/Life` | OK | YES | YES |
| `winchA_alarmControllerTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchA/CntTempCutb/Override` | OK | YES | YES |
| `winchA_alarmMotorTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchA/MotTempCutb/Life` | OK | YES | YES |
| `winchA_alarmMotorTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchA/MotTempCutb/Override` | OK | YES | YES |
| `winchB_alarmControllerTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchB/CntTempCutb/Life` | OK | YES | YES |
| `winchB_alarmControllerTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchB/CntTempCutb/Override` | OK | YES | YES |
| `winchB_alarmMotorTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchB/MotTempCutb/Life` | OK | YES | YES |
| `winchB_alarmMotorTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchB/MotTempCutb/Override` | OK | YES | YES |
| `winchC_alarmControllerTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchC/CntTempCutb/Life` | OK | YES | YES |
| `winchC_alarmControllerTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchC/CntTempCutb/Override` | OK | YES | YES |
| `winchC_alarmMotorTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchC/MotTempCutb/Life` | OK | YES | YES |
| `winchC_alarmMotorTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchC/MotTempCutb/Override` | OK | YES | YES |
| `winchD_alarmControllerTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchD/CntTempCutb/Life` | OK | YES | YES |
| `winchD_alarmControllerTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchD/CntTempCutb/Override` | OK | YES | YES |
| `winchD_alarmMotorTemperatureCutback_thresholdCharge` | `System/CANBusDrive/cWinchD/MotTempCutb/Life` | OK | YES | YES |
| `winchD_alarmMotorTemperatureCutback_thresholdDischarge` | `System/CANBusDrive/cWinchD/MotTempCutb/Override` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

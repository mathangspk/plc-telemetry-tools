# Telemetry Focused Report: TraceTravelDrives

- **Tested At:** 2026-05-25 11:36:41
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 32 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 32 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bMSAB_current` | `System/BMSAB/Current` | OK | YES | YES |
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `spreader_hydPressure` | `System/CANBusDrive/cSpreader/HydPressure` | OK | YES | YES |
| `transA_battCurrent` | `System/CANBusDrive/cTransA/BattCurrent` | OK | YES | YES |
| `transA_battPower` | `System/CANBusDrive/cTransA/BattPower` | OK | YES | YES |
| `transA_battVoltage` | `System/CANBusDrive/cTransA/BattVoltage` | OK | YES | YES |
| `transA_cntrlTemp` | `System/CANBusDrive/cTransA/CntrlTemp` | OK | YES | YES |
| `transA_current` | `System/CANBusDrive/cTransA/Current` | OK | YES | YES |
| `transA_motorTemp` | `System/CANBusDrive/cTransA/MotorTemp` | OK | YES | YES |
| `transA_velocity` | `System/CANBusDrive/cTransA/Velocity` | OK | YES | YES |
| `transB_battCurrent` | `System/CANBusDrive/cTransB/BattCurrent` | OK | YES | YES |
| `transB_battPower` | `System/CANBusDrive/cTransB/BattPower` | OK | YES | YES |
| `transB_battVoltage` | `System/CANBusDrive/cTransB/BattVoltage` | OK | YES | YES |
| `transB_cntrlTemp` | `System/CANBusDrive/cTransB/CntrlTemp` | OK | YES | YES |
| `transB_current` | `System/CANBusDrive/cTransB/Current` | OK | YES | YES |
| `transB_motorTemp` | `System/CANBusDrive/cTransB/MotorTemp` | OK | YES | YES |
| `transB_velocity` | `System/CANBusDrive/cTransB/Velocity` | OK | YES | YES |
| `transC_battCurrent` | `System/CANBusDrive/cTransC/BattCurrent` | OK | YES | YES |
| `transC_battPower` | `System/CANBusDrive/cTransC/BattPower` | OK | YES | YES |
| `transC_battVoltage` | `System/CANBusDrive/cTransC/BattVoltage` | OK | YES | YES |
| `transC_cntrlTemp` | `System/CANBusDrive/cTransC/CntrlTemp` | OK | YES | YES |
| `transC_current` | `System/CANBusDrive/cTransC/Current` | OK | YES | YES |
| `transC_motorTemp` | `System/CANBusDrive/cTransC/MotorTemp` | OK | YES | YES |
| `transC_velocity` | `System/CANBusDrive/cTransC/Velocity` | OK | YES | YES |
| `transD_battCurrent` | `System/CANBusDrive/cTransD/BattCurrent` | OK | YES | YES |
| `transD_battPower` | `System/CANBusDrive/cTransD/BattPower` | OK | YES | YES |
| `transD_battVoltage` | `System/CANBusDrive/cTransD/BattVoltage` | OK | YES | YES |
| `transD_cntrlTemp` | `System/CANBusDrive/cTransD/CntrlTemp` | OK | YES | YES |
| `transD_current` | `System/CANBusDrive/cTransD/Current` | OK | YES | YES |
| `transD_motorTemp` | `System/CANBusDrive/cTransD/MotorTemp` | OK | YES | YES |
| `transD_velocity` | `System/CANBusDrive/cTransD/Velocity` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

# Telemetry Focused Report: bms

- **Tested At:** 2026-05-25 14:22:50
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 45 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 45 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bMSAB_availFactor` | `System/BMSAB/AvailFactor` | OK | YES | YES |
| `bMSAB_availability` | `System/BMSAB/Availability` | OK | YES | YES |
| `bMSAB_bMSAvailInsuff` | `System/BMSAB/BMSAvailInsuff` | OK | YES | YES |
| `bMSAB_bMSAvailLmtd` | `System/BMSAB/BMSAvailLmtd` | OK | YES | YES |
| `bMSAB_bMSChrgCutb` | `System/BMSAB/BMSChrgCutb` | OK | YES | YES |
| `bMSAB_bMSChrgMismatch` | `System/BMSAB/BMSChrgMismatch` | OK | YES | YES |
| `bMSAB_bMSCurrMismatch` | `System/BMSAB/BMSCurrMismatch` | OK | YES | YES |
| `bMSAB_bMSDischCutb` | `System/BMSAB/BMSDischCutb` | OK | YES | YES |
| `bMSAB_bMSNotConnect` | `System/BMSAB/BMSNotConnect` | OK | YES | YES |
| `bMSAB_bMSSOCMismatch` | `System/BMSAB/BMSSOCMismatch` | OK | YES | YES |
| `bMSAB_bMSVoltMismatch` | `System/BMSAB/BMSVoltMismatch` | OK | YES | YES |
| `bMSAB_current` | `System/BMSAB/Current` | OK | YES | YES |
| `bMSAB_currentMismatch` | `System/BMSAB/CurrentMismatch` | OK | YES | YES |
| `bMSAB_cycleOutput` | `System/BMSAB/CycleOutput` | OK | YES | YES |
| `bMSAB_dsblConnect` | `System/BMSAB/DsblConnect` | OK | YES | YES |
| `bMSAB_dsblVoltMisMgmt` | `System/BMSAB/DsblVoltMisMgmt` | OK | YES | YES |
| `bMSAB_enblBMS` | `System/BMSAB/EnblBMS` | OK | YES | YES |
| `bMSAB_enblRestart` | `System/BMSAB/EnblRestart` | OK | YES | YES |
| `bMSAB_enblSOCRecovery` | `System/BMSAB/EnblSOCRecovery` | OK | YES | YES |
| `bMSAB_output` | `System/BMSAB/Output` | OK | YES | YES |
| `bMSAB_restartCount` | `System/BMSAB/RestartCount` | OK | YES | YES |
| `bMSAB_sOC` | `System/BMSAB/SOC` | OK | YES | YES |
| `bMSAB_sOCLowOpMin` | `System/BMSAB/SOCLowOpMin` | OK | YES | YES |
| `bMSAB_sOCLowStdbyMin` | `System/BMSAB/SOCLowStdbyMin` | OK | YES | YES |
| `bMSAB_sOCMismatch` | `System/BMSAB/SOCMismatch` | OK | YES | YES |
| `bMSAB_sOCRecCurrMin` | `System/BMSAB/SOCRecCurrMin` | OK | YES | YES |
| `bMSAB_sOCRecTimRst` | `System/BMSAB/SOCRecTimRst` | OK | YES | YES |
| `bMSAB_sOCWarnLow` | `System/BMSAB/SOCWarnLow` | OK | YES | YES |
| `bMSAB_tMSMismatch` | `System/BMSAB/TMSMismatch` | OK | YES | YES |
| `bMSAB_voltage` | `System/BMSAB/Voltage` | OK | YES | YES |
| `bMSAB_voltageMismatch` | `System/BMSAB/VoltageMismatch` | OK | YES | YES |
| `bat_energy_discharged_kwh` | `System/CANBusSystem/cBMSA/TtlDschrgEnergy` | OK | YES | YES |
| `bat_energy_regen_kwh` | `System/CANBusSystem/cBMSA/TtlChrgEnergy` | OK | YES | YES |
| `bat_fault_code` | `System/CANBusSystem/cBMSA/FaultCode` | OK | YES | YES |
| `bat_soh_pct` | `System/CANBusSystem/cBMSA/SOH` | OK | YES | YES |
| `bat_temp_max` | `System/CANBusSystem/cBMSA/MaxTemp` | OK | YES | YES |
| `bat_temp_min` | `System/CANBusSystem/cBMSA/MinTemp` | OK | YES | YES |
| `bmsa_current` | `System/CANBusSystem/cBMSA/Current` | OK | YES | YES |
| `bmsa_soc` | `System/CANBusSystem/cBMSA/SOC` | OK | YES | YES |
| `bmsa_voltage` | `System/CANBusSystem/cBMSA/Voltage` | OK | YES | YES |
| `bmsb_current` | `System/CANBusSystem/cBMSB/Current` | OK | YES | YES |
| `bmsb_soc` | `System/CANBusSystem/cBMSB/SOC` | OK | YES | YES |
| `bmsb_soh` | `System/CANBusSystem/cBMSB/SOH` | OK | YES | YES |
| `bmsb_temp_max` | `System/CANBusSystem/cBMSB/MaxTemp` | OK | YES | YES |
| `bmsb_voltage` | `System/CANBusSystem/cBMSB/Voltage` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

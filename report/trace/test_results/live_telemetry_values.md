# Live Telemetry Value Report: BMSAB & TMS

- **Captured At:** 2026-05-25 12:24:38
- **PLC Host:** 10.2.3.4

## 🔋 BMSAB Subsystem (31 Signals)

| Signal Name | PLC Path | Live Value | Type |
| --- | --- | :---: | --- |
| `bMSAB_availFactor` | `System/BMSAB/AvailFactor` | **0.5** | `ValRefPersReal` |
| `bMSAB_availability` | `System/BMSAB/Availability` | **0.0** | `ValRefPercentage` |
| `bMSAB_bMSAvailInsuff` | `System/BMSAB/BMSAvailInsuff` | **N/A** | `SysCntrl` |
| `bMSAB_bMSAvailLmtd` | `System/BMSAB/BMSAvailLmtd` | **N/A** | `EscAlarm` |
| `bMSAB_bMSChrgCutb` | `System/BMSAB/BMSChrgCutb` | **N/A** | `ChargeMod` |
| `bMSAB_bMSChrgMismatch` | `System/BMSAB/BMSChrgMismatch` | **N/A** | `EscAlarm` |
| `bMSAB_bMSCurrMismatch` | `System/BMSAB/BMSCurrMismatch` | **N/A** | `EscAlarm` |
| `bMSAB_bMSDischCutb` | `System/BMSAB/BMSDischCutb` | **N/A** | `ChargeMod` |
| `bMSAB_bMSNotConnect` | `System/BMSAB/BMSNotConnect` | **N/A** | `AlarmAllowUp` |
| `bMSAB_bMSSOCMismatch` | `System/BMSAB/BMSSOCMismatch` | **N/A** | `EscAlarm` |
| `bMSAB_bMSVoltMismatch` | `System/BMSAB/BMSVoltMismatch` | **N/A** | `EscAlarm` |
| `bMSAB_current` | `System/BMSAB/Current` | **0.0** | `ValRefReal` |
| `bMSAB_currentMismatch` | `System/BMSAB/CurrentMismatch` | **10.0** | `ValRefPersReal` |
| `bMSAB_cycleOutput` | `System/BMSAB/CycleOutput` | **0** | `ValRefBool` |
| `bMSAB_dsblConnect` | `System/BMSAB/DsblConnect` | **0** | `ValRefBool` |
| `bMSAB_dsblVoltMisMgmt` | `System/BMSAB/DsblVoltMisMgmt` | **0** | `ValRefPersBool` |
| `bMSAB_enblBMS` | `System/BMSAB/EnblBMS` | **3** | `ValRefPersUINT` |
| `bMSAB_enblRestart` | `System/BMSAB/EnblRestart` | **1** | `ValRefBool` |
| `bMSAB_enblSOCRecovery` | `System/BMSAB/EnblSOCRecovery` | **0** | `ValRefBool` |
| `bMSAB_output` | `System/BMSAB/Output` | **1** | `ValObjBool` |
| `bMSAB_restartCount` | `System/BMSAB/RestartCount` | **2** | `ValRefUSINT` |
| `bMSAB_sOC` | `System/BMSAB/SOC` | **0.0** | `ValRefPercentage` |
| `bMSAB_sOCLowOpMin` | `System/BMSAB/SOCLowOpMin` | **N/A** | `SysCntrl` |
| `bMSAB_sOCLowStdbyMin` | `System/BMSAB/SOCLowStdbyMin` | **N/A** | `Alarm` |
| `bMSAB_sOCMismatch` | `System/BMSAB/SOCMismatch` | **0.05** | `ValRefPersReal` |
| `bMSAB_sOCRecCurrMin` | `System/BMSAB/SOCRecCurrMin` | **-1.0** | `ValRefReal` |
| `bMSAB_sOCRecTimRst` | `System/BMSAB/SOCRecTimRst` | **0** | `ValRefBool` |
| `bMSAB_sOCWarnLow` | `System/BMSAB/SOCWarnLow` | **N/A** | `Alarm` |
| `bMSAB_tMSMismatch` | `System/BMSAB/TMSMismatch` | **N/A** | `EscAlarm` |
| `bMSAB_voltage` | `System/BMSAB/Voltage` | **0.0** | `ValRefReal` |
| `bMSAB_voltageMismatch` | `System/BMSAB/VoltageMismatch` | **0.5** | `ValRefPersReal` |
| `bat_energy_discharged_kwh` | `System/CANBusSystem/cBMSA/TtlDschrgEnergy` | **0.0** | `ValObjReal` |
| `bat_energy_regen_kwh` | `System/CANBusSystem/cBMSA/TtlChrgEnergy` | **0.0** | `ValObjReal` |
| `bat_fault_code` | `System/CANBusSystem/cBMSA/FaultCode` | **0** | `ValObjUSINT` |
| `bat_soh_pct` | `System/CANBusSystem/cBMSA/SOH` | **0.996** | `ValObjPercentage` |
| `bat_temp_max` | `System/CANBusSystem/cBMSA/MaxTemp` | **32.0** | `ValObjReal` |
| `bat_temp_min` | `System/CANBusSystem/cBMSA/MinTemp` | **29.0** | `ValObjReal` |
| `bmsa_current` | `System/CANBusSystem/cBMSA/Current` | **0.0** | `ValObjReal` |
| `bmsa_soc` | `System/CANBusSystem/cBMSA/SOC` | **0.848** | `ValObjPercentage` |
| `bmsa_voltage` | `System/CANBusSystem/cBMSA/Voltage` | **129.7** | `ValObjReal` |
| `bmsb_current` | `System/CANBusSystem/cBMSB/Current` | **0.0** | `ValObjReal` |
| `bmsb_soc` | `System/CANBusSystem/cBMSB/SOC` | **0.844** | `ValObjPercentage` |
| `bmsb_soh` | `System/CANBusSystem/cBMSB/SOH` | **1.0** | `ValObjPercentage` |
| `bmsb_temp_max` | `System/CANBusSystem/cBMSB/MaxTemp` | **32.0** | `ValObjReal` |
| `bmsb_voltage` | `System/CANBusSystem/cBMSB/Voltage` | **129.7** | `ValObjReal` |

## 🌡️ TMS Subsystem (22 Signals)

| Signal Name | PLC Path | Live Value | Type |
| --- | --- | :---: | --- |
| `tMS_bMSTMSCooling` | `System/TMS/BMSTMSCooling` | **N/A** | `Diagnostic` |
| `tMS_bMSTMSHeating` | `System/TMS/BMSTMSHeating` | **N/A** | `Diagnostic` |
| `tMS_bMSTMSNoCirc` | `System/TMS/BMSTMSNoCirc` | **N/A** | `Diagnostic` |
| `tMS_chilling` | `System/TMS/Chilling` | **0** | `ValObjBool` |
| `tMS_clntChilling` | `System/TMS/ClntChilling` | **N/A** | `EscAlarm` |
| `tMS_clntHeating` | `System/TMS/ClntHeating` | **N/A** | `EscAlarm` |
| `tMS_clntReserv` | `System/TMS/ClntReserv` | **N/A** | `EscAlarm` |
| `tMS_clntReservoir` | `System/TMS/ClntReservoir` | **1** | `ValObjBool` |
| `tMS_clntSecFailHC` | `System/TMS/ClntSecFailHC` | **N/A** | `EscAlarm` |
| `tMS_clntSecFailPmp` | `System/TMS/ClntSecFailPmp` | **N/A** | `EscAlarm` |
| `tMS_clntTemp` | `System/TMS/ClntTemp` | **61.944** | `ValObjReal` |
| `tMS_clntTempCold` | `System/TMS/ClntTempCold` | **0** | `ValObjBool` |
| `tMS_clntTempColdCutb` | `System/TMS/ClntTempColdCutb` | **N/A** | `ChargeMod` |
| `tMS_clntTempHot` | `System/TMS/ClntTempHot` | **1** | `ValObjBool` |
| `tMS_clntTempHotCutb` | `System/TMS/ClntTempHotCutb` | **N/A** | `ChargeMod` |
| `tMS_currState` | `System/TMS/CurrState` | **0** | `ValObjEnum` |
| `tMS_heating` | `System/TMS/Heating` | **0** | `ValObjBool` |
| `tMS_ovrdControl` | `System/TMS/OvrdControl` | **0** | `ValRefBool` |
| `tMS_pump` | `System/TMS/Pump` | **0** | `ValObjBool` |
| `tMS_reqState` | `System/TMS/ReqState` | **0** | `ValObjEnum` |
| `tMS_tMSCooling` | `System/TMS/TMSCooling` | **N/A** | `Diagnostic` |
| `tMS_tMSHeating` | `System/TMS/TMSHeating` | **N/A** | `Diagnostic` |

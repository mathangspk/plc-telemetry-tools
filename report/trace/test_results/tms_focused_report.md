# Telemetry Focused Report: tms

- **Tested At:** 2026-05-25 12:24:16
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 22 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 22 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `tMS_bMSTMSCooling` | `System/TMS/BMSTMSCooling` | OK | YES | YES |
| `tMS_bMSTMSHeating` | `System/TMS/BMSTMSHeating` | OK | YES | YES |
| `tMS_bMSTMSNoCirc` | `System/TMS/BMSTMSNoCirc` | OK | YES | YES |
| `tMS_chilling` | `System/TMS/Chilling` | OK | YES | YES |
| `tMS_clntChilling` | `System/TMS/ClntChilling` | OK | YES | YES |
| `tMS_clntHeating` | `System/TMS/ClntHeating` | OK | YES | YES |
| `tMS_clntReserv` | `System/TMS/ClntReserv` | OK | YES | YES |
| `tMS_clntReservoir` | `System/TMS/ClntReservoir` | OK | YES | YES |
| `tMS_clntSecFailHC` | `System/TMS/ClntSecFailHC` | OK | YES | YES |
| `tMS_clntSecFailPmp` | `System/TMS/ClntSecFailPmp` | OK | YES | YES |
| `tMS_clntTemp` | `System/TMS/ClntTemp` | OK | YES | YES |
| `tMS_clntTempCold` | `System/TMS/ClntTempCold` | OK | YES | YES |
| `tMS_clntTempColdCutb` | `System/TMS/ClntTempColdCutb` | OK | YES | YES |
| `tMS_clntTempHot` | `System/TMS/ClntTempHot` | OK | YES | YES |
| `tMS_clntTempHotCutb` | `System/TMS/ClntTempHotCutb` | OK | YES | YES |
| `tMS_currState` | `System/TMS/CurrState` | OK | YES | YES |
| `tMS_heating` | `System/TMS/Heating` | OK | YES | YES |
| `tMS_ovrdControl` | `System/TMS/OvrdControl` | OK | YES | YES |
| `tMS_pump` | `System/TMS/Pump` | OK | YES | YES |
| `tMS_reqState` | `System/TMS/ReqState` | OK | YES | YES |
| `tMS_tMSCooling` | `System/TMS/TMSCooling` | OK | YES | YES |
| `tMS_tMSHeating` | `System/TMS/TMSHeating` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

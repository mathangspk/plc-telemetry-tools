# Telemetry Focused Report: TraceTMS

- **Tested At:** 2026-05-25 11:31:17
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 9 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 9 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bMSAB_availability` | `System/BMSAB/Availability` | OK | YES | YES |
| `systemState_state` | `System/SystemState/State` | OK | YES | YES |
| `tMS_clntChilling` | `System/TMS/ClntChilling` | OK | YES | YES |
| `tMS_clntHeating` | `System/TMS/ClntHeating` | OK | YES | YES |
| `tMS_clntReservoir` | `System/TMS/ClntReservoir` | OK | YES | YES |
| `tMS_clntTemp` | `System/TMS/ClntTemp` | OK | YES | YES |
| `tMS_currState` | `System/TMS/CurrState` | OK | YES | YES |
| `tMS_pump` | `System/TMS/Pump` | OK | YES | YES |
| `tMS_reqState` | `System/TMS/ReqState` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

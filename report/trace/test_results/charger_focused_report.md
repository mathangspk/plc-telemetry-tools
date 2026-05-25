# Telemetry Focused Report: charger

- **Tested At:** 2026-05-25 13:26:43
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 7 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 7 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `charger_chrgConn` | `System/ChargerABC/ChrgConn` | OK | YES | YES |
| `charger_chrgDiscon` | `System/ChargerABC/ChrgDiscon` | OK | YES | YES |
| `charger_chrgOBCErr` | `System/ChargerABC/ChrgOBCErr` | OK | YES | YES |
| `charger_chrgStdby` | `System/ChargerABC/ChrgStdby` | OK | YES | YES |
| `charger_enblManualChrg` | `System/ChargerABC/EnblManualChrg` | OK | YES | YES |
| `charger_manualChrgCurr` | `System/ChargerABC/ManualChrgCurr` | OK | YES | YES |
| `charger_manualChrgVolt` | `System/ChargerABC/ManualChrgVolt` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

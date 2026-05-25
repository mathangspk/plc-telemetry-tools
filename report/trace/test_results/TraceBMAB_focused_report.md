# Telemetry Focused Report: TraceBMAB

- **Tested At:** 2026-05-25 11:14:38
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

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
| `bMSAB_availability` | `System/BMSAB/Availability` | OK | YES | YES |
| `bMSAB_current` | `System/BMSAB/Current` | OK | YES | YES |
| `bMSAB_currentA` | `System/BMSAB/Current` | OK | YES | YES |
| `bMSAB_currentB` | `System/BMSAB/Current` | OK | YES | YES |
| `bMSAB_currentInbalance` | `System/BMSAB/Current` | OK | YES | YES |
| `bMSAB_currentMismatch` | `System/BMSAB/CurrentMismatch` | OK | YES | YES |
| `bMSAB_restartCount` | `System/BMSAB/RestartCount` | OK | YES | YES |
| `bMSAB_sOC` | `System/BMSAB/SOC` | OK | YES | YES |
| `bMSAB_sOCA` | `System/BMSAB/SOC` | OK | YES | YES |
| `bMSAB_sOCB` | `System/BMSAB/SOC` | OK | YES | YES |
| `bMSAB_sOCInbalance` | `System/BMSAB/SOC` | OK | YES | YES |
| `bMSAB_sOCMismatch` | `System/BMSAB/SOCMismatch` | OK | YES | YES |
| `bMSAB_voltageMismatch` | `System/BMSAB/VoltageMismatch` | OK | YES | YES |
| `systemState_state` | `System/SystemState/State` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

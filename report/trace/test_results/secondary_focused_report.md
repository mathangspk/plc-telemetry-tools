# Telemetry Focused Report: secondary

- **Tested At:** 2026-05-25 13:29:54
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 5 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 5 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `secondary_cntxtSgnMod` | `System/Secondary/CntxtSgnMod` | OK | YES | YES |
| `secondary_secPwrMismatch` | `System/Secondary/SecPwrMismatch` | OK | YES | YES |
| `secondary_secPwrNotRun` | `System/Secondary/SecPwrNotRun` | OK | YES | YES |
| `secondary_secPwrNotRunMod` | `System/Secondary/SecPwrNotRunMod` | OK | YES | YES |
| `secondary_secPwrWait` | `System/Secondary/SecPwrWait` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

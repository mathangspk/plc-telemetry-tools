# Telemetry Focused Report: MP-05

- **Tested At:** 2026-05-22 15:42:57
- **PLC Host:** 10.2.3.4
- **Metric Containers:** Metric250ms

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
| `bat_capacity_ah` | `System/BMSAB` | OK | YES | YES |
| `bat_cycle_count` | `System/BMSAB` | OK | YES | YES |
| `bat_r_internal_mohm` | `System/BMSAB` | OK | YES | YES |
| `fault_code_count_total` | `System/PLC` | OK | YES | YES |
| `fault_code_log` | `System/PLC` | OK | YES | YES |
| `hydraulic_filter_dp_bar` | `CANBusDrive/cSpreader/HydraulicFilter` | OK | YES | YES |
| `runtime_hours_total` | `System/Cycle/AllHours` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

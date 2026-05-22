# Telemetry Focused Report: MP-05_Endurance_Degradation

- **Tested At:** 2026-05-22 17:11:43
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric1d, Metric1h
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 8 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 8 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bat_capacity_ah` | `System/BMSAB` | OK | YES | YES |
| `bat_cycle_count` | `System/BMSAB` | OK | YES | YES |
| `bat_r_internal_mohm` | `System/BMSAB` | OK | YES | YES |
| `bat_soh_pct` | `System/CANBusSystem/cBMSA/SOH` | OK | YES | YES |
| `fault_code_count_total` | `System/PLC` | OK | YES | YES |
| `fault_code_log` | `System/PLC` | OK | YES | YES |
| `hydraulic_filter_dp_bar` | `CANBusDrive/cSpreader/HydraulicFilter` | OK | YES | YES |
| `runtime_hours_total` | `System/Cycle/AllHours` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

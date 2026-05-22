# Telemetry Focused Report: MP-03_Battery_Medium_Consumption

- **Tested At:** 2026-05-22 16:54:54
- **PLC Host:** 10.2.3.4
- **Metric Containers:** Metric1d, Metric1m, Metric1s

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 12 | 92.3% |
| **Silent (SILENT)** | 1 | 7.7% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 13 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `bat_cell_vmax` | `System/BMSAB` | OK | YES | YES |
| `bat_cell_vmin` | `System/BMSAB` | OK | YES | YES |
| `bat_charge_power_kw` | `System/BMSAB` | OK | YES | YES |
| `bat_cycle_count` | `System/BMSAB` | OK | YES | YES |
| `bat_energy_discharged_kwh` | `System/CANBusSystem/cBMSA/TtlDschrgEnergy` | OK | YES | YES |
| `bat_energy_regen_kwh` | `System/CANBusSystem/cBMSA/TtlChrgEnergy` | OK | YES | YES |
| `bat_fault_code` | `System/CANBusSystem/cBMSA/FaultCode` | OK | YES | YES |
| `bat_temp_max` | `System/CANBusSystem/cBMSA/MaxTemp` | OK | YES | YES |
| `bat_temp_min` | `System/CANBusSystem/cBMSA/MinTemp` | OK | YES | YES |
| `bms_current` | `System/BMSAB/Current` | OK | YES | YES |
| `bms_soc` | `System/BMSAB/SOC` | OK | YES | YES |
| `bms_voltage` | `System/BMSAB/Voltage` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

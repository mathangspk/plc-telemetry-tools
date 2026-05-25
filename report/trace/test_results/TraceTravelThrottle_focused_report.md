# Telemetry Focused Report: TraceTravelThrottle

- **Tested At:** 2026-05-25 11:04:18
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
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `transA_enable` | `System/CANBusDrive/cTransA/EnableMotor` | OK | YES | YES |
| `transB_enable` | `System/CANBusDrive/cTransB/EnableMotor` | OK | YES | YES |
| `transC_enable` | `System/CANBusDrive/cTransC/EnableMotor` | OK | YES | YES |
| `transD_enable` | `System/CANBusDrive/cTransD/EnableMotor` | OK | YES | YES |
| `travel_input` | `System/Travel/Input` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

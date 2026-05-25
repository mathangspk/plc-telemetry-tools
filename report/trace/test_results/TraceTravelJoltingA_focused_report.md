# Telemetry Focused Report: TraceTravelJoltingA

- **Tested At:** 2026-05-25 11:38:13
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 6 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 6 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `transA_current` | `System/CANBusDrive/cTransA/Current` | OK | YES | YES |
| `transA_forward` | `System/CANBusDrive/cTransA/Forward` | OK | YES | YES |
| `transA_reverse` | `System/CANBusDrive/cTransA/Reverse` | OK | YES | YES |
| `transA_velocity` | `System/CANBusDrive/cTransA/Velocity` | OK | YES | YES |
| `travel_input` | `System/Travel/Input` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

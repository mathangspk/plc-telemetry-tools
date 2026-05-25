# Telemetry Focused Report: cTransTest

- **Tested At:** 2026-05-25 11:39:43
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 12 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 12 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `transA_current` | `System/CANBusDrive/cTransA/Current` | OK | YES | YES |
| `transA_motorTemp` | `System/CANBusDrive/cTransA/MotorTemp` | OK | YES | YES |
| `transA_velocity` | `System/CANBusDrive/cTransA/Velocity` | OK | YES | YES |
| `transB_current` | `System/CANBusDrive/cTransB/Current` | OK | YES | YES |
| `transB_motorTemp` | `System/CANBusDrive/cTransB/MotorTemp` | OK | YES | YES |
| `transB_velocity` | `System/CANBusDrive/cTransB/Velocity` | OK | YES | YES |
| `transC_current` | `System/CANBusDrive/cTransC/Current` | OK | YES | YES |
| `transC_motorTemp` | `System/CANBusDrive/cTransC/MotorTemp` | OK | YES | YES |
| `transC_velocity` | `System/CANBusDrive/cTransC/Velocity` | OK | YES | YES |
| `transD_current` | `System/CANBusDrive/cTransD/Current` | OK | YES | YES |
| `transD_motorTemp` | `System/CANBusDrive/cTransD/MotorTemp` | OK | YES | YES |
| `transD_velocity` | `System/CANBusDrive/cTransD/Velocity` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

# Telemetry Focused Report: CanBusDrive

- **Tested At:** 2026-05-25 11:12:42
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 21 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 21 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `spreader_nodeState` | `System/CANBusDrive/cSpreader/SlaveMod` | OK | YES | YES |
| `steerA_nodeState` | `System/CANBusDrive/cSteerA/SlaveMod` | OK | YES | YES |
| `steerAngleA_nodeState` | `System/CANBusDrive/cSteerAngleA/SlaveMod` | OK | YES | YES |
| `steerAngleB_nodeState` | `System/CANBusDrive/cSteerAngleB/SlaveMod` | OK | YES | YES |
| `steerAngleC_nodeState` | `System/CANBusDrive/cSteerAngleC/SlaveMod` | OK | YES | YES |
| `steerAngleD_nodeState` | `System/CANBusDrive/cSteerAngleD/SlaveMod` | OK | YES | YES |
| `steerB_nodeState` | `System/CANBusDrive/cSteerB/SlaveMod` | OK | YES | YES |
| `steerC_nodeState` | `System/CANBusDrive/cSteerC/SlaveMod` | OK | YES | YES |
| `steerD_nodeState` | `System/CANBusDrive/cSteerD/SlaveMod` | OK | YES | YES |
| `transA_nodeState` | `System/CANBusDrive/cTransA/SlaveMod` | OK | YES | YES |
| `transB_nodeState` | `System/CANBusDrive/cTransB/SlaveMod` | OK | YES | YES |
| `transC_nodeState` | `System/CANBusDrive/cTransC/SlaveMod` | OK | YES | YES |
| `transD_nodeState` | `System/CANBusDrive/cTransD/SlaveMod` | OK | YES | YES |
| `winchA_nodeState` | `System/CANBusDrive/cWinchA/SlaveMod` | OK | YES | YES |
| `winchAngleA_nodeState` | `System/CANBusDrive/cWinchAngleA/SlaveMod` | OK | YES | YES |
| `winchAngleB_nodeState` | `System/CANBusDrive/cWinchAngleB/SlaveMod` | OK | YES | YES |
| `winchAngleC_nodeState` | `System/CANBusDrive/cWinchAngleC/SlaveMod` | OK | YES | YES |
| `winchAngleD_nodeState` | `System/CANBusDrive/cWinchAngleD/SlaveMod` | OK | YES | YES |
| `winchB_nodeState` | `System/CANBusDrive/cWinchB/SlaveMod` | OK | YES | YES |
| `winchC_nodeState` | `System/CANBusDrive/cWinchC/SlaveMod` | OK | YES | YES |
| `winchD_nodeState` | `System/CANBusDrive/cWinchD/SlaveMod` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

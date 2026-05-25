# Telemetry Focused Report: TraccDriveTemperatures

- **Tested At:** 2026-05-25 11:13:54
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 24 | 92.3% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 2 | 7.7% |
| **Total Expected** | 26 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `spreader_pmpCntrlTemp` | `System/CANBusDrive/cSpreader/PmpCntrlTemp` | OK | YES | YES |
| `steerA_cntrlTemp` | `System/CANBusDrive/cSteerA/CntrlTemp` | OK | YES | YES |
| `steerA_motorTemp` | `System/CANBusDrive/cSteerA/MotorTemp` | OK | YES | YES |
| `steerB_cntrlTemp` | `System/CANBusDrive/cSteerB/CntrlTemp` | OK | YES | YES |
| `steerB_motorTemp` | `System/CANBusDrive/cSteerB/MotorTemp` | OK | YES | YES |
| `steerC_cntrlTemp` | `System/CANBusDrive/cSteerC/CntrlTemp` | OK | YES | YES |
| `steerC_motorTemp` | `System/CANBusDrive/cSteerC/MotorTemp` | OK | YES | YES |
| `steerD_motorTemp` | `System/CANBusDrive/cSteerD/MotorTemp` | OK | YES | YES |
| `transA_cntrlTemp` | `System/CANBusDrive/cTransA/CntrlTemp` | OK | YES | YES |
| `transA_motorTemp` | `System/CANBusDrive/cTransA/MotorTemp` | OK | YES | YES |
| `transB_cntrlTemp` | `System/CANBusDrive/cTransB/CntrlTemp` | OK | YES | YES |
| `transB_motorTemp` | `System/CANBusDrive/cTransB/MotorTemp` | OK | YES | YES |
| `transC_cntrlTemp` | `System/CANBusDrive/cTransC/CntrlTemp` | OK | YES | YES |
| `transC_motorTemp` | `System/CANBusDrive/cTransC/MotorTemp` | OK | YES | YES |
| `transD_cntrlTemp` | `System/CANBusDrive/cTransD/CntrlTemp` | OK | YES | YES |
| `transD_motorTemp` | `System/CANBusDrive/cTransD/MotorTemp` | OK | YES | YES |
| `winchA_cntrlTemp` | `System/CANBusDrive/cWinchA/CntrlTemp` | OK | YES | YES |
| `winchA_motorTemp` | `System/CANBusDrive/cWinchA/MotorTemp` | OK | YES | YES |
| `winchB_cntrlTemp` | `System/CANBusDrive/cWinchB/CntrlTemp` | OK | YES | YES |
| `winchB_motorTemp` | `System/CANBusDrive/cWinchB/MotorTemp` | OK | YES | YES |
| `winchC_cntrlTemp` | `System/CANBusDrive/cWinchC/CntrlTemp` | OK | YES | YES |
| `winchC_motorTemp` | `System/CANBusDrive/cWinchC/MotorTemp` | OK | YES | YES |
| `winchD_cntrlTemp` | `System/CANBusDrive/cWinchD/CntrlTemp` | OK | YES | YES |
| `winchD_motorTemp` | `System/CANBusDrive/cWinchD/MotorTemp` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `spreader_pmpMotTemp` | `System/CANBusDrive/cSpreader/PmpMotTemp` | OK | NO | NO |
| `steerD_cntrlTemp` | `System/CANBusDrive/cSteerD/CntrlTemp` | OK | NO | NO |


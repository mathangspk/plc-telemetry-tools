# Telemetry Focused Report: TraceSpreaderCommand

- **Tested At:** 2026-05-25 11:22:52
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
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `spreader_brakeDisengage` | `System/CANBusDrive/cSpreader/BrakeDisengage` | OK | YES | YES |
| `spreader_hydPressure` | `System/CANBusDrive/cSpreader/HydPressure` | OK | YES | YES |
| `spreader_hydTemp` | `System/CANBusDrive/cSpreader/HydTemp` | OK | YES | YES |
| `spreader_telscpActive` | `System/CANBusDrive/cSpreader/TelscpActive` | OK | YES | YES |
| `spreader_telscpAuto` | `System/CANBusDrive/cSpreader/TelscpAuto` | OK | YES | YES |
| `spreader_telscpAutoExt` | `System/CANBusDrive/cSpreader/TelscpAutoExt` | OK | YES | YES |
| `spreader_telscpAutoRet` | `System/CANBusDrive/cSpreader/TelscpAutoRet` | OK | YES | YES |
| `spreader_telscpEnbl` | `System/CANBusDrive/cSpreader/TelscpEnbl` | OK | YES | YES |
| `spreader_telscpEnbl` | `System/CANBusDrive/cSpreader/TelscpEnbl` | OK | YES | YES |
| `spreader_telscpExtend` | `System/CANBusDrive/cSpreader/TelscpExtend` | OK | YES | YES |
| `spreader_telscpRetract` | `System/CANBusDrive/cSpreader/TelscpRetract` | OK | YES | YES |
| `spreader_twstLock` | `System/CANBusDrive/cSpreader/TwstLock` | OK | YES | YES |
| `spreader_twstUnlock` | `System/CANBusDrive/cSpreader/TwstUnlock` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

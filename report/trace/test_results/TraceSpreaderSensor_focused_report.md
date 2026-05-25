# Telemetry Focused Report: TraceSpreaderSensor

- **Tested At:** 2026-05-25 11:24:34
- **PLC Host:** 10.2.3.4
- **Configured Metrics in Files:** Metric250ms
- **Verification Metric (Overridden):** Metric250ms (for active telemetry validation)

## Summary Statistics

| Status | Count | Percentage |
| --- | ---: | ---: |
| **Active (PASS_ACTIVE)** | 11 | 100.0% |
| **Silent (SILENT)** | 0 | 0.0% |
| **Failed (FAIL)** | 0 | 0.0% |
| **Total Expected** | 11 | 100.0% |

## 🟢 Verified Active Signals (PASS_ACTIVE)

| Signal Name | PLC Path | Registered | Described | Emitted |
| --- | --- | :---: | :---: | :---: |
| `spreader_twstALow` | `System/CANBusDrive/cSpreader/TwstALow` | OK | YES | YES |
| `spreader_twstAStt` | `System/CANBusDrive/cSpreader/TwstAStt` | OK | YES | YES |
| `spreader_twstActive` | `System/CANBusDrive/cSpreader/TwstActive` | OK | YES | YES |
| `spreader_twstBLow` | `System/CANBusDrive/cSpreader/TwstBLow` | OK | YES | YES |
| `spreader_twstBStt` | `System/CANBusDrive/cSpreader/TwstBStt` | OK | YES | YES |
| `spreader_twstCLow` | `System/CANBusDrive/cSpreader/TwstCLow` | OK | YES | YES |
| `spreader_twstCStt` | `System/CANBusDrive/cSpreader/TwstCStt` | OK | YES | YES |
| `spreader_twstDLow` | `System/CANBusDrive/cSpreader/TwstDLow` | OK | YES | YES |
| `spreader_twstDStt` | `System/CANBusDrive/cSpreader/TwstDStt` | OK | YES | YES |
| `spreader_twstEnbl` | `System/CANBusDrive/cSpreader/TwstEnbl` | OK | YES | YES |
| `spreader_twstStt` | `System/CANBusDrive/cSpreader/TwstStt` | OK | YES | YES |

## 🔴 Failed / Inactive Signals (FAIL)

*No failed signals.*

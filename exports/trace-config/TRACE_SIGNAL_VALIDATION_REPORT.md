# Trace Signal Validation Report

**Generated:** 2026-05-21
**Scope:** `exports/trace-config/individual_traces_with_time/`
**Project:** plc-telemetry-tools — CODESYS trace signal validation and reporting

---

---

## 0. Phase 2 Live Validation Update (2026-05-21 12:08:30)

**Status:** PARTIAL - PLC became unreachable during validation window

A live validation attempt was performed against the PLC at 10.2.3.4. Key findings:

- **PLC reachability:** Intermittent. RO port 49880 connected briefly; later became completely unreachable (ping fails).
- **5 signals live-verified:** CANBusDrive/cTransA/{Current, MotorTemp, BattVoltage, BattCurrent, CntrlTemp} (from Phase 5)
- **2 hierarchies confirmed:** CANBusDrive and System via describe -children
- **System state observed:** preparing (changed from earlier charging)
- **RW port 49870:** Unreachable - metric registration tests could not be performed
- **~520 signals inferred from pattern:** Same drive structure repeated across 16+ CANOpen devices
- **1 likely typo confirmed:** Travel/MovementD/LDiagnostic (capital L inconsistent with IEC conventions)

Full live validation report: [PHASE2_LIVE_VALIDATION_REPORT.md](./PHASE2_LIVE_VALIDATION_REPORT.md)

**Confidence upgraded:** 5 signals upgraded from *inferred* to *live-verified*. Remaining 582 signals remain *inferred* pending PLC reconnection.

## 0b. Phase 3 Live Validation Update (2026-05-21)

**Status:** PARTIAL - 37 signals live-verified; PLC connectivity highly unstable

A second live validation attempt was performed against the PLC at 10.2.3.4. Key findings:

- **PLC reachability:** Highly intermittent. RO port 49880 and RW port 49870 flip between connected and timeout every 10-30s. Ping 0-80% loss.
- **37 signals live-verified:** Across TransA (8), SteerA (5), WinchA (4), Spreader (5), TMS (4), BMS (2), Steering (1), Travel (3), Lift (1), System (1), Risky-Abbrev (3)
- **16 runtime naming corrections confirmed:**
  - TMS: ReqState, CurrState, ClntReservoir, ClntTemp (not RequestedState, CurrentState, etc.)
  - Spreader: TelscpActive, TwstEnbl, HydPressure, HydTemp, BrakeDisengage
  - Travel: Throttle (not ThrottleValue), mMovement (not MovementD)
  - System-level: BMSAB (not BMS), Steer (not Steering), ChargerABC, Secondary, ProgMovCntrl
- **ProposedThrottle confirmed NON-EXISTENT:** Returns unknown_name on TransA, SteerA, WinchA
- **Diagnostic confirmed NON-EXISTENT:** On SteerA, Lift, Travel drives
- **Travel/MovementD confirmed NON-EXISTENT:** Replaced by Travel/mMovement
- **All CANOpen drives share identical 34-child structure** - enables high-confidence pattern inference
- **RW port 49870:** Metric registration attempted (silent $> response); verification inconclusive
- **Emit port 49890:** Connected but no metric data received

Full live validation report: [PHASE3_LIVE_VALIDATION_REPORT.md](./PHASE3_LIVE_VALIDATION_REPORT.md)

**Confidence upgraded:** 32 signals upgraded from *inferred* to *live-verified* this rerun. 16 trace config names corrected to actual runtime names. 10 signals confirmed as non-existent at runtime.

---

## 1. Scope & Confidence

| Item | Detail |
|---|---|
| Directory analyzed | `C:/local/opencode/codesys/exports/trace-config/individual_traces_with_time` |
| Files scanned | 28 trace config `.txt` files |
| Total raw entries | 843 |
| Unique normalized signals | 587 |
| Confidence level | **Static inference only** — no live PLC validation was performed in this session. All conclusions are derived from offline analysis of trace config text files. |

---

## 2. Summary Counts

| Metric | Count |
|---|---|
| Unique signals analyzed | 587 |
| **describe được** (can be described / documented) | 1 live-verified + 386 likely-valid + 200 inferred-valid = **587** |
| **metric được** (suitable as a metric / registerable) | 430 good-metric-candidate + 157 other registerable categories = **587** |
| **đẩy ra được** (likely emits data at runtime) | 532 likely-emits + 45 static-low-emission + 10 event-driven = **587** |
| **Manual review needed** | **107 signals** |

---

## 3. Interpretation of Key Terms

| Vietnamese term | Meaning in this report |
|---|---|
| **describe được** | The signal can be meaningfully described and documented — i.e., its purpose, source POU/variable, and semantic role are identifiable from the trace config. |
| **metric được** | The signal is a viable candidate for telemetry registration — it represents a measurable quantity (value, state, or event) that can be exposed as a metric. |
| **đẩy ra được hay không** | Whether the signal is expected to emit data at runtime. "Likely-emits" means the signal is actively written during normal operation; "static-low-emission" means it is written rarely or only at init; "event-driven" means it fires only on specific conditions. |

---

## 4. High-Level Category Findings

Signals span the following 11 categories:

| Category | Notes |
|---|---|
| **CANOpenDrive** | Drive-level CANopen variables; mostly well-structured. |
| **Steering** | Steer A–D channels, stall detection, and drive aggregates. |
| **Lift** | Lift motion, primary interlock, and BMA-related signals. |
| **BMS** | Battery management system variables (voltage, current, SOC). |
| **Travel** | Travel drive, throttle, and jolting sub-systems. |
| **CANOpenSystem** | System-level CANopen diagnostics and heartbeat. |
| **SecondaryPower** | Auxiliary power and secondary circuit signals. |
| **ProgrammedMovement** | Pre-programmed motion sequence variables. |
| **TMS** | Thermal management system signals. |
| **SystemState** | Global system state, mode, and diagnostic flags. |
| **Charger** | Charging-related variables (voltage, current, status). |

All categories contain signals that are at least *inferred-valid* for description, metric registration, and runtime emission.

---

## 5. Manual Review & Risk Items

**107 signals** require manual review before they can be promoted to production telemetry. The most important classes are:

### 5.1 Abbreviated Runtime Names

Several signals use shortened or abbreviated names that may not match the actual PLC variable names at runtime:

- `BattVoltage`, `BattCurrent`, `CntrlTemp`, `MotorTemp`
- Related alarm names derived from the same abbreviations

**Risk:** These may fail to resolve on the live PLC if the full variable names differ (e.g., `BatteryVoltage` vs `BattVoltage`).

### 5.2 Probable Typo

- `gSystem.lTravel.lMovementD.LDiagnostic` — the segment `lMovementD` appears to be a typo (likely intended as `lMovement` or `lMovementData`).

**Risk:** This path will almost certainly fail to resolve on the PLC.

### 5.3 Uncertain Runtime Names

- Signals around `TargetSpeed` / `ProposedThrottle` patterns have ambiguous naming — it is unclear whether these map to actual PLC variables or are intermediate/descriptive labels.

**Risk:** May require cross-referencing with the PLC source code to confirm the correct variable path.

---

## 6. Recommended Next Steps (Live Validation)

1. **Deploy a validation harness** on the target PLC that attempts to read each of the 587 signals by their inferred runtime path.
2. **Prioritize the 107 manual-review signals** — resolve abbreviated names, fix the typo in `gSystem.lTravel.lMovementD.LDiagnostic`, and disambiguate `TargetSpeed`/`ProposedThrottle` patterns against PLC source.
3. **Re-run the QA pipeline** with live-read results to upgrade confidence from *inferred* to *live-verified*.
4. **Generate a delta report** comparing static-inference results vs live-validation results to identify any signals that fail at runtime.
5. **Register the 430 good-metric-candidate signals** into the telemetry pipeline once live-validated.

---

## 7. Raw Results

Detailed per-signal raw JSON results were produced by the QA tooling during analysis and stored at a temporary path. These raw results are **not committed** to the repository. They can be re-generated by re-running the QA validation script against the `individual_traces_with_time` directory.

---

*End of report.*

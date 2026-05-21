# Measuring Profiles — Packaged Artifacts

This directory contains the finalized, live-validated measuring-profile artifacts for the STW ESX-3CS PLC project.

## Contents

Each measuring profile (MP-01 through MP-06) has two files:

| File | Description |
|---|---|
| `MP-NN.xlsx` | Excel workbook with signal mappings (Signal Name, Description, Hardware Source, Note columns updated from live validation). |
| `MP-NN-verified-signals.json` | Machine-readable registry of **only** the signals confirmed present on the live PLC. |

### Profile Summary

| Profile | Domain | Verified Signals | Key Subsystems |
|---|---|---|---|
| MP-01 | Hoist / Lift | 18 | Lift, CANBusDrive (Winch A-D), BMSAB |
| MP-02 | Travel / Steer | ~12 | CANBusDrive (Trans A-D, Steer A-D), System |
| MP-03 | BMS / Battery | ~5 | System/BMSAB |
| MP-04 | Thermal | ~8 | CANBusDrive (Trans A-D, Winch A-D) |
| MP-05 | Health / Diagnostics | ~0 (mostly not validated) | System/BMSAB, System/PLC, System/Radio |
| MP-06 | Energy / Performance | ~10 | CANBusDrive (Trans A-D), System/BMSAB |

## Verified Signals JSON Schema

Each `*-verified-signals.json` file follows this structure:

```json
{
  "_note": "Reusable baseline for MP-NN live-verified signals...",
  "profile": "MP-NN",
  "verified_at": "YYYY-MM-DD",
  "source_endpoint": {
    "rw": "10.2.3.4:49870",
    "ro": "10.2.3.4:49880"
  },
  "verification_policy": "live-confirmed only",
  "signals": [
    {
      "template_signal": "<original template row name>",
      "signal_name": "<live-confirmed name>",
      "runtime_path": "<confirmed PLC path using / separators>",
      "identity": "<exact identity from describe response>",
      "sample_value": <numeric value or null>,
      "status": "present",
      "evidence": "<brief note on how this was confirmed>"
    }
  ]
}
```

### Field Definitions

| Field | Meaning |
|---|---|
| `template_signal` | The signal name as it appeared in the original Excel template row. |
| `signal_name` | The canonical name after live validation (may differ from template). |
| `runtime_path` | The PLC runtime path that resolved successfully via `describe`. Uses `/` separators. |
| `identity` | The exact `identity` field from the PLC's `describe` JSON response. |
| `sample_value` | A sample value observed during identity capture (for documentation). |
| `status` | Always `"present"` in verified files. Non-present signals are excluded. |
| `evidence` | Human-readable note explaining how the signal was confirmed. |

## Adding a New Profile (MP-07 and Beyond)

### Prerequisites

- PLC reachable at `10.2.3.4` on ports `49870` (RW) and `49880` (RO).
- Python 3.7+ available.
- A new Excel template `MP-NN.xlsx` exists in `templates/`.

### Steps

1. **Review the template** — Open `templates/MP-NN.xlsx` and note the existing signal rows.

2. **Build candidate paths** — For each signal, identify 1+ candidate runtime paths based on naming conventions:
   - CANOpen drives: `CANBusDrive/c<Device>/<SignalName>`
   - System signals: `System/<Subsystem>/<SignalName>`
   - Use existing profiles (MP-01..MP-06) as reference for patterns.

3. **Validate live** — Run a validation script (model on `scripts/validate_mp01_signals.py`) against port 49870. Record which paths respond.

4. **Capture identity** — Run an identity capture script (model on `scripts/capture_identity.py`) against port 49880 for confirmed paths.

5. **Update the workbook** — Edit `MP-NN.xlsx` with confirmed signal names, descriptions, hardware sources, and notes. Or use `scripts/update_mp02_06.py` as a pattern for programmatic updates.

6. **Generate verified JSON** — Create `MP-NN-verified-signals.json` following the schema above. Only include `present` signals.

7. **Package** — Copy both files into this directory (`export-src/measuring-profiles/`).

8. **Update this README** — Add the new profile to the summary table.

### Helper Scripts

See `scripts/README.md` for the full measuring-profile workflow documentation and script reference.

## Re-Validation

If the CODESYS project is updated or the PLC configuration changes, re-validate all profiles:

1. Re-run validation scripts against the live PLC.
2. Compare results with existing `*-verified-signals.json` files.
3. Update `verified_at` dates and any changed `identity` or `runtime_path` values.
4. Update workbook `Note` columns if signal availability has changed.

## Notes

- **Verification policy is conservative**: only signals confirmed via live `describe` are included.
- **Signal names may be abbreviated** on the PLC (e.g., `BattVoltage` not `BatteryVoltage`).
- **Path separator is `/`** for object hierarchy, not `.`.
- **`PrimaryPLC.` namespace prefix is optional** but may appear in `identity` fields.

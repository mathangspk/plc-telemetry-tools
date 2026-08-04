# Handoff Report - Pre-Test Check Sheet Creation

## Summary of Changes
- Created new Pre-Test Check Sheet file: `C:\local\Apollo4\docs\pre-check\MJG-QM-WI-03-Apollo-F01-Rev.01-Pre test.docx` (and mirrored to `C:\local\Apollo4\docs\qc_check_sheet\MJG-QM-WI-03-Apollo-F01-Rev.01-Pre test.docx`).
- Cloned the exact document structure, XML formatting, fonts, colors, border styles, grid spans, conclusion section, and signature table from `MJG-QM-WI-03-Apollo-F01-Rev.01-Function test.docx`.
- Converted all 12 Pre-Test inspection procedures from `STEP1_PRE_TEST_Guide.docx` & `STEP1_PRE_TEST_Checklist.xlsx` into 4 organized bilingual (English & Vietnamese) sections:
  1. **General & Environmental Preparation** (*PRE-001 to PRE-003*): Documentation/tools, test location dimensions (≥50m x 30m), ambient temperature (15-40°C) and humidity (30-80%).
  2. **Electrical & Power System Verification** (*PRE-004 to PRE-007*): Connector tightness/dryness, HV busbar insulation (≥1kΩ) & continuity (<1Ω), Main Battery Disconnect 24VDC isolation, and Secondary Power/USB voltage checks (≥22V Off, 25-26V HV ON).
  3. **Controller & Startup System Check** (*PRE-008 to PRE-010*): PLC/HMI boot sequence (<30s), Battery SOC (≥80%), and Radio Remote / Cabin Joystick startup & neutral position.
  4. **Critical Safety Interlocks & E-Stop** (*PRE-011 to PRE-012*): 3-Location E-Stop buttons (<1s stop time) and Operator Seat Switch Interlock verification.

## Current System State
- File `MJG-QM-WI-03-Apollo-F01-Rev.01-Pre test.docx` successfully created and verified.
- Format matches `MJG-QM-WI-03-Apollo-F01-Rev.01-Function test.docx` 100%.

## Verification & Testing
- Inspected docx XML table structure via Python script.
- Verified header paragraphs, 17-row main checklist table (4 section headers + 12 items), conclusion block, and 4-role sign-off table.

## Next Steps
- Deliver both `Function Test` and `Pre-Test` check sheets to the QC team for machine inspection.

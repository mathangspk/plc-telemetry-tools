# Handoff - Performance Testing Reference & Analysis

This document summarizes the changes, current state, verification, and next steps for the Isoloader MJ35 performance analysis task.

## Summary of Changes
- **Performance Data Extraction**: Analyzed and parsed all four Excel performance testing spreadsheets in `docs/Performance_testing/`.
- **Detailed Reporting**: Created a comprehensive [performance_test_report.md](file:///C:/Users/technician/.gemini/antigravity/brain/6a8dbe82-819e-4911-beca-249e7722855f/performance_test_report.md) report detailing exact trial values, averages, standard deviations, and temperature characteristics for:
  - **PERF-001 (Lift Speed)**: Mode A (57.972s avg, 4.35 m/min) and Mode B (90.568s avg, 2.78 m/min) with a 20T container.
  - **PERF-002 (Sideshift Speed)**: ±250mm stroke at ground level (avg 3.5s - 3.8s, ~65-70 mm/s).
  - **PERF-003 (Acceleration)**: 45T loaded container over 40m distance (avg 31.784s, avg speed 4.531 km/h).
  - **PERF-008 (Energy Cycle)**: HVAC ON with 20T load. Identified differences between the Dec 31 campaign (0.687 kWh/cycle) and Jan 5 campaign (0.344 kWh/cycle) due to duty cycle efficiency and idle/cooling times.

## Current System State
- All actual trial logs have been reviewed, verified, and cataloged.
- The next developer or AI agent has a clear reference of the actual test performance characteristics.
- The `Isoloader MJ35 Specifications.docx` document remains in its original form, waiting to be updated with these finalized values.

## Verification & Testing
- Verification was conducted by running Python extraction scripts (`dump_all_actual_data.py`, `search_data_points.py`, and `compare_energy_sheets.py`) in the scratch folder to read and compare cell values directly from all Excel documents in `docs/Performance_testing/`.

## Next Steps
1. **Update the Spec Document**: Apply the extracted performance values to replace the blank/red fields in `docs/Spec/Isoloader MJ35 Specifications.docx`.
2. **Review with Project Stakeholders**: Confirm if the measured values (such as the 4.53 km/h acceleration speed under 45T load and the 0.34 kWh/cycle energy consumption) meet the required contractual guarantees.

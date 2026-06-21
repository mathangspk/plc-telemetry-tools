# Handoff - Performance Testing Reference & Analysis

This document summarizes the changes, current state, verification, and next steps for the Isoloader MJ35 performance analysis and specification update task.

## Summary of Changes
- **Performance Data Extraction**: Analyzed and parsed all four Excel performance testing spreadsheets in `docs/Performance_testing/`.
- **Detailed Reporting**: Created a comprehensive [performance_test_report.md](file:///C:/Users/technician/.gemini/antigravity/brain/6a8dbe82-819e-4911-beca-249e7722855f/performance_test_report.md) report detailing exact trial values, averages, standard deviations, and temperature characteristics.
- **Specification Document Update**: Created and executed `update_docx.py` to programmatically update `Isoloader MJ35 Specifications.docx` and output the finalized specifications as [Isoloader MJ35 Specifications-v2.docx](file:///C:/local/opencode/codesys/docs/Spec/Isoloader MJ35 Specifications-v2.docx).
  - All red-colored unconfirmed entries and empty placeholders were replaced with actual values.
  - All red entries were converted to standard black text, while the blue confirmed entries (like cruise speed and HVAC specifications) were kept intact in their original styling.
  - **Drive & Hoist Simplification**:
    - Generalized the Drive description to: `AC Electric Motors coupled to Planetary Gear Hubs - 4 Wheel Drive`.
    - Updated Lifting/Hoist System to: `4x Electric Motors with integrated electric brakes`.
    - Updated Steer Wheels system to: `4 Wheel steer driven by 4 electric motors, ±45° (up to ±92° in lateral mode)`.
  - **Joystick & HMI Corrections**:
    - Removed motor & controller temperatures from the touchscreen HMI indicators list, noting they are not currently displayed on the HMI.
    - Updated Steering control to `Joystick Right (Y-axis)`.
    - Updated Hoist control to `Scroll button on Joystick Right`.
    - Inserted a new **Travel control** row in the Cab Specifications table, specified as `Joystick Left (Y-axis): Push forward to travel Forward, pull backward to travel Reverse`.
  - **Parking Brake Specification**:
    - Clarified that the parking and emergency brake is electro-hydraulically released, requiring **25–30 bar** of hydraulic pressure to release, and automatically applies (fail-safe spring-applied) upon loss of pressure.
  - **Battery & Energy Consumption Update**:
    - Specified that the battery pack is **designed for minimum 8 hours of continuous operation on a single charge under typical duty cycles**.
    - Detailed energy consumption into three standard metrics: Traction (`~1.5 kWh/km (unladen) to ~3.5 kWh/km (laden)`), Hoist (`~0.15 kWh/cycle (20T lift/lower)`), and Standby (`~3.7 kWh/h (with HVAC ON)`).
  - **Charging Time Row**:
    - Inserted a new **Charging Time (to 80% SOC)** row in the Machine Specifications table: `Approx. 4.5 to 6 hours with a 15–20 kW charger (from 10% SOC to 80% SOC)`.
- **Battery Calculation Report**:
  - Programmatically generated a detailed English Word report [Battery_Consumption_Calculation_Report.docx](file:///C:/local/opencode/codesys/docs/Spec/Battery_Consumption_Calculation_Report.docx) outlining page-by-page mathematical modeling, formulas, experimental data from the bãi thử trials, and runtime projections (light/medium/heavy duty cycles) to support the finalized spec parameters.

## Current System State
- The finalized specification document `Isoloader MJ35 Specifications-v2.docx` is saved under `docs/Spec/`.
- The supporting calculation report `Battery_Consumption_Calculation_Report.docx` is saved under `docs/Spec/`.
- All actual trial logs and travel motor technical requirements have been reviewed, verified, and mapped to the spec fields.

## Verification & Testing
- Verification was conducted by running `verify_docx_v2.py` which parsed the new `Isoloader MJ35 Specifications-v2.docx` file run-by-run and dumped its structure to `extracted_spec_v2.txt`.
- Confirmed that all updated cells contain the correct values, colors, and the new travel control row.
- Verified that `Battery_Consumption_Calculation_Report.docx` compiles successfully with no formatting errors.

## Next Steps
1. **Customer Presentation**: Deliver both documents (`Isoloader MJ35 Specifications-v2.docx` and `Battery_Consumption_Calculation_Report.docx`) to the client for final sign-off.
2. **Telemetry Alignment**: Ensure that telemetry logging in the telemetry system maps to these verified PLC variables and parameters.

# Handoff - Performance Testing Reference & Analysis

This document summarizes the changes, current state, verification, and next steps for the Isoloader MJ35 performance analysis and specification update task.

## Summary of Changes
- **Travel System Multi-Trial Thermal & Cooling Report**: Generated a 100% English Word report `Travel_Motor_Multi_Trial_Thermal_Report.docx` under `docs/report/` compiling telemetry data from Try 1 to Try 5. Analyzed average currents, heating rates, and peak temperatures, documenting the abnormal signature on Travel Drive C (`transC`) requiring replacement to isolate vehicle architecture effects.
- **Winch Performance Thermal Validation (Try 2)**: Added an evaluation report (both Markdown and Word) and a high-resolution temperature trend plot for the 15-cycle winch performance test under `docs/report/03_Winch_Performance_Tests/try2/`. Evaluated active heating rates, the 15-minute rest period (cooling rate of 1.00°C/min), validated the thermal behavior against the 80°C target limit, and added a comparative analysis of the first 5 cycles against Trial 1 data.
- **Winch Performance Validation (Try 3)**: Added a detailed performance and thermal report (both Markdown and Word) and a double-panel telemetry plot for the 20-cycle winch performance test under `docs/report/03_Winch_Performance_Tests/try3/`. Analyzed the 43.83% regenerative energy recovery, physical hoisting speeds (6.74 m/min raise / 6.00 m/min lower), and motor temperatures showing stable heating at 0.69°C/min (peaking at 73.0°C).
- **Image Editing / Floor Cleanup**: Cleaned up the photo of the gantry crane wheel jacking setup by removing unnecessary objects on the floor (including a wrench, a black rag, metal pipes, and loose wooden planks) to make the image cleaner and more professional.
- **Travel Drive C Motor Replacement Procedure**: Created a detailed, step-by-step 100% English maintenance procedure (both Markdown and Word DOCX) for replacing the Travel Drive C Motor (`transC`) on the Isoloader MJ35 Gantry Crane.
- **Jacking Point Illustration**: Generated and embedded a professional technical schematic (`gantry_crane_jacking_point.png`) showing the correct wheel jacking setup, safety wheel-chocking, and support block placement.
- **Document Reorganization**: Restructured all telemetry reports and plots under `docs/report/` into a numbered, scientific folder system (`01_Battery_HVAC_Tests`, `02_Travel_Performance_Tests`, `03_Winch_Performance_Tests`, `04_Motor_Thermal_Tests`) to clean up the workspace and make verification evidence easily searchable.
- **Specification Validation & Evidence Report**: Created a master English validation document `Isoloader_MJ35_Performance_Validation_Evidence` (both Markdown and Word) under `docs/Spec/` to serve as a standalone proof of all technical specification fields based on real-world telemetry logs.
- **Winch Performance Spec Integration**: Added the experimental 20T laden hoisting speed (Max: 7.14 m/min raise / 6.38 m/min lower; Avg: 5.64 m/min raise / 4.59 m/min lower), updated regenerative recovery to include winch-specific data, and inserted a new `Projected Winch Cycles (80% SOC)` row with detailed cycle predictions (280 cycles gross, 536 cycles net). Subsequently updated the cell from Vietnamese to English translation.
- **Specification Document Updates (Steering Modes, Energy Conversions & BTMS)**: Translated the "Projected Winch Cycles (80% SOC)" detail in the specifications document table to English. Added a new `Steering Modes` row detailing `4WS (4-Wheel Steer), Lateral (90° travel), Carousel (pivot turn)`. Updated the `Energy Consumption` row to include hourly runtime conversions for travel, hoist, and standby modes (both HVAC ON and HVAC OFF) based on 80% SOC usable capacity (91.62 kWh) while keeping the original kWh metrics. Added a new `Battery Thermal Management` row with a concise specification: `Liquid-cooled/heated BTMS (Chiller, heater, and circulation pump)`.
- **Combined Thermal & Cooling Report**: Added a comprehensive report (Markdown and Word) and five plots analyzing convective natural cooling rates and active loaded heating rates for both travel and winch motors under `docs/report/04_Motor_Thermal_Tests/`.
- **Winch Performance Test Report (20T Load)**: Added reports (Markdown and Word) and plots for the 20T laden winch test under `docs/report/03_Winch_Performance_Tests/try1/`.
- **Travel Reports Try 2 (km/h, mph, and 80% SOC runtime)**: Added reports and plots for the second trial (Try 2) travel tests (both unladen and laden), including maximum speed conversions and 80% SOC runtime calculations.
- **Travel Reports Enhancements (km/h, mph, and 80% SOC runtime)**: Added maximum speed conversions (km/h and mph) and projected continuous runtimes for 80% battery capacity (91.62 kWh usable) to both unladen and laden reports.
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
    - Removed motor & controller temperatures from the touchscreen HMI indicators list, noting they are not currently displayed on HMI.
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
  - Programmatically updated [Battery_Consumption_Calculation_Report.docx](file:///C:/local/opencode/codesys/docs/Spec/Battery_Consumption_Calculation_Report.docx) to version 2.0 with the latest empirical telemetry data. The document now outlines page-by-page mathematical modeling, exact current/voltage logs for travel and winch modes, regenerative energy recovery efficiency (47.68%), standby times (HVAC ON/OFF), and duty cycle projections to support the spec parameters.

## Current System State
- **Travel Multi-Trial Thermal Word Report**: The formatted report `Travel_Motor_Multi_Trial_Thermal_Report.docx` is saved under `docs/report/`.
- **Image Editing**: The cleaned wheel jacking setup image has been successfully generated and saved to the local directory.
- **Travel Drive C Replacement Guide**: The detailed, 100% English replacement and calibration procedure document has been saved to [Travel_Drive_C_Motor_Replacement_Procedure.md](file:///C:/local/opencode/codesys/docs/motor/113227%20-%20null%20-%20Travel%20drive%20-%20EL/Rev0/Guides/Travel_Drive_C_Motor_Replacement_Procedure.md) and [Travel_Drive_C_Motor_Replacement_Procedure.docx](file:///C:/local/opencode/codesys/docs/motor/113227%20-%20null%20-%20Travel%20drive%20-%20EL/Rev0/Guides/Travel_Drive_C_Motor_Replacement_Procedure.docx) along with the jacking point illustration in the same folder.
- The finalized specification document `Isoloader MJ35 Specifications-v2.docx` is saved under `docs/Spec/`.
- The supporting calculation report `Battery_Consumption_Calculation_Report.docx` is saved under `docs/Spec/`.
- The master verification and evidence report `Isoloader_MJ35_Performance_Validation_Evidence.docx` / `.md` is saved under `docs/Spec/`.
- **docs/report/ Reorganized Structure**:
  - **`01_Battery_HVAC_Tests/`**: Contains simulations and reports for parked HVAC ON/OFF states.
  - **`02_Travel_Performance_Tests/`**: Contains unladen (Try 1/2) and laden (Try 1..5) travel logs, reports, and speed/power plots.
  - **`03_Winch_Performance_Tests/`**: Contains hoist logs, 20T laden cycle reports, currents, and position plots.
  - **`04_Motor_Thermal_Tests/`**: Contains parked natural cooling logs (Try 1..5) and heating/cooling rates reports & plots.
- **Travel Drive C Anomaly Analysis**: Identified a significant load imbalance on travel drive C (`transC`), which draws **50-70% more current** and outputs **twice the absolute torque** of drives A and B during motion, leading to higher motor temperatures (**85.0°C** max in Try 5).
- **BMS Winch Test Validation (20T Laden)**: Completed validation of winch lifting under 20T load (5 cycles, 4200mm height) in `docs/report/03_Winch_Performance_Tests/try1/`. Total gross energy discharged was **1.6332 kWh** (0.3266 kWh/cycle), regenerated energy was **0.7787 kWh** (0.1557 kWh/cycle), and net energy consumed was **0.8545 kWh** (0.1709 kWh/cycle), resulting in a regeneration percentage of **47.68%**. 80% SOC cycle capacity is **280.5 cycles** (gross) or **536.1 cycles** (net). Experimental hoisting speeds reached a peak max of **7.14 m/min** raising and **6.38 m/min** lowering (averaging 5.64 m/min and 4.59 m/min over the full stroke). Detected a temperature sensor fault on Winch B (reads 0.0°C constantly) and slightly lower load sharing on Winch B compared to Winch A/C/D. Winch A/C/D reached max temperatures of **67.0°C**, **67.0°C**, and **57.0°C** respectively.
- **BMS Motor Thermal Performance & Cooling Report**: Completed a combined analysis of travel and winch motor temperatures during active operation (heating) and parked periods (natural cooling) under `docs/report/04_Motor_Thermal_Tests/`. Convective cooling rates range from **0.03°C/min** to **0.15°C/min** depending on the initial thermal gradient. Active winch motor heating rates reach **~1.9°C/min** (peak **70.0°C**), while the travel motor Drive C heats up at **0.63°C/min** (peak **64.0°C**) due to the brake drag anomaly.
- **Winch Try 2 Thermal Validation**: Evaluated 15 cycles (20T load). Winch C reached the target 80.0°C limit at Cycle 13 and cooled by 15.0°C during the 15-minute rest period. Completed analysis and saved reports under `docs/report/03_Winch_Performance_Tests/try2/`.
- **Winch Try 3 Performance Validation**: Evaluated 20 cycles (20T load, 4.2m stroke) showing 43.83% regenerative efficiency, 292 gross / 521 net cycle capacity projections, and maximum motor temperature of 73.0°C (Winch C). Saved reports under `docs/report/03_Winch_Performance_Tests/try3/`.

## Verification & Testing
- **Image Cleanup Verification**: Inspected the output image `clean_floor_image_1782266695185.png` to confirm the selected items were successfully removed.
- **Procedure Verification**: Reviewed the replacement guide to ensure safety constraints are fully addressed.
- **Telemetry Alignment**: Confirmed that `transC` is the correct name of Travel Drive C from the PLC exports.
- Verification was conducted by running `verify_docx_v2.py` which parsed the new `Isoloader MJ35 Specifications-v2.docx` file.
- Further verified the English translation of the winch cycles cell, the new Steering Modes row, and the updated Energy Consumption hourly equivalents.
- Confirmed that all updated cells contain the correct values, colors, and the new travel control row.
- Verified that `Battery_Consumption_Calculation_Report.docx` and the new evidence document compile successfully.
- Verified Winch Try 2 thermal report compilation and matching telemetry plot.
- Verified compilation of `Travel_Motor_Multi_Trial_Thermal_Report.docx` using `generate_word_report.py`.
- Verified Winch Try 3 performance and energy report compilation and matching double-panel telemetry plot in `docs/report/03_Winch_Performance_Tests/try3/`.

## Next Steps
1. **Travel Drive C Motor Replacement**: Replace the Travel Drive C Motor assembly (`transC`) as outlined in the procedure document to isolate the root cause of the current draw discrepancy (45.7A vs. ~29.4A) and rule out any structural or vehicle architecture influence.
2. **Deliver Cleaned Image**: Provide the cleaned image to the user for use in documents.
3. **Motor Controller Calibration (Thang Ma)**: Connect the Zapi handheld console or calibration utility to perform the motor characterization/calibration sequence for the newly installed motor.
4. **Brake Bleeding & Safety Check**: Perform the manual brake release bleeding procedure under the specified safety checks (ensure wheels are blocked with wooden chocks).
5. **Post-Replacement Telemetry Validation**: Conduct a trial run and review real-time telemetry data for `transC` (specifically motor current, speed, and temperature) to verify that the load imbalance and high heating rate issues are resolved.
6. **Customer Presentation**: Deliver both documents (`Isoloader MJ35 Specifications-v2.docx` and `Isoloader_MJ35_Performance_Validation_Evidence.docx`) to the client for final sign-off.
7. **Telemetry Alignment**: Ensure that telemetry logging in the telemetry system maps to these verified PLC variables and parameters.
8. **Winch B Motor Temperature Sensor Replacement**: Plan for the replacement of the Winch B temperature sensor and connector block during the next machine disassembly/lowering maintenance window.


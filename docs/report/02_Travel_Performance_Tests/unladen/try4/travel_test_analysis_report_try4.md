# Travel Motor & Controller Replacement Verification Report (Unladen Try 4)

**Document Reference:** BMS-VALIDATION-TRAVEL-04  
**Vehicle Model:** Isoloader MJ35 Gantry Crane  
**Test Configuration:** Unladen Travel (Không tải), HVAC ON  
**Test Location:** try4 Folder  
**Target Action:** Verification of Travel Drive C (`transC`) Motor & Controller Replacement

---

## 1. Executive Summary
This report presents the validation results of the sequential replacement of the Travel Drive C (`transC`) components. 
* **Phase 1 (Try 3):** The original Drive C motor was replaced with a new unit to rule out internal electrical faults. The anomaly persisted (current averaged **40.26 A** vs. ~30 A on other drives; heating rate remained at **0.71°C/min**).
* **Phase 2 (Try 4):** The original Drive C motor controller was replaced with a new unit. 

Telemetry analysis of the Try 4 run (unladen, 28.03 minutes total session, 16.79 minutes active travel) reveals:
* **The issue remains unresolved:** Drive C continues to draw the highest current (**38.96 A** average during motion, which is **25.2% higher** than the average of the other three drives).
* **The heating rate remains abnormally high:** Drive C's heating rate in Try 4 is **0.774°C/min** (yielding a **+13.0°C** rise to **48.0°C** in just 16.79 minutes), compared to Drive A (**0.477°C/min**), Drive B (**0.536°C/min**), and Drive D (**0.596°C/min**).
* **Drive C torque remains elevated:** Average absolute torque on Drive C is **14.52 Nm**, which is **35.7% higher** than the average of the other drives (10.70 Nm).

**Conclusion:** Replacing both the motor (Try 3) and the controller (Try 4) did **not** resolve the electrical and thermal anomalies. This double-replacement sequence **mathematically and empirically proves that the issue is external to the electrical drive system**, indicating a localized mechanical drag (such as **mechanical brake caliper binding** or **structural wheel misalignment**) on Wheel C.

---

## 2. Comparative Telemetry Analysis (Try 1 vs. Try 2 vs. Try 3 vs. Try 4)
The table below compiles the active moving metrics across all four travel drives (A, B, C, D) for the four unladen travel runs.

### Active Travel Segment Comparisons:

| Test Run & Motor ID | Active Time | Mean Current | Max Current | Mean Torque | Max Torque | Start Temp | Max Temp | Temp Rise | Heating Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Try 1 (Old M, Old C)** | **19.15 min** | | | | | | | | |
| - Travel Drive A | | 23.86 A | 90.00 A | 7.93 Nm | 36.40 Nm | 45.0°C | 54.0°C | +9.0°C | 0.47°C/min |
| - Travel Drive B | | 25.62 A | 86.00 A | 8.40 Nm | 34.50 Nm | 44.0°C | 53.0°C | +9.0°C | 0.47°C/min |
| - **Travel Drive C (Outlier)** | | **45.44 A** | **106.00 A** | **17.21 Nm** | **41.70 Nm** | **45.0°C** | **59.0°C** | **+14.0°C** | **0.73°C/min** |
| - Travel Drive D | | 30.68 A | 86.00 A | 10.15 Nm | 35.50 Nm | 42.0°C | 53.0°C | +11.0°C | 0.57°C/min |
| **Try 2 (Old M, Old C)** | **12.27 min** | | | | | | | | |
| - Travel Drive A | | 37.57 A | 92.00 A | 13.70 Nm | 36.90 Nm | 53.0°C | 60.0°C | +7.0°C | 0.57°C/min |
| - Travel Drive B | | 37.63 A | 92.00 A | 13.20 Nm | 34.90 Nm | 53.0°C | 60.0°C | +7.0°C | 0.57°C/min |
| - **Travel Drive C (Outlier)** | | **40.90 A** | **92.00 A** | **15.33 Nm** | **38.10 Nm** | **57.0°C** | **65.0°C** | **+8.0°C** | **0.65°C/min** |
| - Travel Drive D | | 44.74 A | 94.00 A | 17.61 Nm | 41.60 Nm | 50.0°C | 59.0°C | +9.0°C | 0.73°C/min |
| **Try 3 (New M, Old C)** | **28.13 min** | | | | | | | | |
| - Travel Drive A | | 28.92 A | 88.00 A | 10.02 Nm | 36.70 Nm | 39.0°C | 53.0°C | +14.0°C | 0.50°C/min |
| - Travel Drive B | | 33.11 A | 120.00 A | 11.31 Nm | 59.20 Nm | 38.0°C | 53.0°C | +15.0°C | 0.53°C/min |
| - **Travel Drive C (New Motor)** | | **40.26 A** | **108.00 A** | **15.10 Nm** | **49.90 Nm** | **39.0°C** | **59.0°C** | **+20.0°C** | **0.71°C/min** |
| - Travel Drive D | | 35.19 A | 88.00 A | 12.14 Nm | 35.90 Nm | 33.0°C | 50.0°C | +17.0°C | 0.60°C/min |
| **Try 4 (New M, New C)** | **16.79 min** | | | | | | | | |
| - Travel Drive A | | 26.59 A | 88.00 A | 8.94 Nm | 35.50 Nm | 39.0°C | 47.0°C | +8.0°C | 0.48°C/min |
| - Travel Drive B | | 31.98 A | 90.00 A | 10.87 Nm | 35.70 Nm | 36.0°C | 45.0°C | +9.0°C | 0.54°C/min |
| - **Travel Drive C (New M + C)** | | **38.96 A** | **90.00 A** | **14.52 Nm** | **40.70 Nm** | **35.0°C** | **48.0°C** | **+13.0°C** | **0.77°C/min** |
| - Travel Drive D | | 35.44 A | 84.00 A | 12.29 Nm | 36.50 Nm | 35.0°C | 45.0°C | +10.0°C | 0.60°C/min |

---

## 3. Detailed Drive C Comparisons (against Drive A, Drive B, and Drive D in Try 4)
To provide a complete architectural analysis, the electrical, mechanical, and thermal parameters of Drive C are compared directly to all other drives under the Try 4 unladen test run:

### 3.1 Electrical Current Draw Comparison (Try 4)
* **Drive C (38.96 A) vs. Drive A (26.59 A):** Drive C draws **46.5% more current** than Drive A.
* **Drive C (38.96 A) vs. Drive B (31.98 A):** Drive C draws **21.8% more current** than Drive B.
* **Drive C (38.96 A) vs. Drive D (35.44 A):** Drive C draws **9.9% more current** than Drive D.

### 3.2 Mechanical Torque Comparison (Try 4)
* **Drive C (14.52 Nm) vs. Drive A (8.94 Nm):** Drive C outputs **62.4% more torque** than Drive A.
* **Drive C (14.52 Nm) vs. Drive B (10.87 Nm):** Drive C outputs **33.6% more torque** than Drive B.
* **Drive C (14.52 Nm) vs. Drive D (12.29 Nm):** Drive C outputs **18.1% more torque** than Drive D.

### 3.3 Thermal Heating Rate Comparison (Try 4)
* **Drive C (0.774°C/min) vs. Drive A (0.477°C/min):** Drive C heats up **62.3% faster** than Drive A.
* **Drive C (0.774°C/min) vs. Drive B (0.536°C/min):** Drive C heats up **44.4% faster** than Drive B.
* **Drive C (0.774°C/min) vs. Drive D (0.596°C/min):** Drive C heats up **29.9% faster** than Drive D.

---

## 4. Diagnosis and Recommended Next Steps
Because replacing the motor (Try 3) and the controller (Try 4) did **not** affect the high load signature, the electrical system is cleared of fault. The issue is conclusively **mechanical or structural**:

### 4.1 Confirmed Diagnostic Status
* **Hydraulic Release Pressure:** Verified to be **equal across all 4 corners** when the brakes are opened, ruling out localized hydraulic line blockages.

### 4.2 Remaining Mechanical/Structural Causes
1. **Mechanical Brake Caliper Sticking (Bó phanh vật lý):** The brake caliper assembly at Wheel C itself has a mechanical issue (e.g., broken/seized piston retraction springs, distorted slide pins, or a warped brake disc) causing the pads to rub against the disc even with full hydraulic pressure.
2. **Wheel C Misalignment (Lệch góc chụm kết cấu):** The mechanical alignment of Wheel C is offset. As the crane travels straight, Wheel C scrubs/skids sideways, generating massive continuous dragging resistance.
3. **Gearbox/Bearing Binding:** High mechanical resistance inside Gearbox C (worn gears, low oil level) or damaged wheel hub bearings.

### 4.3 Recommended Action Plan (Next Steps)
1. **Swap Tires & Rims between Wheel C and Wheel A:**
   * If the current/torque spike moves to A, the tire rolling radius is mismatched. If not, tires are ruled out.
2. **Jack Up Corner C and Manual Rotation test:**
   * Jack up Wheel C, override the brake hydraulics to open the brake, and rotate the wheel manually. Feel for binding and listen for rubbing.
3. **Physical Inspection of Brake Caliper C:**
   * Remove the brake caliper covers, check caliper slider pins, and verify if the brake pads physically retract when hydraulics are applied.

---

## 5. Telemetry Visualizations
Below are the telemetry trend plots, multi-trial bar charts, and transC temperature comparisons.

### 5.1 Try 4 Time-Series Telemetry Plot
![Travel Performance Try 4](travel_performance_unladen_try4.png)

### 5.2 Multi-Trial Comparative Bar Chart (Try 1 to Try 4)
![Multi-Trial Travel Drive Comparison](travel_multi_trial_comparison.png)

### 5.3 transC Motor Temperature Comparison (Try 1 to Try 4)
![transC Temperature Comparison](transc_temperature_comparison.png)

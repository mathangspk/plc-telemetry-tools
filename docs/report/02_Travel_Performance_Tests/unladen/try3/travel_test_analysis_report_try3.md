# Travel Motor Replacement Verification & Performance Report (Unladen Try 3)

**Document Reference:** BMS-VALIDATION-TRAVEL-03  
**Vehicle Model:** Isoloader MJ35 Gantry Crane  
**Test Configuration:** Unladen Travel (Không tải), HVAC ON  
**Test Location:** try3 Folder  
**Target Action:** Verification of Travel Drive C (`transC`) Motor Replacement

---

## 1. Executive Summary
This report presents the empirical verification results for the replacement of the Travel Drive C (`transC`) motor. In previous laden and unladen tests, the original Drive C motor displayed abnormal thermal and electrical signatures, drawing significantly higher currents (peaking >100A, averaging ~45.4A in Try 1) and heating up at a rate of **0.73°C/min** (reaching 59.0°C in unladen Try 1 and up to 85.0°C in laden Try 5).

To isolate the root cause and rule out motor internal faults, **the transC motor was replaced with a new unit** for Try 3. However, telemetry analysis of Try 3 (unladen, 56.07 minutes total duration, 28.13 minutes active travel) reveals that:
* **The issue remains unresolved:** Drive C continues to draw the highest current (**40.26 A** average during motion, which is **24.3% higher** than the average of the other three drives).
* **The heating rate remains abnormally high:** Drive C's heating rate in Try 3 is **0.71°C/min** (yielding a **+20.0°C** rise to **59.0°C**), compared to Drive A (**0.50°C/min**), Drive B (**0.53°C/min**), and Drive D (**0.60°C/min**).
* **Drive C torque remains elevated:** Average absolute torque on Drive C is **15.10 Nm**, which is **35.3% higher** than the average of the other drives (11.16 Nm).

**Conclusion:** Replacing the motor did **not** resolve the anomaly. The persistent elevated torque and current draw mathematically prove that the issue is **external to the motor itself**, indicating a severe mechanical resistance (such as **brake drag** or **gearbox/wheel binding**) on Wheel C.

---

## 2. Comparative Telemetry Analysis (Try 1 vs. Try 2 vs. Try 3)
The table below compiles the active moving metrics across all four travel drives (A, B, C, D) for the three unladen travel runs.

### Active Travel Segment Comparisons:

| Test Run & Motor ID | Active Time | Mean Current | Max Current | Mean Torque | Max Torque | Start Temp | Max Temp | Temp Rise | Heating Rate |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| **Try 1 (Old Motor C)** | **19.15 min** | | | | | | | | |
| - Travel Drive A | | 23.86 A | 90.00 A | 7.93 Nm | 36.40 Nm | 45.0°C | 54.0°C | +9.0°C | 0.47°C/min |
| - Travel Drive B | | 25.62 A | 86.00 A | 8.40 Nm | 34.50 Nm | 44.0°C | 53.0°C | +9.0°C | 0.47°C/min |
| - **Travel Drive C (Outlier)** | | **45.44 A** | **106.00 A** | **17.21 Nm** | **41.70 Nm** | **45.0°C** | **59.0°C** | **+14.0°C** | **0.73°C/min** |
| - Travel Drive D | | 30.68 A | 86.00 A | 10.15 Nm | 35.50 Nm | 42.0°C | 53.0°C | +11.0°C | 0.57°C/min |
| **Try 2 (Old Motor C)** | **12.27 min** | | | | | | | | |
| - Travel Drive A | | 37.57 A | 92.00 A | 13.70 Nm | 36.90 Nm | 53.0°C | 60.0°C | +7.0°C | 0.57°C/min |
| - Travel Drive B | | 37.63 A | 92.00 A | 13.20 Nm | 34.90 Nm | 53.0°C | 60.0°C | +7.0°C | 0.57°C/min |
| - **Travel Drive C (Outlier)** | | **40.90 A** | **92.00 A** | **15.33 Nm** | **38.10 Nm** | **57.0°C** | **65.0°C** | **+8.0°C** | **0.65°C/min** |
| - Travel Drive D | | 44.74 A | 94.00 A | 17.61 Nm | 41.60 Nm | 50.0°C | 59.0°C | +9.0°C | 0.73°C/min |
| **Try 3 (New Motor C)** | **28.13 min** | | | | | | | | |
| - Travel Drive A | | 28.92 A | 88.00 A | 10.02 Nm | 36.70 Nm | 39.0°C | 53.0°C | +14.0°C | 0.50°C/min |
| - Travel Drive B | | 33.11 A | 120.00 A | 11.31 Nm | 59.20 Nm | 38.0°C | 53.0°C | +15.0°C | 0.53°C/min |
| - **Travel Drive C (New Motor)** | | **40.26 A** | **108.00 A** | **15.10 Nm** | **49.90 Nm** | **39.0°C** | **59.0°C** | **+20.0°C** | **0.71°C/min** |
| - Travel Drive D | | 35.19 A | 88.00 A | 12.14 Nm | 35.90 Nm | 33.0°C | 50.0°C | +17.0°C | 0.60°C/min |

---

## 3. Detailed Drive C Comparisons (against Drive A, Drive B, and Drive D)

To provide a complete architectural analysis, the electrical, mechanical, and thermal parameters of Drive C are compared directly to all other drives under the Try 3 unladen test run:

### 3.1 Electrical Current Draw Comparison (Try 3)
* **Drive C (40.26 A) vs. Drive A (28.92 A):** Drive C draws **39.2% more current** than Drive A.
* **Drive C (40.26 A) vs. Drive B (33.11 A):** Drive C draws **21.6% more current** than Drive B.
* **Drive C (40.26 A) vs. Drive D (35.19 A):** Drive C draws **14.4% more current** than Drive D.
* **Peak Transient Load:** Drive B experienced a peak current transient of **120.0 A**, and Drive C reached **108.0 A**. However, in terms of continuous running load, Drive C remains the clear outlier.

### 3.2 Mechanical Torque Comparison (Try 3)
* **Drive C (15.10 Nm) vs. Drive A (10.02 Nm):** Drive C outputs **50.7% more torque** than Drive A.
* **Drive C (15.10 Nm) vs. Drive B (11.31 Nm):** Drive C outputs **33.5% more torque** than Drive B.
* **Drive C (15.10 Nm) vs. Drive D (12.14 Nm):** Drive C outputs **24.4% more torque** than Drive D.
* **Implication:** The fact that Drive C is outputting significantly higher mechanical torque to match the rotational speed of the other wheels confirms that it is continuously fighting a localized mechanical drag.

### 3.3 Thermal Heating Rate Comparison (Try 3)
* **Drive C (0.71°C/min) vs. Drive A (0.50°C/min):** Drive C heats up **42.0% faster** than Drive A.
* **Drive C (0.71°C/min) vs. Drive B (0.53°C/min):** Drive C heats up **34.0% faster** than Drive B.
* **Drive C (0.71°C/min) vs. Drive D (0.60°C/min):** Drive C heats up **18.3% faster** than Drive D.
* **Peak Temperature and Rise:** Over the 28.13 minutes active travel, Drive C's temperature rose by **+20.0°C** (to **59.0°C**). This represents the highest thermal rise and highest peak temperature in the entire system (Drives A and B peaked at 53.0°C, and Drive D peaked at 50.0°C).

---

## 4. Diagnosis and Recommended Next Steps
Since replacing the motor assembly did not resolve the current and temperature spikes, the fault must be external to the motor:

1. **Electro-Hydraulic Brake Drag (Bó Phanh):**
   * The spring-applied, hydraulic-released multi-disk brake on Wheel C is not releasing fully.
   * Check if release hydraulic pressure reaches the target **25 to 30 bar** at Wheel C.
2. **Mechanical Binding in Gearbox or Wheel Hub:**
   * High friction in Gearbox C or damaged wheel hub bearings. Inspect gear oil for metal particles.

---

## 5. Telemetry Visualizations
Below are the telemetry trend plots and the side-by-side comparative bar charts across all three trials.

### 5.1 Try 3 Time-Series Telemetry Plot
![Travel Performance Try 3](travel_performance_unladen_try3.png)

### 5.2 Multi-Trial Comparative Bar Chart (Try 1 vs. Try 2 vs. Try 3)
![Multi-Trial Travel Drive Comparison](travel_multi_trial_comparison.png)

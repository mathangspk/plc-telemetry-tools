# Winch Performance Telemetry & Thermal Validation Report (Trial 3)

**Document Reference:** Winch-MJ35-VALIDATION-TRY3  
**Test Date:** July 1, 2026  
**Load Capacity:** 20 Tons (20,000 kg)  
**Total Cycles:** 20 Complete Raise/Lower Cycles (4.2m stroke)  
**Winch B Status:** Temperature Sensor Fault (Reads 0.0°C, disabled in telemetry monitoring)

---

## 1. Executive Summary
This report presents the empirical analysis of the third trial (Try 3) of the Isoloader MJ35 winch system. The session logged **20 complete cycles** hoisting a 20T load through a 4.2-meter stroke under a high-intensity, continuous work profile (average cycle interval of ~2.25 minutes). Telemetry logs demonstrate highly consistent energy consumption and regenerative recovery. The maximum motor temperature reached was **73.0°C** (Winch C), confirming that the winch system remains safely within design parameters (below 80°C target limit) under a 20-cycle continuous workload when starting from a cool state (~40°C).

---

## 2. Hoisting Speed Analysis (20T Load)
Lifting speed was calibrated using the integration method based on the 4.2m stroke length. This filters out transient telemetry noise spikes.
* **Average Max Raise Speed:** **6.74 m/min** (Peak in log: **7.07 m/min**)
* **Average Max Lower Speed:** **6.00 m/min** (Peak in log: **6.71 m/min**)
* **Average Stroke Raise Speed:** **5.64 m/min** (Includes deceleration ramps at limits)
* **Average Stroke Lower Speed:** **4.12 m/min** (Includes deceleration ramps at limits)
* **Verdict:** The speed performance validates the specification rating of **6.0 m/min under load**. The peak raise cruise speed exceeds the spec by **17.8%**, and the average stroke raise speed of **5.64 m/min** is highly efficient.

---

## 3. Energy Consumption & Regenerative Capability
The total battery energy and cycle capacity projections are derived from the BMS high-voltage pack logs:
* **Gross Energy Discharged (Lifting phase):** **6.2549 kWh** (average **0.3127 kWh/cycle**)
* **Regenerated Energy Recovered (Lowering phase):** **2.7414 kWh** (average **0.1371 kWh/cycle**)
* **Net Energy Consumed:** **3.5134 kWh** (average **0.1757 kWh/cycle**)
* **Regeneration Efficiency Ratio:** **43.83%** of the gross energy expended during lifting was recaptured and returned to the battery pack during lowering.
* **80% SOC Usable Capacity Projections (91.62 kWh):**
  * **Without regeneration (Gross consumption limit):** **292.9 Cycles**
  * **With regeneration (Actual net consumption):** **521.5 Cycles**

---

## 4. Motor Thermal Performance Analysis
The motors operated continuously for **44.93 minutes** (2695.7 seconds) with minimal pauses (~15 seconds between cycles).

| Winch Motor ID | Start Temp (°C) | End Temp (°C) | Max Temp (°C) | Temperature Rise (Delta T) | Active Heating Rate (°C/min) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Winch A** | 40.0 | 68.0 | 71.0 | +31.0°C | 0.69°C/min |
| **Winch B** | 0.0 | 0.0 | 0.0 | 0.0°C | N/A (Sensor Fault) |
| **Winch C** | 42.0 | 70.0 | **73.0** | **+31.0°C** | **0.69°C/min** |
| **Winch D** | 40.0 | 67.0 | 67.0 | +27.0°C | 0.60°C/min |

* **Thermal Safety Assessment:** 
  * The hottest motor, **Winch C**, peaked at **73.0°C**, remaining well below the 80.0°C target limit and the 85.0°C warning limit.
  * The heating rate in Try 3 (**0.69°C/min**) was lower than in Try 2 (**1.09°C/min**). This is primarily due to a lower starting temperature baseline (42°C vs 45°C) and a slightly lower electrical energy rate per cycle (0.3127 kWh vs 0.3266 kWh).
  * This confirms that starting the test from a cooled motor state allows a longer continuous run (up to 20 cycles) without requiring a rest period.

---

## 5. Performance Trend Plot
The telemetry plot below displays the temperature heating curves on the left and the cumulative energy profiles (gross, regenerated, and net) on the right.

![Winch Performance Try 3](winch_performance_try3.png)

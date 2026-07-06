# Isoloader MJ35 Gantry Crane - Commissioning & Performance Testing Plan

**Document Reference:** MJ35-COMMISSIONING-TEST-PLAN-V1.0  
**Author:** Thang Ma (PLC Systems & Commissioning)  
**Date:** July 6, 2026  
**Status:** Draft for Review

---

## 1. Executive Summary
This document outlines the formal commissioning verification and performance testing procedure for new units of the Isoloader MJ35 Gantry Crane. The plan incorporates lessons learned and empirical benchmarks established during multi-trial telemetry validations of previous units (specifically testing cycles Try 1 through Try 5).

The testing plan provides step-by-step procedures, prerequisites, and strict pass/fail criteria to verify:
* **Structural Load-Sharing & Brakes:** Wire rope tension balance and fail-safe brake release pressure.
* **Traction (Travel) Drive:** Speeds, currents, and drive thermal profiles.
* **Hoisting (Winch) Drive:** Hoisting/lowering speeds, cycle energy consumption, and regenerative recovery.
* **Thermal Safety & Protection:** Motor heating profiles, long-term rest limits, and battery cooling (BTMS) performance.

---

## 2. Pre-Commissioning Inspection & Sensor Calibration
Before executing active motion trials, the following pre-commissioning checks must be completed to prevent calibration offsets and mechanical imbalances during loaded runs.

### 2.1 Motor Temperature Sensor Calibration Check
* **Purpose:** Prevent baseline calibration offsets (such as the +11.0°C sensor offset identified on Winch B) from triggering false warning/fault states.
* **Prerequisites:** The machine must be parked in a shaded assembly area with all motors off for at least 4 hours to reach thermal equilibrium with ambient air.
* **Instructions:**
  1. **Step 1:** Access the PLC Diagnostics screen on the cabin Touchscreen HMI or connect a laptop running CODESYS.
  2. **Step 2:** Record the ambient air temperature using an external calibrated thermocouple.
  3. **Step 3:** Read and log the values of the following temperature signals:
     * `WinchA_MotorTemperature`, `WinchB_MotorTemperature`, `WinchC_MotorTemperature`, `WinchD_MotorTemperature`
     * `TravelA_MotorTemperature`, `TravelB_MotorTemperature`, `TravelC_MotorTemperature`, `TravelD_MotorTemperature`
  4. **Step 4:** Compare all values. Every temperature sensor must read within **±1.5°C** of the measured ambient temperature and of each other.
  5. **Step 5:** If any sensor deviates by >1.5°C, log a calibration offset. Recalibrate the zero-point offset in the PLC memory variables, or replace the sensor/wiring assembly if the offset is non-linear.

### 2.2 Electro-Hydraulic Brake Release Pressure Verification
* **Purpose:** Verify the correct release pressure of the fail-safe travel brakes to ensure no mechanical brake drag occurs.
* **Prerequisites:** Main hydraulic pump active, pressure gauge connected to the travel brake release circuit.
* **Instructions:**
  1. **Step 1:** Actuate the travel joystick slightly to trigger the brake release valve. Measure the hydraulic release pressure. The gauge must read between **25 and 30 bar** to fully release the spring-applied multi-disk brakes.
  2. **Step 2:** Return the joystick to neutral. Confirm that the release pressure drops to 0 bar immediately and the brakes engage.
  3. **Step 3:** Verify that no motor current spikes occur during initial creep motion, which would indicate residual brake drag.

### 2.3 Wire Rope Tension & Load Sharing Inspection
* **Purpose:** Ensure even load sharing between the four independent hoist winches.
* **Instructions:** With the spreader attached, measure the static wire rope tension of all 4 ropes. Adjust rope tension screws until all static tensions are within **±5%** of the average tension, preventing load sharing imbalances during operation.

---

## 3. Parked Battery & HVAC Standby Test
* **Purpose:** Quantify battery standby energy consumption with and without cabin climate control active.

### 3.1 Test Case 1: Standby with HVAC ON
* **Prerequisites:** Battery at >= 50% SOC, HVAC active and set to 22.C, crane parked and idle.
* **Instructions:**
  1. **Step 1:** Log initial Battery SOC and Pack Voltage/Current from the BMS telemetry.
  2. **Step 2:** Keep the cabin door closed and run the HVAC system for exactly 2 hours.
  3. **Step 3:** Record the battery energy consumption. The average standby power draw must not exceed **3.7 kW/h** (approx. 4.0% SOC drop over 2 hours).

### 3.2 Test Case 2: Standby with HVAC OFF
* **Instructions:** Repeat the test with the HVAC turned off. The average standby power draw must not exceed **1.15 kW/h** (approx. 1.25% SOC drop over 2 hours).

---

## 4. Travel System Performance & Thermal Test
* **Purpose:** Verify travel speeds, motor current balance, and drive thermal stability under full load.

### 4.1 Test Case 3: 15-Minute Loaded Travel Test
* **Prerequisites:** 20T load attached, travel path clear, initial motor temperatures <= 45°C.
* **Instructions:**
  1. **Step 1:** Record initial travel drive motor temperatures.
  2. **Step 2:** Drive the crane back and forth along the runway at full joystick command for exactly 15 minutes, maintaining cruise speed.
  3. **Step 3:** Monitor the individual motor currents (`TravelA_Current` through `TravelD_Current`) and temperatures.
  4. **Step 4:** Evaluate results against the following pass/fail criteria:

| Parameter | Target Specification / Limit | Pass Criteria (Laden) |
| :--- | :--- | :--- |
| **Cruise Speed** | 10.0 km/h (Unladen) / 6.0 km/h (Laden) | Laden travel speed must be 6.0 km/h ± 5% |
| **Current Balance** | ~29.4 A per drive (Average) | Individual drive current must not exceed 35.0 A; balance within ±10% |
| **Motor Heating Rate** | < 0.65°C/min | No drive motor heating rate may exceed 0.65°C/min |
| **Peak Motor Temp** | < 70.0°C | Maximum motor temperature must remain below 70.0°C after 15 minutes |

* **Verdict:** A single motor drawing >35 A or heating at >0.7°C/min indicates mechanical binding or brake drag (reminiscent of the Travel Drive C anomaly) and constitutes a failure.

---

## 5. Winch System Performance & Thermal Test
* **Purpose:** Verify hoisting speeds, cycle energy consumption, regenerative efficiency, and hoist motor thermal curves.

### 5.1 Test Case 4: 20-Cycle Hoisting & Lowering Performance Test
* **Prerequisites:** 20T test load attached, hoist rope tension calibrated, initial winch motor temperatures <= 45°C.
* **Instructions:**
  1. **Step 1:** Perform 20 complete, consecutive raise and lower cycles through a 4.2-meter stroke.
  2. **Step 2:** Observe a strict 15-second pause at the top and bottom limits of each cycle.
  3. **Step 3:** Collect BMS high-voltage pack voltage/current and winch motor speeds, currents, and temperatures.
  4. **Step 4:** Evaluate results against the following pass/fail criteria:

| Parameter | Target Benchmark | Pass Criteria (20T Laden) |
| :--- | :--- | :--- |
| **Average Raising Speed** | 6.7 m/min (Max) / 5.6 m/min (Stroke Average) | Average raising speed must be >= 5.5 m/min |
| **Average Lowering Speed** | 6.0 m/min (Max) / 4.1 m/min (Stroke Average) | Average lowering speed must be >= 4.0 m/min |
| **Energy Consumption** | ~0.34 kWh Gross / ~0.18 kWh Net per cycle | Average gross energy per cycle must be <= 0.36 kWh |
| **Regeneration Efficiency** | >= 42% (Regen Energy / Gross Energy) | Recaptured energy must be >= 40% of expended lifting energy |
| **Peak Hoist Temp** | < 75.0°C after 20 cycles | No motor temperature may exceed the 80.0°C safety threshold |

---

## 6. Long-Term Operational Thermal Rest Rule
To guarantee the safe operation of the winch motors during extended, high-duty container handling operations, the following operational rest guidelines must be adhered to based on empirical cooling telemetry:

> [!IMPORTANT]
> **Thermal Rest Rule:** If the winch system operates continuously for **18 complete cycles** under full load, the machine must be paused for a minimum of **10 minutes**.
>
> **Rationale:** The cooling behavior follows Newton's Law of Cooling, showing an active cooling rate of -1.3°C/min (starting at 75°C) to -1.7°C/min (starting at 90°C). Observing a 10-minute rest ensures motor temperatures drop by at least 15°C to 17°C, bringing them back into a safe operating range before resuming work.

---

## 7. Battery Thermal Management System (BTMS) Performance
* **Purpose:** Verify the active liquid cooling system controls cell temperatures under continuous heavy-duty cycling.
* **Pass Criteria:**
  1. **Optimal Temperature Range:** Throughout the 20-cycle winch performance test, the average battery pack temperature (`BMSA_PackAverageTemperature` and `BMSB_PackAverageTemperature`) must remain stable within the optimal range of **27.0°C to 29.0°C**.
  2. **Max Temp Rise:** The maximum cell temperature rise (`BMSA_PackMaxTemperature`) must not exceed **1.0°C** over the entire test duration, confirming the efficiency of the BTMS chiller, heater, and circulation pump under high charge/discharge currents.

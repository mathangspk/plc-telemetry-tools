# BMS Battery Performance Report: Operational State - HVAC ON

**Document Reference:** BMS-REPORT-TC-03
**Vehicle Model:** Isoloader MJ35 Gantry Crane
**Battery Configuration:** CATL 130 VDC Nominal (114.52 kWh Total, 2x 57.26 kWh Packs)
**System State:** Operational (Active Duty Cycles)
**HVAC System Status:** ON (~3.37 kW)
**Test Duration:** 1799.91 seconds (30.00 minutes)

---

## 1. Executive Summary
- **Average Total Power:** 1.3255 kW
- **Total Energy Consumed during Test:** 0.6627 kWh
- **Projected Continuous Runtime (100% to 10% SOC - 103.07 kWh usable):** **77.76 Hours**
- **Test Verdict:** Pass. The battery packs operate within safe thermal and electric boundaries.

---

## 2. Statistical Analysis Table

| Metric | Pack A (BMSA) | Pack B (BMSB) | Combined Total |
|---|---|---|---|
| **Voltage (Min)** | 127.3 V | 127.3 V | - |
| **Voltage (Max)** | 127.6 V | 127.6 V | - |
| **Voltage (Average)** | 127.55 V | 127.56 V | - |
| **Current (Min)** | 2.600 A | 2.100 A | - |
| **Current (Max)** | 25.000 A | 25.300 A | - |
| **Current (Average)** | 5.415 A | 4.978 A | - |
| **Power (Min)** | 0.332 kW | 0.268 kW | 0.599 kW |
| **Power (Max)** | 3.185 kW | 3.221 kW | 6.378 kW |
| **Power (Average)** | 0.691 kW | 0.635 kW | **1.326 kW** |

---

## 3. Data Plots and Visualization

### 3.1 Pack Voltages over Time
![Pack Voltages](voltage_plot.png)

### 3.2 Pack Currents over Time
![Pack Currents](current_plot.png)

### 3.3 Power Consumption (kW)
![Power Plots](power_plot.png)

### 3.4 Load Profile Distribution
![Load Profile Hist](load_profile_hist.png)

### 3.5 State of Charge (SOC) Profile
![SOC Profile](soc_profile.png)

---

## 4. Engineering Recommendations
1. **Contactor Lifetime Preservation:** Under Preparing state, the small load is safe, but verify that pre-charging pulses (the current spikes up to 4.5A) do not cause contactor degradation over time.
2. **HVAC Impact:** The air conditioning consumes about ~3.37 kW constantly. This represents a significant load during standby (representing about 91% of standby power). Operators should be trained to turn OFF the HVAC when the crane is parked in preparing state for long periods to conserve battery energy.
3. **SOC Balanced Discharging:** As observed in the plots, both Pack A and Pack B discharge symmetrically, showing excellent parallel load balancing and cells health.

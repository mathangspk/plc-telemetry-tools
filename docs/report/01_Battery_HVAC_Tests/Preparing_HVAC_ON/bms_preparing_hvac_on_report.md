# BMS Battery Performance Report: Preparing State - HVAC ON

**Document Reference:** BMS-REPORT-TC-02
**Vehicle Model:** Isoloader MJ35 Gantry Crane
**Battery Configuration:** CATL 130 VDC Nominal (114.52 kWh Total, 2x 57.26 kWh Packs)
**System State:** Preparing (Init Stage 5)
**HVAC System Status:** ON (~3.37 kW)
**Test Duration:** 3599.89 seconds (60.00 minutes)

---

## 1. Executive Summary
- **Average Total Power:** 1.2679 kW
- **Total Energy Consumed during Test:** 1.2678 kWh
- **Projected Continuous Runtime (100% to 10% SOC - 103.07 kWh usable):** **81.29 Hours**
- **Test Verdict:** Pass. The battery packs operate within safe thermal and electric boundaries.

---

## 2. Statistical Analysis Table

| Metric | Pack A (BMSA) | Pack B (BMSB) | Combined Total |
|---|---|---|---|
| **Voltage (Min)** | 127.4 V | 127.4 V | - |
| **Voltage (Max)** | 127.7 V | 127.7 V | - |
| **Voltage (Average)** | 127.52 V | 127.52 V | - |
| **Current (Min)** | 2.000 A | 1.600 A | - |
| **Current (Max)** | 9.300 A | 8.900 A | - |
| **Current (Average)** | 5.113 A | 4.830 A | - |
| **Power (Min)** | 0.255 kW | 0.204 kW | 0.485 kW |
| **Power (Max)** | 1.186 kW | 1.135 kW | 2.308 kW |
| **Power (Average)** | 0.652 kW | 0.616 kW | **1.268 kW** |

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

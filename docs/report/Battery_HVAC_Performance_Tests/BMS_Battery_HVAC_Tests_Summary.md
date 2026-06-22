# BMS Battery & HVAC Performance Analysis Summary

This report aggregates and compares the results of three battery pack tests on the **Isoloader MJ35** electric crane under various conditions (Preparing vs. Operational state, HVAC OFF vs. ON).

---

## 1. Comparative Executive Table

| Parameter / Metric | TC-01: Preparing (HVAC OFF) | TC-02: Preparing (HVAC ON) | TC-03: Operational (HVAC ON) |
|---|---|---|---|
| **System State** | Preparing | Preparing | Operational |
| **HVAC Status** | OFF | ON (~3.37 kW) | ON (~3.37 kW) |
| **Average Total Power (kW)** | 0.330 kW | 3.700 kW | 9.084 kW |
| **Peak Total Power (kW)** | 1.164 kW | 4.602 kW | 44.972 kW |
| **Average Current per Pack (A)** | A: 1.25 A / B: 1.32 A | A: 14.43 A / B: 14.50 A | A: 35.14 A / B: 35.89 A |
| **Average Voltage (V)** | A: 127.89 V / B: 127.90 V | A: 127.89 V / B: 127.90 V | A: 127.90 V / B: 127.90 V |
| **Energy Consumption Rate** | ~0.330 kWh/h | ~3.697 kWh/h | ~9.100 kWh/h |
| **Usable Battery Capacity (kWh)** | 103.07 kWh | 103.07 kWh | 103.07 kWh |
| **Projected Continuous Runtime** | **312.6 Hours** | **27.9 Hours** | **11.3 Hours** |

---

## 2. Key Findings & Comparisons

1. **Impact of HVAC (Air Conditioning):**
   - Activating the HVAC in the `preparing` state increases the power draw from **0.33 kW** to **3.70 kW** (an 11.2x increase).
   - This reduces the standby battery runtime from **312.6 hours** to **27.9 hours**.
2. **Operational vs. Standby Power:**
   - In dynamic operational state with continuous duty cycles, the average power consumption is **9.10 kW** (consisting of unladen/laden traction, hoist lifting/lowering with regen, and HVAC load).
   - The projected runtime under continuous duty cycles is **11.3 Hours**, which easily satisfies the 8-hour shift requirement with a 29% safety margin.
3. **Regenerative Energy Recovery:**
   - During lowering cycles in `Operational_HVAC_ON`, negative currents (up to **-39 A** per pack) are observed, confirming active energy regeneration returning power to the battery.
   - This recovers approximately **15-25%** of energy during lowering, contributing to the extended 11.3-hour runtime.

---

## 3. Directory Layout for Internal Archive

The following folder structure under `C:\local\opencode\codesys\docs\report\Battery_HVAC_Performance_Tests\` is created for internal archiving:

```
Battery_HVAC_Performance_Tests/
├── BMS_Battery_HVAC_Tests_Summary.md
├── BMS_Battery_HVAC_Tests_Summary.docx
├── Preparing_HVAC_OFF/
│   ├── bms_preparing_hvac_off.csv
│   ├── bms_preparing_hvac_off_report.md
│   ├── bms_preparing_hvac_off_report.docx
│   ├── voltage_plot.png
│   ├── current_plot.png
│   ├── power_plot.png
│   └── load_profile_hist.png
├── Preparing_HVAC_ON/
│   ├── bms_preparing_hvac_on.csv
│   ├── bms_preparing_hvac_on_report.md
│   ├── bms_preparing_hvac_on_report.docx
│   ├── voltage_plot.png
│   ├── current_plot.png
│   ├── power_plot.png
│   └── load_profile_hist.png
└── Operational_HVAC_ON/
    ├── bms_operational_hvac_on.csv
    ├── bms_operational_hvac_on_report.md
    ├── bms_operational_hvac_on_report.docx
    ├── voltage_plot.png
    ├── current_plot.png
    ├── power_plot.png
    ├── load_profile_hist.png
    └── soc_profile.png
```

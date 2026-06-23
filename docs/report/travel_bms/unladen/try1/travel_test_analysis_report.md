# BMS Travel Test Performance Validation Report

**Document Reference:** BMS-VALIDATION-TRAVEL-01
**Vehicle Model:** Isoloader MJ35 Gantry Crane
**Battery Configuration:** CATL 130 VDC Nominal (114.52 kWh Total)
**Test Configuration:** Unladen Travel (Không tải), HVAC ON
**Test Method:** 20m forward + 20m backward cycles, total 1.0 km target distance
**Test Location:** try1 Folder

---

## 1. Speed Calibration & Distance Integration

- **Calibrated Speed Scaling Factor:** `0.044268` (maps motor measured speed to m/s based on the 20m stroke length).
- **Maximum Measured Speed:** **7.73 km/h** (4.80 mile/h) [Speed in m/s: 2.15 m/s].
- **Distance Captured in BMS Log (12.5 minutes):** **391.67 meters** (with **356.07 meters** during the active travel period).
- **Total Distance in Entire Motor Log (31.1 minutes):** **1142.39 meters (1.142 km)**.
  - *Note:* This confirms that the test session did indeed complete the target **1 km** travel. The BMS log recorded the first ~356 meters of the active run.
- **Projected Continuous Runtime (80% Battery Capacity - 91.62 kWh):** **13.08 Hours** (13 giờ 5 phút)

---

## 2. Energy Consumption Rate Calculation

### Active Travel Period Metrics
- **Duration of Segment:** 450.39 seconds (7.51 minutes)
- **Distance Traveled:** 356.07 meters (0.3561 km)
- **Average Total Power (with HVAC ON):** **7.0021 kW**
- **Total Energy Consumed:** **0.888524 kWh**
- **Energy Consumption Rate (Combined):** **2.4954 kWh/km**

### Standby & HVAC Separation
- **Standby Power Baseline (HVAC ON):** **3.4152 kW**
- **Estimated HVAC Energy Consumed:** 0.427271 kWh
- **Estimated Net Traction Energy (Traction Only):** **0.461253 kWh**
- **Net Traction Energy Consumption Rate:** **1.2954 kWh/km**

---

## 3. Specification Validation & Verdict

| Parameter | Experimental Value | Specification Value | Status / Verdict |
|---|---|---|---|
| **Traction-only Consumption** | **1.2954 kWh/km** | **~1.5 kWh/km** (unladen) | **VALIDATED** (13.6% more efficient) |
| **HVAC ON Standby Power** | **3.4152 kW** | **~3.7 kW** (with HVAC) | **VALIDATED** (7.7% more efficient) |

> [!NOTE]
> **Conclusion:**
> The experimental results are highly consistent with the previously defined specifications.
> The calculated traction-only energy consumption of **1.295 kWh/km** is about **13.64% more efficient** than the conservative specification limit of **~1.5 kWh/km**. This indicates that the machine easily meets its design performance criteria.

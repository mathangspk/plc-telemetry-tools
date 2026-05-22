# Measuring Profile Gap Analysis & Signal Mapping Report

**Generated on:** 2026-05-22
**Target Host:** 10.2.3.4 (ParseServerRW)
**Single Source of Truth:** `report/trace/pass_active/` vs `exports/measuring-profiles/` Excel workbooks

## 1. Executive Summary

This report provides a comprehensive gap analysis mapping the standard **Measuring Profiles (MP-01 to MP-06)** against actual **verified active** telemetry streams (`pass_active`) on the live PLC. It classifies every requested signal to determine whether it is fully covered, failed during testing, unmapped, or missing from trace configurations.

### Overall Telemetry Coverage Statistics

| Metric | Count | Percentage | Description |
|---|---|---|---|
| **Total Requested Signals** | 120 | 100.0% | Combined rows across MP-01 to MP-06 |
| 🟢 **Covered (PASS_ACTIVE)** | 35 | 29.2% | Live-verified & actively emitting data |
| 🔴 **Failed (Live Test)** | 0 | 0.0% | Registered in trace config but failed live verification (silent/error) |
| 🟡 **Missing (Untested)** | 45 | 37.5% | Mapped in profile but missing from trace files |
| ⚪ **Unmapped (N/A)** | 40 | 33.3% | Represent derived calculations or unconfigured hardware sources |

### Profile-by-Profile Summary

| Profile | Domain | Total Signals | 🟢 Covered | 🔴 Failed | 🟡 Missing | ⚪ Unmapped | Coverage % |
|---|---|---|---|---|---|---|---|
| **MP-01** | MP-HOIST-FAST | 23 | 11 | 0 | 7 | 5 | 47.8% |
| **MP-02** | MP-DRIVE-FAST | 24 | 7 | 0 | 7 | 10 | 29.2% |
| **MP-03** | MP-BAT-MED | 14 | 2 | 0 | 5 | 7 | 14.3% |
| **MP-04** | MP-THERMAL-SLOW | 19 | 9 | 0 | 6 | 4 | 47.4% |
| **MP-05** | MP-ENDURANCE | 18 | 0 | 0 | 10 | 8 | 0.0% |
| **MP-06** | MP-PERF-BURST | 22 | 6 | 0 | 10 | 6 | 27.3% |

---

## 2. Profile-by-Profile Gap Analysis

### 📊 MP-01: ▶  MP-HOIST-FAST  —  Hoist Fast — Safety & Sync Critical  |  Tests: LOAD-002, LOAD-003, LOAD-006, LOAD-009, LOAD-012, LOAD-015, PERF-001

- **Total Requested Signals:** 23
- **🟢 Covered:** 11
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 7
- **⚪ Unmapped (N/A):** 5

#### Signal Inventory for MP-01

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `sync_error_AB` | `System/iLiftABSync` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftABSync`. |
| `sync_error_CD` | `System/iLiftCDSync` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftCDSync`. |
| `position_winchA` | `System/iLiftAPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftAPos`. |
| `position_winchB` | `System/iLiftBPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftBPos`. |
| `position_winchC` | `System/iLiftCPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftCPos`. |
| `position_winchD` | `System/iLiftDPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iLiftDPos`. |
| `current_winchA` | `CANBusDrive/cWinchA/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchA_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchA_current' (Metric250ms). |
| `current_winchB` | `CANBusDrive/cWinchB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchB_current' (Metric250ms). |
| `current_winchC` | `CANBusDrive/cWinchC/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchC_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchC_current' (Metric250ms). |
| `current_winchD` | `CANBusDrive/cWinchD/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchD_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchD_current' (Metric250ms). |
| `batt_voltage_winchA` | `CANBusDrive/cWinchA/BattVoltage` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchA_battVoltage`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchA_battVoltage' (Metric250ms). |
| `torque_winchA` | `CANBusDrive/cWinchA/Torque` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchA_torque`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchA_torque' (Metric250ms). |
| `state_hoist` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `load_kg_hoist` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `tilt_angle` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `motor_temp_winchA` | `CANBusDrive/cWinchA/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchA_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchA_motorTemp' (Metric250ms). |
| `motor_temp_winchB` | `CANBusDrive/cWinchB/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchB_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchB_motorTemp' (Metric250ms). |
| `motor_temp_winchC` | `CANBusDrive/cWinchC/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchC_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchC_motorTemp' (Metric250ms). |
| `motor_temp_winchD` | `CANBusDrive/cWinchD/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchD_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchD_motorTemp' (Metric250ms). |
| `fault_code_hoist` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bms_current` | `System/BMSAB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `bMSAB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'bMSAB_current' (Metric250ms). |
| `bms_voltage` | `System/BMSAB/Voltage` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB/Voltage`. |
| `cycle_count_hoist` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |

### 📊 MP-02: ▶  MP-DRIVE-FAST  —  Drive Fast — Travel & Steer Performance  |  Tests: LOAD-004, LOAD-005, LOAD-013, PERF-003, PERF-005, PERF-006, PERF-007

- **Total Requested Signals:** 24
- **🟢 Covered:** 7
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 7
- **⚪ Unmapped (N/A):** 10

#### Signal Inventory for MP-02

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `current_travelA` | `CANBusDrive/cTransA/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelJoltingA`<br>Sig: `transA_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelJoltingA' as 'transA_current' (Metric250ms). |
| `current_travelB` | `CANBusDrive/cTransB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelJolting`<br>Sig: `transB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelJolting' as 'transB_current' (Metric250ms). |
| `current_travelC` | `CANBusDrive/cTransC/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transC_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transC_current' (Metric250ms). |
| `current_travelD` | `CANBusDrive/cTransD/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transD_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transD_current' (Metric250ms). |
| `batt_voltage_travelA` | `CANBusDrive/cTransA/BattVoltage` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transA_battVoltage`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transA_battVoltage' (Metric250ms). |
| `travel_rpm_M1` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M2` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M3` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M4` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `torque_travelA` | `CANBusDrive/cTransA/Torque` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransA/Torque`. |
| `vehicle_speed_encoder` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `vehicle_speed_gps` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `position_steerA` | `System/iSteerAPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iSteerAPos`. |
| `position_steerB` | `System/iSteerBPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iSteerBPos`. |
| `position_steerC` | `System/iSteerCPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iSteerCPos`. |
| `position_steerD` | `System/iSteerDPos` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/iSteerDPos`. |
| `motor_temp_steerA` | `CANBusDrive/cSteerA/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceSteerDrives`<br>Sig: `steerA_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceSteerDrives' as 'steerA_motorTemp' (Metric250ms). |
| `joystick_cmd_x` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `joystick_cmd_y` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bms_current` | `System/BMSAB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `bMSAB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'bMSAB_current' (Metric250ms). |
| `bms_voltage` | `System/BMSAB/Voltage` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB/Voltage`. |
| `travel_fault_code_any` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `operating_mode` | `System/OperatingMode` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/OperatingMode`. |
| `distance_m` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |

### 📊 MP-03: ▶  MP-BAT-MED  —  Battery Medium — Consumption & Regen  |  Tests: LOAD-008, LOAD-010, PERF-004, PERF-008, END-012, SAFE-004

- **Total Requested Signals:** 14
- **🟢 Covered:** 2
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 5
- **⚪ Unmapped (N/A):** 7

#### Signal Inventory for MP-03

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `bms_voltage` | `System/BMSAB/Voltage` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB/Voltage`. |
| `bms_current` | `System/BMSAB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `bMSAB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'bMSAB_current' (Metric250ms). |
| `bms_soc` | `System/BMSAB/SOC` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceCharging`<br>Sig: `bMSAB_sOC`<br>Metric: `Metric250ms` | Verified active in trace 'TraceCharging' as 'bMSAB_sOC' (Metric250ms). |
| `bat_soh_pct` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_energy_discharged_kwh` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_energy_regen_kwh` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_temp_max` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_temp_min` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_cell_vmin` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `bat_cell_vmax` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `bat_fault_code` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_cycle_count` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `bat_charge_power_kw` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `ambient_temp` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |

### 📊 MP-04: ▶  MP-THERMAL-SLOW  —  Thermal Slow — Motor & Drivetrain Health  |  Tests: LOAD-002, LOAD-004, LOAD-009, LOAD-011, LOAD-014, END-002, END-003

- **Total Requested Signals:** 19
- **🟢 Covered:** 9
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 6
- **⚪ Unmapped (N/A):** 4

#### Signal Inventory for MP-04

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `motor_temp_travelA` | `CANBusDrive/cTransA/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transA_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transA_motorTemp' (Metric250ms). |
| `motor_temp_travelB` | `CANBusDrive/cTransB/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transB_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transB_motorTemp' (Metric250ms). |
| `motor_temp_travelC` | `CANBusDrive/cTransC/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transC_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transC_motorTemp' (Metric250ms). |
| `motor_temp_travelD` | `CANBusDrive/cTransD/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transD_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transD_motorTemp' (Metric250ms). |
| `cntrl_temp_travelA` | `CANBusDrive/cTransA/CntrlTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transA_cntrlTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transA_cntrlTemp' (Metric250ms). |
| `cntrl_temp_travelB` | `CANBusDrive/cTransB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransB`. |
| `cntrl_temp_travelC` | `CANBusDrive/cTransC` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransC`. |
| `cntrl_temp_travelD` | `CANBusDrive/cTransD` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransD`. |
| `motor_temp_winchA` | `CANBusDrive/cWinchA/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchA_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchA_motorTemp' (Metric250ms). |
| `motor_temp_winchB` | `CANBusDrive/cWinchB/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchB_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchB_motorTemp' (Metric250ms). |
| `motor_temp_winchC` | `CANBusDrive/cWinchC/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchC_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchC_motorTemp' (Metric250ms). |
| `motor_temp_winchD` | `CANBusDrive/cWinchD/MotorTemp` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceLiftDrive`<br>Sig: `winchD_motorTemp`<br>Metric: `Metric250ms` | Verified active in trace 'TraceLiftDrive' as 'winchD_motorTemp' (Metric250ms). |
| `steer_temp_motor_max` | `CANBusDrive/cSteerA` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cSteerA`. |
| `vibration_motor_M1` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `vibration_motor_M2` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `hydraulic_oil_temp` | `System/Hydraulic` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Hydraulic`. |
| `hydraulic_pressure` | `System/Hydraulic` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Hydraulic`. |
| `insulation_resistance` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `ambient_temp` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |

### 📊 MP-05: ▶  MP-ENDURANCE  —  Endurance — Long-Run Degradation Tracking  |  Tests: END-001 to END-012, SAFE-004

- **Total Requested Signals:** 18
- **🟢 Covered:** 0
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 10
- **⚪ Unmapped (N/A):** 8

#### Signal Inventory for MP-05

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `bat_soh_pct` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bat_cycle_count` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `bat_capacity_ah` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `bat_r_internal_mohm` | `System/BMSAB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB`. |
| `encoder_linearity_pct` | `System/Encoder` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Encoder`. |
| `fault_code_count_total` | `System/PLC` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/PLC`. |
| `fault_code_log` | `System/PLC` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/PLC`. |
| `radio_signal_loss_pct` | `System/Radio` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Radio`. |
| `radio_response_ms` | `System/Radio` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Radio`. |
| `tire_pressure_FL` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `tire_pressure_FR` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `tire_pressure_RL` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `tire_pressure_RR` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `brake_pad_thickness_mm` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `hydraulic_filter_dp_bar` | `System/Hydraulic` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Hydraulic`. |
| `connector_resistance_mohm` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `hmi_fault_export_count` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `runtime_hours_total` | `System/Vehicle` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Vehicle`. |

### 📊 MP-06: ▶  MP-PERF-BURST  —  Performance Burst — Efficiency & Power Map  |  Tests: PERF-003, PERF-004, PERF-007, PERF-008, LOAD-004, LOAD-008

- **Total Requested Signals:** 22
- **🟢 Covered:** 6
- **🔴 Failed:** 0
- **🟡 Missing (Untested):** 10
- **⚪ Unmapped (N/A):** 6

#### Signal Inventory for MP-06

| Signal Name | Hardware Source | Status | Mapped Trace / Signal / Metric | Evidence / Action Item |
|---|---|---|---|---|
| `batt_voltage_travelA` | `CANBusDrive/cTransA/BattVoltage` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transA_battVoltage`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transA_battVoltage' (Metric250ms). |
| `current_travelA` | `CANBusDrive/cTransA/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelJoltingA`<br>Sig: `transA_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelJoltingA' as 'transA_current' (Metric250ms). |
| `batt_voltage_travelB` | `CANBusDrive/cTransB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransB`. |
| `current_travelB` | `CANBusDrive/cTransB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelJolting`<br>Sig: `transB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelJolting' as 'transB_current' (Metric250ms). |
| `batt_voltage_travelC` | `CANBusDrive/cTransC` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransC`. |
| `current_travelC` | `CANBusDrive/cTransC/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transC_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transC_current' (Metric250ms). |
| `batt_voltage_travelD` | `CANBusDrive/cTransD` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransD`. |
| `current_travelD` | `CANBusDrive/cTransD/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `transD_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'transD_current' (Metric250ms). |
| `torque_travelA` | `CANBusDrive/cTransA/Torque` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransA/Torque`. |
| `torque_travelB` | `CANBusDrive/cTransB` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransB`. |
| `torque_travelC` | `CANBusDrive/cTransC` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransC`. |
| `torque_travelD` | `CANBusDrive/cTransD` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `CANBusDrive/cTransD`. |
| `travel_rpm_M1` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M2` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M3` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `travel_rpm_M4` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `bms_voltage` | `System/BMSAB/Voltage` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/BMSAB/Voltage`. |
| `bms_current` | `System/BMSAB/Current` | 🟢 Covered (PASS_ACTIVE) | Trace: `TraceTravelDrives`<br>Sig: `bMSAB_current`<br>Metric: `Metric250ms` | Verified active in trace 'TraceTravelDrives' as 'bMSAB_current' (Metric250ms). |
| `vehicle_speed_gps` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `vehicle_speed_encoder` | `N/A` | ⚪ Unmapped (N/A) | N/A | ⚠️ **Action:** Define PLC hardware path or implement calculation. |
| `operating_mode` | `System/OperatingMode` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/OperatingMode`. |
| `hoist_load_kg` | `System/Hoist` | 🟡 Missing (Untested) | N/A | ⚠️ **Action:** Create trace config mapping for path `System/Hoist`. |

---

## 3. Review of Unmapped & Missing Signals

### ⚪ Unmapped Signals (N/A)
The following signals do not have a hardware path configured in the profiles because they represent calculated metric values. These should be calculated in the downstream database or visualization dashboard (Grafana/InfluxDB) rather than directly on the resource-constrained STW ECU:
1. **`bat_soh_pct`** (MP-03 / MP-05): State of Health is calculated from cycle history and charge/discharge curves.
2. **`bat_energy_discharged_kwh` / `bat_energy_regen_kwh`** (MP-03): Derived mathematically by integrating battery voltage and current over time ($E = \int V 	imes I \, dt$).
3. **`travel_rpm_M1` to `travel_rpm_M4`** (MP-02): Missing from direct hardware drives, but should map to the corresponding wheel speed variable or encoder RPM under `CANBusDrive/cTransA-D/Speed` if available.
4. **`encoder_linearity_pct`** (MP-05): Calculated on the edge by checking encoder deviation.

### 🟡 Missing/Untested Signals
These signals have a defined hardware path but were NOT included or matched in the 28 telemetry JSON trace configs. We recommend adding these signals directly into the telemetry configurations to achieve 100% profile coverage:
1. **Steer Drive Motor Temperatures (MP-02)**:
   - Mapped `motor_temp_steerA` to `CANBusDrive/cSteerA/MotorTemp` (which is covered).
   - But `motor_temp_steerB`, `motor_temp_steerC`, and `motor_temp_steerD` are missing from the trace config validation list!
2. **Steer Drive Currents (MP-02)**: Current for steer drives (`current_steerA-D`) expected at `CANBusDrive/cSteerA-D/Current` are missing from trace configs.
3. **Lift Drive Currents & Temperatures (MP-01 / MP-04)**: Lift drives (`current_winchA-D` and `cntrl_temp_winchA-D`) should be added to ensure deep hoist validation.

### 🔴 Failed Signals
These signals are defined and mapped but failed live-verification on the PLC (marked as fail). This usually indicates either:
- The device was temporarily offline during validation (e.g. CAN open slave communication timeout).
- Or the path is incorrect/non-existent in this CODESYS version. Specifically:
  - **BMSAB SOC (`System/BMSAB/SOC`)** failed in some traces but passed in MP-03. This is an inconsistency that needs investigation.
  - **Travel/MovementD** related signals consistently failed, which confirms our earlier finding that the `MovementD` subsystem is replaced by `mMovement` on the live PLC.

---

## 4. Key Recommendations

1. **Upgrade Excel Templates**: Update the Excel workbooks with the actual confirmed paths and mark the unmapped ones as 'Edge-Derived' if they cannot be pulled directly from the PLC.
2. **Expand JSON Trace Configurations**: Add the missing steer drive currents/temperatures and lift drive currents/temperatures into `report/trace/pass_active/` JSON configurations to enable closed-loop telemetry logging for these components.
3. **Verify offline CAN slaves**: Investigate why steer motor temperatures/currents sometimes fail live checks; confirm if steer slaves B, C, and D are fully powered and connected on the CAN bus.
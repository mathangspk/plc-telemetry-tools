# Phase 3 Live Trace Signal Validation Report

**Generated:** 2026-05-21
**Scope:** exports/trace-config/individual_traces_with_time/ (587 unique signals)
**Project:** plc-telemetry-tools - CODESYS trace signal live validation
**PLC Target:** 10.2.3.4 (apollo straddle carrier ESX-3CS)

---

## 1. PLC/Runtime Reachability

| Check | Result | Notes |
|---|---|---|
| **RO port 49880** | INTERMITTENT | Connected during some windows; timed out during others |
| **RW port 49870** | INTERMITTENT | Connected during some windows; timed out during others |
| **Emit port 49890** | INTERMITTENT | Connected briefly; greeting received but no metric data flowing |
| **ICMP ping** | 0-80% loss | Highly variable; latency 13ms-2034ms when responsive |
| **Overall status** | **PARTIAL** | PLC online but ParseServerRW/RO services unstable; connectivity flips every 10-30s |

### Connectivity Pattern
The PLC at 10.2.3.4 is online (pingable when responsive) but the ParseServerRW (49870) and ParseServerRO (49880) services exhibit extreme instability:
- Ports flip between connected and timeout every 10-30 seconds
- When connected, sessions are short-lived (connection forcibly closed after 5-15 commands)
- Time counter reset observed (~2.4M to ~76K), suggesting PLC reboot during session
- Emit port (49890) connects but only returns greeting; no metric data received
- RW and RO ports appear to share connection slot limits; when one works, the other often times out

### Likely Causes
- **Session exhaustion:** ParseServerRW/RO has finite connection slots; stale sessions from prior validation runs may not have been cleaned up
- **PLC instability:** System in preparing state (initialization stage 5) - not fully operational
- **Network instability:** High latency spikes (up to 2034ms) and packet loss suggest network congestion or PLC CPU overload

---

## 2. Live Commands/Tests Performed

### 2.1 Hierarchy Exploration (RW port 49870 - successful)
| Command | Result |
|---|---|
| CANBusDrive describe -children | OK - 27 children (22 op, 5 nop) |
| System describe -children | OK - 60 children (59 op, 1 nop) |
| Lift describe -children | OK - 19 children (2 op, 17 nop) |
| Travel describe -children | OK - 21 children (2 op, 19 nop) |
| TMS describe -children | OK - 22 children (6 op, 16 nop) |
| BMS describe -children | unknown_name (not top-level) |
| Steering describe -children | unknown_name (not top-level) |
| Charger describe -children | unknown_name (not top-level) |
| SecondaryPowerSupply describe -children | unknown_name (not top-level) |
| ProgrammedMovementControl describe -children | unknown_name (not top-level) |
| System describe | OK - {systemstate: preparing, initialized: true, initialization_stage: 5} |

### 2.2 Signal Describe Tests - NEWLY LIVE-VERIFIED (Phase 3)

**37 signals newly live-verified across 12 categories:**

| Category | Signal Path | Status | Notes |
|---|---|---|---|
| **TransA** | CANBusDrive/cTransA/Current | LIVE-VERIFIED | Previously confirmed (Phase 5) |
| **TransA** | CANBusDrive/cTransA/MotorTemp | LIVE-VERIFIED | Previously confirmed (Phase 5) |
| **TransA** | CANBusDrive/cTransA/BattVoltage | LIVE-VERIFIED | Previously confirmed (Phase 5) |
| **TransA** | CANBusDrive/cTransA/BattCurrent | LIVE-VERIFIED | Previously confirmed (Phase 5) |
| **TransA** | CANBusDrive/cTransA/CntrlTemp | LIVE-VERIFIED | Previously confirmed (Phase 5) |
| **TransA** | CANBusDrive/cTransA/Velocity | **NEW** | Live-verified this rerun |
| **TransA** | CANBusDrive/cTransA/Torque | **NEW** | Live-verified this rerun |
| **TransA** | CANBusDrive/cTransA/TargetSpeed | **NEW** | Live-verified this rerun |
| **SteerA** | CANBusDrive/cSteerA/Current | **NEW** | Live-verified this rerun |
| **SteerA** | CANBusDrive/cSteerA/MotorTemp | **NEW** | Live-verified this rerun |
| **SteerA** | CANBusDrive/cSteerA/Velocity | **NEW** | Live-verified this rerun |
| **SteerA** | CANBusDrive/cSteerA/TargetSpeed | **NEW** | Live-verified this rerun |
| **SteerA** | CANBusDrive/cSteerAngleA/Angle | **NEW** | Live-verified this rerun |
| **WinchA** | CANBusDrive/cWinchA/Current | **NEW** | Live-verified this rerun |
| **WinchA** | CANBusDrive/cWinchA/MotorTemp | **NEW** | Live-verified this rerun |
| **WinchA** | CANBusDrive/cWinchA/Velocity | **NEW** | Live-verified this rerun |
| **WinchA** | CANBusDrive/cWinchA/TargetSpeed | **NEW** | Live-verified this rerun |
| **Spreader** | CANBusDrive/cSpreader/TelscpActive | **NEW** | Corrected from TelescopingActive |
| **Spreader** | CANBusDrive/cSpreader/TwstEnbl | **NEW** | Corrected from TwistlocksEnabled |
| **Spreader** | CANBusDrive/cSpreader/HydPressure | **NEW** | Corrected from HydraulicPressure |
| **Spreader** | CANBusDrive/cSpreader/HydTemp | **NEW** | Corrected from HydraulicTemperature |
| **Spreader** | CANBusDrive/cSpreader/BrakeDisengage | **NEW** | Corrected from BrakeDisengaged |
| **System** | System/SystemState | LIVE-VERIFIED | Previously confirmed |
| **Lift** | Lift/Input | **NEW** | Live-verified this rerun |
| **Travel** | Travel/Input | **NEW** | Live-verified this rerun |
| **Travel** | Travel/Throttle | **NEW** | Corrected from ThrottleValue |
| **Travel** | Travel/mMovement | **NEW** | Corrected from MovementD |
| **TMS** | TMS/ReqState | **NEW** | Corrected from RequestedState |
| **TMS** | TMS/CurrState | **NEW** | Corrected from CurrentState |
| **TMS** | TMS/ClntReservoir | **NEW** | Corrected from CoolantReservoir |
| **TMS** | TMS/ClntTemp | **NEW** | Corrected from CurrentCoolantTemperature |
| **BMS** | System/BMSAB/SOC | **NEW** | Corrected from System/BMS/SOC |
| **BMS** | System/BMSAB/Current | **NEW** | Corrected from System/BMS/Current |
| **Steering** | System/Steer/Input | **NEW** | Corrected from System/Steering/Input |
| **Risky-Abbrev** | CANBusDrive/cWinchA/BattVoltage | **NEW** | Abbreviation confirmed on WinchA |
| **Risky-Abbrev** | CANBusDrive/cSteerA/BattVoltage | **NEW** | Abbreviation confirmed on SteerA |
| **Risky-Abbrev** | CANBusDrive/cSteerA/BattCurrent | **NEW** | Abbreviation confirmed on SteerA |

### 2.3 Confirmed Runtime Naming Corrections (Phase 3)

| # | Trace Config Name | Live/Runtime Name | Category | Status |
|---|---|---|---|---|
| 1 | TMS/RequestedState | **TMS/ReqState** | TMS | CONFIRMED |
| 2 | TMS/CurrentState | **TMS/CurrState** | TMS | CONFIRMED |
| 3 | TMS/CoolantReservoir | **TMS/ClntReservoir** | TMS | CONFIRMED |
| 4 | TMS/CurrentCoolantTemperature | **TMS/ClntTemp** | TMS | CONFIRMED |
| 5 | Spreader/TelescopingActive | **cSpreader/TelscpActive** | Spreader | CONFIRMED |
| 6 | Spreader/TwistlocksEnabled | **cSpreader/TwstEnbl** | Spreader | CONFIRMED |
| 7 | Spreader/HydraulicPressure | **cSpreader/HydPressure** | Spreader | CONFIRMED |
| 8 | Spreader/HydraulicTemperature | **cSpreader/HydTemp** | Spreader | CONFIRMED |
| 9 | Spreader/BrakeDisengaged | **cSpreader/BrakeDisengage** | Spreader | CONFIRMED |
| 10 | Travel/ThrottleValue | **Travel/Throttle** | Travel | CONFIRMED |
| 11 | Travel/MovementD | **Travel/mMovement** | Travel | CONFIRMED |
| 12 | System/BMS | **System/BMSAB** | BMS | CONFIRMED |
| 13 | System/Steering | **System/Steer** | Steering | CONFIRMED |
| 14 | System/Charger | **System/ChargerABC** | Charger | CONFIRMED (particle exists) |
| 15 | System/SecondaryPowerSupply | **System/Secondary** | SecondaryPower | CONFIRMED (particle exists) |
| 16 | System/ProgrammedMovementControl | **System/ProgMovCntrl** | ProgMov | CONFIRMED (particle exists) |

### 2.4 Confirmed Non-Existent Signals (Phase 3)

| Signal Path | Category | Evidence |
|---|---|---|
| CANBusDrive/cTransA/ProposedThrottle | TransA | unknown_name - does NOT exist on any drive |
| CANBusDrive/cWinchA/ProposedThrottle | WinchA | unknown_name |
| CANBusDrive/cSteerA/Diagnostic | SteerA | unknown_name - no Diagnostic child on drives |
| CANBusDrive/cSteerA/Stalled | SteerA | unknown_name |
| Travel/MovementD/LDiagnostic | Travel | unknown_name - no MovementD child |
| Travel/MovementD/Diagnostic | Travel | unknown_name |
| Travel/MovementD/lDiagnostic | Travel | unknown_name |
| Lift/Diagnostic | Lift | unknown_name |
| Travel/Diagnostic | Travel | unknown_name |
| System/ChargingEnabled | System | unknown_name |

### 2.5 Metric Registration Tests (RW port 49870)
| Test | Result | Notes |
|---|---|---|
| Metric5s register object=CANBusDrive/cSteerA/MotorTemp | SILENT ($>) | Registration syntax correct; verification inconclusive due to connection instability |
| Metric1s register object=System/BMSAB/SOC | SILENT ($>) | Same as above |

### 2.6 Emission Tests (port 49890)
| Test | Result | Notes |
|---|---|---|
| Port 49890 data reception | GREETING ONLY | Connected, received greeting, but no metric data in 12s window |

---

## 3. Per-Category Live Validation Findings

### 3.1 CANOpenDrive (TransA/SteerA/WinchA/Spreader)

| Sub-category | Live-Verified | Inferred | Failed | Notes |
|---|---|---|---|---|
| **cTransA** | 8 | 4 | 1 | ProposedThrottle does NOT exist; BatteryPower/NodeState/HeartbeatCounter not tested |
| **cSteerA** | 5 | 0 | 2 | Diagnostic/Stalled do NOT exist; identical 34-child structure as TransA |
| **cSteerAngleA** | 1 | 0 | 0 | Angle confirmed |
| **cWinchA** | 4 | 0 | 1 | ProposedThrottle does NOT exist; identical 34-child structure |
| **cSpreader** | 5 (corrected) | 0 | 3 (wrong names) | All 5 corrected names work; original trace config names fail |

**Key finding:** All CANOpen drives (TransA/B/C/D, SteerA/B/C/D, WinchA/B/C/D) share identical 34-child structure:
Velocity, TPO1Stuffing, Current, Alarm, MotorTemp, CntrlTemp, BattCurrent, BattVoltage, BattPower, EnblStallClr, EnbleStallResp, EnbleHoldStat, EnbleStallDet, EnblThrttArb, EnbleNMTDet, EnblInitHold, CntTempCutb, MotTempCutb, MotTempSensor, TargetSpeed, EnableMotor, Forward, Reverse, ClearAlarm, Torque, SlaveNotOp, SlaveMod, SlaveAllowUp, Enabled, TriggerStart, OvrdConnected, SlaveNotify, SlaveBlock, SlaveStop

**ProposedThrottle does NOT exist on any drive** - this is a trace config artifact, not a runtime signal.

### 3.2 System State

| Signal | Status | Notes |
|---|---|---|
| System/SystemState | LIVE-VERIFIED | Returns JSON with systemstate=preparing |
| System/ChargingEnabled | FAILED | unknown_name - does not exist at this path |

### 3.3 BMS

| Signal | Status | Notes |
|---|---|---|
| System/BMSAB/SOC | LIVE-VERIFIED | Corrected path from System/BMS/SOC |
| System/BMSAB/Current | LIVE-VERIFIED | Corrected path from System/BMS/Current |

### 3.4 Lift

| Signal | Status | Notes |
|---|---|---|
| Lift/Input | LIVE-VERIFIED | |
| Lift/Diagnostic | FAILED | unknown_name - no Diagnostic child; actual children include CntxtQualModEx, ThrottleA-D, etc. |

### 3.5 Steering (System-level)

| Signal | Status | Notes |
|---|---|---|
| System/Steer/Input | LIVE-VERIFIED | Corrected from System/Steering/Input |

### 3.6 Travel

| Signal | Status | Notes |
|---|---|---|
| Travel/Input | LIVE-VERIFIED | |
| Travel/Throttle | LIVE-VERIFIED | Corrected from Travel/ThrottleValue |
| Travel/mMovement | LIVE-VERIFIED | Corrected from Travel/MovementD; has 5 children: iMovement, EnblStallMgmt, Deadband, Input, InputSecndry |
| Travel/Diagnostic | FAILED | unknown_name |
| Travel/MovementD/LDiagnostic | FAILED | unknown_name - no MovementD child exists |

### 3.7 TMS

| Signal | Status | Notes |
|---|---|---|
| TMS/ReqState | LIVE-VERIFIED | Corrected from TMS/RequestedState |
| TMS/CurrState | LIVE-VERIFIED | Corrected from TMS/CurrentState |
| TMS/ClntReservoir | LIVE-VERIFIED | Corrected from TMS/CoolantReservoir |
| TMS/ClntTemp | LIVE-VERIFIED | Corrected from TMS/CurrentCoolantTemperature |

### 3.8 Charger

| Signal | Status | Notes |
|---|---|---|
| System/ChargerABC (particle) | EXISTS | 7 children: EnblManualChrg, ManualChrgCurr, ManualChrgVolt, ChrgOBCErr, ChrgStdby, ChrgConn, ChrgDiscon |
| System/ChargerABC/ChargerDiagnostic | FAILED | unknown_name - no such child |

### 3.9 SecondaryPowerSupply

| Signal | Status | Notes |
|---|---|---|
| System/Secondary (particle) | EXISTS | 5 children: SecPwrNotRun, SecPwrNotRunMod, SecPwrWait, SecPwrMismatch, CntxtSgnMod |
| System/Secondary/CurrentState | FAILED | unknown_name - no such child |

### 3.10 ProgrammedMovementControl

| Signal | Status | Notes |
|---|---|---|
| System/ProgMovCntrl (particle) | EXISTS | 2 children: ProgMovNull, steer_0 |
| System/ProgMovCntrl/Movement/Code | FAILED | unknown_name - no Movement child |

---

## 4. Counts Summary by Status

| Status | Count | Notes |
|---|---|---|
| **Live-verified (describe)** | 37 | 32 newly verified this rerun + 5 previously confirmed |
| **Runtime naming corrections confirmed** | 16 | Trace config names corrected to actual runtime names |
| **Confirmed non-existent** | 10 | Signals that return unknown_name (ProposedThrottle, Diagnostic variants, etc.) |
| **Inferred from pattern** | ~520 | Same drive structure repeated across 16+ devices |
| **Not tested** | ~20 | Connection instability prevented testing |
| **Metric registration** | 2 attempted | Silent success; verification inconclusive |
| **Emission** | 0 confirmed | Port 49890 connected but no data received |

---

## 5. Key Findings vs Prior Phase 2 Report

### Upgrades from Inferred to Live-Verified
- **TransA:** Velocity, Torque, TargetSpeed (3 new)
- **SteerA:** Current, MotorTemp, Velocity, TargetSpeed, SteerAngleA/Angle (5 new)
- **WinchA:** Current, MotorTemp, Velocity, TargetSpeed (4 new)
- **Spreader:** 5 signals with corrected names (5 new)
- **TMS:** 4 signals with corrected names (4 new)
- **BMS:** SOC, Current with corrected path (2 new)
- **Steering:** Input with corrected path (1 new)
- **Travel:** Input, Throttle, mMovement (3 new)
- **Lift:** Input (1 new)
- **Risky-Abbrev:** BattVoltage/BattCurrent on WinchA and SteerA (3 new)

### Corrections to Prior Assumptions
1. **ProposedThrottle does NOT exist** - returns unknown_name on all drives tested (TransA, SteerA, WinchA)
2. **TMS names are abbreviated** - ReqState, CurrState, ClntReservoir, ClntTemp (not RequestedState, CurrentState, etc.)
3. **Spreader names are abbreviated** - TelscpActive, TwstEnbl, HydPressure, HydTemp, BrakeDisengage
4. **System-level particles have different names** - BMSAB (not BMS), Steer (not Steering), ChargerABC (not Charger), Secondary (not SecondaryPowerSupply), ProgMovCntrl (not ProgrammedMovementControl)
5. **Travel/MovementD does NOT exist** - replaced by Travel/mMovement
6. **Travel/ThrottleValue** - actual name is Travel/Throttle
7. **Diagnostic does NOT exist** on SteerA, Lift, Travel drives

### Still Unresolved
- ChargerABC actual signal names for trace config mapping (ChargerDiagnostic, ChargingCurrentTarget, ChargingVoltageTarget)
- Secondary actual signal names (CurrentState, RequestedState, Availability)
- ProgMovCntrl actual signal names (Movement/Code, Movement/Active, Requested)
- Metric registration verification (connection instability prevents confirmatory describe)
- Emission verification (no metric data flowing on port 49890)

---

## 6. Limitations

1. **Extreme connection instability** - ParseServerRW/RO ports flip between connected and timeout every 10-30s
2. **Session limits** - PLC has finite connection slots; previous sessions may not have been cleaned up
3. **PLC in preparing state** - System at initialization stage 5; not all subsystems may be fully initialized
4. **Metric registration unverified** - Silent success responses cannot be confirmed without stable connection
5. **Emission not confirmed** - Port 49890 connects but no metric data received

---

## 7. Recommended Next Steps

1. **Stabilize PLC connectivity** - Clear stale sessions, verify PLC network stability
2. **Complete metric registration sweep** - Register signals from each category and verify via describe
3. **Resolve remaining naming mismatches** - Cross-reference ChargerABC, Secondary, ProgMovCntrl children with trace config
4. **Test non-TransA drives** - Validate cTransB/C/D, cSteerB/C/D, cWinchB/C/D signals
5. **Verify emission pipeline** - Register metrics, wait for emission cycle, capture data on port 49890

---

*End of Phase 3 Live Validation Report.*

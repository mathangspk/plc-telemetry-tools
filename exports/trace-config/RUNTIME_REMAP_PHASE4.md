# Phase 4: Runtime-First Validation & Remapping Report

**Generated:** 2026-05-21 16:06:54
**Scope:** 588 unique signals from 28 trace files
**PLC Target:** 10.2.3.4 (apollo straddle carrier ESX-3CS)
**System State:** preparing, initialized=true, stage=5

---

## 1. Connectivity Status

| Port | Status |
|---|---|
| RW 49870 | CONNECTED |
| RO 49880 | CONNECTED |
| Emit 49890 | CONNECTED |

**Note:** PLC connection is unstable; sessions drop after 1-3 commands. Each subsystem probed in separate connection.

## 2. Top-Level System Children (Live-Enumerated)

Total: 60 children (59 op, 1 nop)

| Name | Type |
|---|---|
| Local | Local |
| Reporting | Reporting |
| LED | LED |
| Executor | Executor |
| Cycle | Cycle |
| PLC | PLC |
| SystemState | SystemState |
| ParserRW | ParseTCPServer |
| ParserRO | ParseTCPServer |
| ParserEdge | ParseTCPServer |
| Metric0ms | ParticleRepEvent |
| Metric250ms | ParticleRepEvent |
| Metric500ms | ParticleRepEvent |
| Metric1s | ParticleRepEvent |
| Metric5s | ParticleRepEvent |
| Metric1m | ParticleRepEvent |
| Metric1h | ParticleRepEvent |
| Metric1d | ParticleRepEvent |
| CANBusSystem | CANMaster |
| CANBusDrive | CANMaster |
| Cabin | UICabin |
| CabinSecPwr | oSysStateAuto |
| BMSAB | BMSAB |
| ChargerABC | ChargerABC |
| FuncModeCntrl | FuncModeCntrl |
| UIEvent | UIEvent |
| ProgMovCntrl | mProgCntrl |
| Travel | mTravelQuad |
| Lift | mLiftQuad |
| iLiftAPos | iwScaled |
| iLiftBPos | iwScaled |
| iLiftCPos | iwScaled |
| iLiftDPos | iwScaled |
| iLiftABSync | iSynch |
| iLiftCDSync | iSynch |
| iLiftSync | iSynch |
| Spreader | Spreader |
| iTwistALowered | iwPosOnly |
| iTwistBLowered | iwPosOnly |
| iTwistCLowered | iwPosOnly |
| iTwistDLowered | iwPosOnly |
| iwTwistRdy | iwTwistRdy |
| iTwistLowerTrav | iwLockout |
| OperatingMode | OperatingMode |
| Active | ActiveSystem |
| UMFS | UMFS |
| EstopLoad | oSysStateAuto |
| TMS | TMS |
| Secondary | Secondary |
| Alarm | oSystemState |
| Beacons | oSystemState |
| Horn | oSystemState |
| Lights | oSystemState |
| SensorSupply | oSysStateAuto |
| Steer | mSteerElec |
| iSteerAPos | iwScaled |
| iSteerBPos | iwScaled |
| iSteerCPos | iwScaled |
| iSteerDPos | iwScaled |
| ClearFailSafe | ValRefBool (NOP) |

## 3. Subsystem Child Naming Patterns (Live-Enumerated)

### System/BMSAB
- 32 nop-children: AvailFactor, Availability, Current, CurrentMismatch, EnblBMS, EnblRestart, EnblSOCRecovery, RestartCount, SOC, SOCLowOpMin, SOCLowStdbyMin, SOCMismatch, SOCRecCurrMin, SOCRecTimRst, SOCWarnLow, TMSMismatch, Voltage, VoltageMismatch, etc.

### System/Steer
- op: CntxtQualModEx, iMovement
- iMovement children: ChannelMask, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement

### System/TMS
- op: Chilling, ClntReservoir, ClntTemp, CurrState, Heating, Pump
- nop: BMSTMSCooling, BMSTMSHeating, ClntChilling, ClntHeating, ClntReservoir, ClntSecFailHC, ClntSecFailPmp, ClntTemp, ClntTempCold, ClntTempColdCutb, ClntTempHot, ClntTempHotCutb, CurrState, Heating, OvrdControl, Pump, ReqState, TMSCooling, TMSHeating

### System/Travel
- op: CntxtQualModEx, iMovement
- iMovement children: ChannelMask, ClntTempColdCutb, CntxtQualModEx, Life, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement

### System/Lift
- op: CntxtQualModEx, iMovement
- iMovement children: ChannelMask, ClntTempColdCutb, CntxtQualModEx, Life, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement

### System/Secondary
- nop: CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait

### System/ProgMovCntrl
- nop: ProgMovNull, steer_0

### System/ChargerABC
- nop: ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt

### System/Spreader
- op: AB, CD, TwstALow, TwstBLow, TwstCLow, TwstDLow

### System/SystemState
- nop: AutoStart, CntxtSysCntrl, CntxtSysStateDn, CntxtSysStateUp, Event, State

### CANBusDrive
- 22 devices: BusPower, cSpreader, cSteerA-D, cSteerAngleA-D, cTransA-D, cWinchA-D, cWinchAngleA-D

### CANBusDrive/cTransA (and cSteerA, cWinchA - identical structure)
- 9 signals: Alarm, BattCurrent, BattPower, BattVoltage, CntrlTemp, Current, MotorTemp, TPO1Stuffing, Velocity

### CANBusDrive/cSpreader
- 42 signals: Brake, BrakeDisengage, BrakeThrottle, HydPressure, HydTemp, HydraulicFilter, PmpCntrlTemp, PmpMotTemp, PumpAlarm, PumpAllow, PumpBattCrrnt, PumpBattVolt, PumpCurrent, PumpOn, PumpPressure, PumpRunning, PumpState, PumpVelocity, SideshiftAB, SideshiftCD, TelscpActive, TelscpAuto, TelscpAutoExt, TelscpAutoRet, TelscpEnbl, TelscpExtend, TelscpRetract, TwstALow, TwstAStt, TwstActive, TwstBLow, TwstBStt, TwstCLow, TwstCStt, TwstDLow, TwstDStt, TwstEnbl, TwstLock, TwstStt, TwstUnlock

## 4. Reconciliation Summary

| Category | Count |
|---|---|
| Total unique trace signals | 588 |
| Exact match | 27 |
| Remapped via abbreviation/device rename | 461 |
| No runtime match | 96 |
| Nonexistent (confirmed) | 4 |

## 5. Key Remap Findings

### 5.1 Particle Name Remaps

| Trace Config Name | Runtime Name | Evidence |
|---|---|---|
| System/BMS | System/BMSAB | Live-enumerated |
| System/Steering | System/Steer | Live-enumerated |
| System/Charger | System/ChargerABC | Live-enumerated |
| System/SecondaryPowerSupply | System/Secondary | Live-enumerated |
| System/ProgrammedMovementControl | System/ProgMovCntrl | Live-enumerated |

### 5.2 TMS Abbreviations

| Trace Config Name | Runtime Name | Evidence |
|---|---|---|
| TMS/RequestedState | TMS/ReqState | Live-enumerated |
| TMS/CurrentState | TMS/CurrState | Live-enumerated |
| TMS/CoolantReservoir | TMS/ClntReservoir | Live-enumerated |
| TMS/CurrentCoolantTemperature | TMS/ClntTemp | Live-enumerated |
| TMS/CoolantChilling | TMS/ClntChilling | Live-enumerated |
| TMS/CoolantHeating | TMS/ClntHeating | Live-enumerated |
| TMS/CoolantPump | TMS/Pump | Live-enumerated |

### 5.3 Drive Device Name Remaps (no 'c' prefix in trace config)

| Trace Config Device | Runtime Device |
|---|---|
| TransA/B/C/D | cTransA/B/C/D |
| SteerA/B/C/D | cSteerA/B/C/D |
| WinchA/B/C/D | cWinchA/B/C/D |
| Spreader | cSpreader |
| SteerAngleA/B/C/D | cSteerAngleA/B/C/D |
| WinchAngleA/B/C/D | cWinchAngleA/B/C/D |

### 5.4 Drive Signal Abbreviations

| Trace Config Name | Runtime Name |
|---|---|
| MotorTemperature | MotorTemp |
| ControllerTemperature | CntrlTemp |
| BatteryVoltage | BattVoltage |
| BatteryCurrent | BattCurrent |
| BatteryPower | BattPower |

### 5.5 Spreader Signal Abbreviations

| Trace Config Name | Runtime Name |
|---|---|
| TelescopingActive | TelscpActive |
| TelescopingEnabled | TelscpEnbl |
| TelescopingAutoCommand | TelscpAuto |
| TelescopingExtendCommand | TelscpExtend |
| TelescopingRetractCommand | TelscpRetract |
| TwistlocksEnabled | TwstEnbl |
| TwistlocksActive | TwstActive |
| TwistlocksLockCommand | TwstLock |
| TwistlocksUnlockCommand | TwstUnlock |
| HydraulicPressure | HydPressure |
| HydraulicTemperature | HydTemp |
| BrakeDisengaged | BrakeDisengage |
| TwistlockACurrentState | TwstAStt |
| TwistlockALoweredState | TwstALow |
| PumpMotorTemperature | PmpMotTemp |
| PumpControllerTemperature | PmpCntrlTemp |

### 5.6 Movement/Steering Wheel Remaps

| Trace Config Path | Runtime Path |
|---|---|
| Travel/MovementA-D | Travel/iMovement |
| Lift/MovementA-D | Lift/iMovement |
| Steering/WheelA-D | Steer/iMovement |
| Travel/ThrottleValue | Travel/Throttle |

## 6. Confirmed Non-Existent Signals

| # | Trace Config Path | Runtime Path |
|---|---|---|
| 1 | `gSystem.lLift.lDiagnostic` | `System/Lift/Diagnostic` |
| 2 | `gSystem.lTravel.lDiagnostic` | `System/Travel/Diagnostic` |
| 3 | `gSystem.lTravel.lMovementD.LDiagnostic` | `System/Travel/MovementD/LDiagnostic` |
| 4 | `gSystem.lTravel.lMovementD.lDiagnostic` | `System/Travel/MovementD/Diagnostic` |

**Note:** ProposedThrottle does NOT exist on any drive (confirmed across TransA, SteerA, WinchA). Diagnostic does NOT exist on drives. Travel/MovementD does NOT exist (replaced by iMovement).

## 7. No Runtime Match (Requires Further Investigation)

Total: 96 signals

### 7.1 Lift Subsystem (22 signals)
Trace config references: Input, InputProcessed, ScalingA-D, Diagnostic, MovementA-D/Diagnostic, Interlock*, ChargeInterlock*, ThrottleValue
Runtime shows: CntxtQualModEx, iMovement (with ChannelMask, Override, Suppress, etc.)
**Gap:** Lift has many more children than currently enumerated; Input, ScalingA-D, Interlock, ChargeInterlock particles not found.

### 7.2 Lift*Interlock Particles (24 signals)
Trace config references: LiftAPositionInterlock, LiftBPositionInterlock, LiftCPositionInterlock, LiftDPositionInterlock, LiftABSynchronousInterlock, LiftCDSynchronousInterlock, LiftSynchronousInterlock
Runtime: These particles not found as top-level System children.

### 7.3 Travel Subsystem (10 signals)
Trace config references: Diagnostic, MovementA-D/Diagnostic, ScalingA-D, Input, InputProcessed, etc.
Runtime shows: CntxtQualModEx, iMovement

### 7.4 Steering Subsystem (40+ signals)
Trace config references: Input, TargetAngle, AdjustState, WheelA-D/*, SteerModeDiagnostic, ModeChange, etc.
Runtime shows: CntxtQualModEx, iMovement

### 7.5 BMSAB Deep Signals (10 signals)
Trace config references: RestartCount, SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B, etc.
Runtime BMSAB has 32 nop-children but these specific paths not matched.

### 7.6 ChargerABC Mismatch (7 signals)
Trace config references: ChargerDiagnostic, ChargingCurrentTarget, ChargingVoltageTarget, CurrentBMSChargeState, RequestedBMSChargeState, RequestedOBCState, CurrentOBCState
Runtime ChargerABC has: ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt

### 7.7 Secondary Mismatch (12 signals)
Trace config references: CurrentState, RequestedState, Availability, ControllerSecondaryPowerSupplyA/B/*
Runtime Secondary has: CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait

### 7.8 ProgMovCntrl Mismatch (10 signals)
Trace config references: Movement/Code, Movement/ProgMovDiagnostic, Requested, Movement/Enabled, Movement/Diagnostic, Movement/Active, Movement/TimeStep, Movement/State, Movement/Input, Movement/Moving, Movement/Success, Movement/ThrottleValue
Runtime ProgMovCntrl has only: ProgMovNull, steer_0

### 7.9 SystemState Deep Signals (4 signals)
Trace config references: AllowDownTrace, AllowUpTrace, NextStateTrace, SystemControlTrace, ForceMaxTrace
Runtime SystemState has: AutoStart, CntxtSysCntrl, CntxtSysStateDn, CntxtSysStateUp, Event, State

### 7.10 CANBusDrive/cSpreader Missing Signals (3 signals)
Trace config references: TelescopingEnabled (duplicate), TwistlocksEnabled (duplicate)
Runtime cSpreader has TelscpEnbl, TwstEnbl but some trace config variants not matched.

## 8. Exact Matches (Sample)

Total: 27 signals

| # | Trace Config | Runtime Path |
|---|---|---|
| 1 | `gSystem.lCANOpenMasterSystem.lBMSA.lCurrentBMSState.lValue` | `System/CANBusSystem/BMSA/CurrentBMSState` |
| 2 | `gSystem.lCANOpenMasterSystem.lBMSA.lNodeState` | `System/CANBusSystem/BMSA/NodeState` |
| 3 | `gSystem.lCANOpenMasterSystem.lBMSA.lPackAverageTemperature.lValue` | `System/CANBusSystem/BMSA/PackAverageTemperature` |
| 4 | `gSystem.lCANOpenMasterSystem.lBMSA.lPackFaultCode.lValue` | `System/CANBusSystem/BMSA/PackFaultCode` |
| 5 | `gSystem.lCANOpenMasterSystem.lBMSA.lPackFaultNumber.lValue` | `System/CANBusSystem/BMSA/PackFaultNumber` |
| 6 | `gSystem.lCANOpenMasterSystem.lBMSA.lPackMaxTemperature.lValue` | `System/CANBusSystem/BMSA/PackMaxTemperature` |
| 7 | `gSystem.lCANOpenMasterSystem.lBMSA.lPackMinTemperature.lValue` | `System/CANBusSystem/BMSA/PackMinTemperature` |
| 8 | `gSystem.lCANOpenMasterSystem.lBMSA.lRequestedBMSState.lValue` | `System/CANBusSystem/BMSA/RequestedBMSState` |
| 9 | `gSystem.lCANOpenMasterSystem.lBMSB.lCurrentBMSState.lValue` | `System/CANBusSystem/BMSB/CurrentBMSState` |
| 10 | `gSystem.lCANOpenMasterSystem.lBMSB.lNodeState` | `System/CANBusSystem/BMSB/NodeState` |
| 11 | `gSystem.lCANOpenMasterSystem.lBMSB.lPackAverageTemperature.lValue` | `System/CANBusSystem/BMSB/PackAverageTemperature` |
| 12 | `gSystem.lCANOpenMasterSystem.lBMSB.lPackFaultCode.lValue` | `System/CANBusSystem/BMSB/PackFaultCode` |
| 13 | `gSystem.lCANOpenMasterSystem.lBMSB.lPackFaultNumber.lValue` | `System/CANBusSystem/BMSB/PackFaultNumber` |
| 14 | `gSystem.lCANOpenMasterSystem.lBMSB.lPackMaxTemperature.lValue` | `System/CANBusSystem/BMSB/PackMaxTemperature` |
| 15 | `gSystem.lCANOpenMasterSystem.lBMSB.lPackMinTemperature.lValue` | `System/CANBusSystem/BMSB/PackMinTemperature` |
| 16 | `gSystem.lCANOpenMasterSystem.lBMSB.lRequestedBMSState.lValue` | `System/CANBusSystem/BMSB/RequestedBMSState` |
| 17 | `gSystem.lCANOpenMasterSystem.lChargerA.lNodeState` | `System/CANBusSystem/ChargerA/NodeState` |
| 18 | `gSystem.lCANOpenMasterSystem.lChargerA.lOBCStatus.lValue` | `System/CANBusSystem/ChargerA/OBCStatus` |
| 19 | `gSystem.lCANOpenMasterSystem.lChargerA.lOBCStatusDerived` | `System/CANBusSystem/ChargerA/OBCStatusDerived` |
| 20 | `gSystem.lCANOpenMasterSystem.lChargerA.lRequestedOBCState.lValue` | `System/CANBusSystem/ChargerA/RequestedOBCState` |
| 21 | `gSystem.lCANOpenMasterSystem.lChargerA.lStatusCC.lValue` | `System/CANBusSystem/ChargerA/StatusCC` |
| 22 | `gSystem.lCANOpenMasterSystem.lChargerA.lStatusCP.lValue` | `System/CANBusSystem/ChargerA/StatusCP` |
| 23 | `gSystem.lCANOpenMasterSystem.lChargerA.lStopCharging.lValue` | `System/CANBusSystem/ChargerA/StopCharging` |
| 24 | `gSystem.lCANOpenMasterSystem.lSecondaryPowerSupplyA.lNodeState` | `System/CANBusSystem/SecondaryPowerSupplyA/NodeState` |
| 25 | `gSystem.lCANOpenMasterSystem.lSecondaryPowerSupplyB.lNodeState` | `System/CANBusSystem/SecondaryPowerSupplyB/NodeState` |
| 26 | `gSystem.lCANOpenMasterSystem.lUInterfaceCabin.lNodeState` | `System/CANBusSystem/UInterfaceCabin/NodeState` |
| 27 | `gSystem.lSystemState.lState.lValue` | `System/SystemState/State` |

## 9. Remaining Blind Spots

1. **Lift deep hierarchy** - Input, ScalingA-D, MovementA-D, Interlock, ChargeInterlock particles not found in runtime. May require deeper traversal or different path.
2. **Lift*Interlock particles** - 7 interlock particles referenced in trace config not found as System children. May be nested or named differently.
3. **Travel deep hierarchy** - Diagnostic, ScalingA-D, MovementA-D/Diagnostic not found. Only CntxtQualModEx and iMovement confirmed.
4. **Steering deep hierarchy** - 40+ signals referencing Steering.Input, Steering.TargetAngle, Steering.WheelA-D/* not matched. Only Steer.CntxtQualModEx and Steer.iMovement confirmed.
5. **BMSAB deep signals** - RestartCount, SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B paths not matched to BMSAB children.
6. **ChargerABC signal mapping** - Trace config names (ChargerDiagnostic, ChargingCurrentTarget, etc.) do not match runtime children (ChrgConn, ChrgOBCErr, etc.).
7. **Secondary signal mapping** - Trace config names (CurrentState, RequestedState, Availability, Controller*) do not match runtime children (SecPwrNotRun, SecPwrWait, etc.).
8. **ProgMovCntrl signal mapping** - Trace config expects Movement/* hierarchy; runtime only has ProgMovNull and steer_0.
9. **SystemState deep signals** - AllowDownTrace, AllowUpTrace, NextStateTrace, SystemControlTrace, ForceMaxTrace not found.
10. **CANBusDrive signals beyond 9** - Only 9 signals confirmed per drive; prior phases reported 34-child structure. Current PLC state may differ or connection truncation.
11. **Metric registration & emission** - Not verified in this pass.
12. **CANBusSystem full hierarchy** - Only BMSA, BMSB, ChargerA children partially confirmed.

---

*End of Phase 4 Runtime-First Validation & Remapping Report.*

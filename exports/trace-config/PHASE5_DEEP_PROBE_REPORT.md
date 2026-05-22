# Phase 5: Deep Probing Pass - 96 No-Match Resolution Report

**Date:** 2026-05-21
**PLC Target:** 10.2.3.4 (apollo ESX-3CS)
**Scope:** Resolve 96 no runtime match signals from Phase 4 remapping

---

## Executive Summary

| Metric | Count |
|---|---|
| Total no-match signals from Phase 4 | 96 |
| **Newly resolved this pass** (exist at runtime) | **23** |
| Abbreviation mismatches (runtime exists, different name) | 4 |
| **Confirmed nonexistent** | **69** |
| Remaining unresolved | 0 |

---

## 1. Newly Resolved Signals (23)

### 1.1 Lift Subsystem (2)
| Trace Config | Runtime Path | Note |
|---|---|---|
| gSystem.lLift.lInput.lValue | System/Lift/Input | Direct match |
| gSystem.lLift.lThrottleValue | System/Lift/Throttle | Runtime uses Throttle |

### 1.2 Travel Subsystem (2)
| Trace Config | Runtime Path | Note |
|---|---|---|
| gSystem.lTravel.lInput.lValue | System/Travel/Input | Direct match |
| gSystem.lTravel.lThrottleValue | System/Travel/Throttle | Runtime uses Throttle |

### 1.3 Steering Subsystem (2)
| Trace Config | Runtime Path | Note |
|---|---|---|
| gSystem.lSteering.lInput.lValue | System/Steer/Input | Direct match |
| gSystem.lSteering.lTargetAngle.lValue | System/Steer/TargetAngle | Direct match |

### 1.4 SystemState Subsystem (6)
| Trace Config | Runtime Path | Type |
|---|---|---|
| gSystem.lSystemState.lAutoStart | System/SystemState/AutoStart | Causal |
| gSystem.lSystemState.lEvent | System/SystemState/Event | Event |
| gSystem.lSystemState.lState.lValue | System/SystemState/State | ValObjEnum |
| gSystem.lSystemState.lCntxtSysCntrl | System/SystemState/CntxtSysCntrl | CntxtSysCntrl |
| gSystem.lSystemState.lCntxtSysStateDn | System/SystemState/CntxtSysStateDn | CntxtSysStateDn |
| gSystem.lSystemState.lCntxtSysStateUp | System/SystemState/CntxtSysStateUp | CntxtSysStateUp |

### 1.5 TMS Subsystem (12)
| Trace Config | Runtime Path | Note |
|---|---|---|
| gSystem.lTMS.lCoolantChilling.lValue | System/TMS/ClntChilling | Abbreviation |
| gSystem.lTMS.lCoolantHeating.lValue | System/TMS/ClntHeating | Abbreviation |
| gSystem.lTMS.lCurrentState.lValue | System/TMS/CurrState | Abbreviation |
| gSystem.lTMS.lRequestedState.lValue | System/TMS/ReqState | Abbreviation |
| gSystem.lTMS.lCoolantReservoir.lValue | System/TMS/ClntReservoir | Abbreviation |
| gSystem.lTMS.lCurrentCoolantTemperature.lValue | System/TMS/ClntTemp | Abbreviation |
| gSystem.lTMS.lCoolantPump.lValue | System/TMS/Pump | Abbreviation |
| gSystem.lTMS.lChilling | System/TMS/Chilling | Direct match |
| gSystem.lTMS.lHeating | System/TMS/Heating | Direct match |
| gSystem.lTMS.lPump | System/TMS/Pump | Direct match |

### 1.6 BMSAB Subsystem (1)
| Trace Config | Runtime Path | Type |
|---|---|---|
| gSystem.lBMS.lRestartCount | System/BMSAB/RestartCount | ValRefUSINT |

---

## 2. Confirmed Nonexistent (69)

### 2.1 Lift Deep (12): InputProcessed, ThrottleValue, ScalingA-D, MovementA-D, ChargeInterlock, Interlock
### 2.2 Lift*Interlock Top-Level (21): All 7 interlock particles nonexistent
### 2.3 Travel Deep (21): InputProcessed, InputNulled, InputPresent*, InputResolved, InputScaling, InputSecondary, EnableInputSecondary, Active, ThrottleValue, SlowFactor*, ScalingA-D, MovementA-D, SteerAdjustTimer
### 2.4 Steering Deep (17): InputProcessed, InputPresentAny, AdjustState, SteerModeDiagnostic, Mode, ModeChange, RequestedAbsoluteTargetAngle, TargetAngleIncrement*, CurrentAbsDelta, ZeroTargetAngleSwitch, WheelA-D
### 2.5 SystemState Deep (6): AllowDownTrace, AllowUpTrace, NextStateTrace, SystemControlTrace, ForceMaxTrace, ChargingEnabled
### 2.6 TMS (1): RequestedCoolantTemperature
### 2.7 BMSAB Deep (6): SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B
### 2.8 ChargerABC (7): All trace config signals nonexistent
### 2.9 Secondary (6): All trace config signals nonexistent
### 2.10 ProgMovCntrl (2): Movement, Requested
### 2.11 CANBusDrive (6): HeartbeatCounter x3, FreeWheel x2, Enable

---

## 3. Key Corrections to Prior Mapping

1. **CANBusDrive signal count:** 34 per drive (9 op + 25 nop), NOT 9 as Phase 4 reported
2. **HeartbeatCounter:** Does NOT exist (Phase 4 false positive)
3. **FreeWheel:** Does NOT exist (Phase 4 false positive)
4. **Enable:** Does NOT exist; runtime has EnableMotor and Enabled
5. **TMS abbrev remapping bug:** known_remaps failed due to System/ prefix mismatch
6. **BMSAB deep signals:** SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B do NOT exist
7. **ChargerABC/Secondary/ProgMovCntrl:** Complete mismatch - all trace config signals nonexistent
8. **Steering WheelA-D:** No wheel-level hierarchy exists at runtime

---

## 4. Runtime Hierarchy Summary

| Subsystem | Runtime Children |
|---|---|
| Lift | CntxtQualModEx, Input, Throttle, iMovement |
| Travel | CntxtQualModEx, Input, Throttle, iMovement |
| Steer | CntxtQualModEx, Input, TargetAngle, iMovement |
| SystemState | AutoStart, CntxtSysCntrl, CntxtSysStateDn, CntxtSysStateUp, Event, State |
| TMS | Chilling, ClntChilling, ClntHeating, ClntReservoir, ClntTemp, ClntTempCold, ClntTempHot, CurrState, Heating, Pump, ReqState |
| BMSAB | 32 nop-children (RestartCount confirmed) |
| ChargerABC | ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt |
| Secondary | CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait |
| ProgMovCntrl | ProgMovNull, steer_0 |
| CANBusDrive | 22 devices, 34 signals per drive, 54 on cSpreader |

---

*End of Phase 5 Report.*
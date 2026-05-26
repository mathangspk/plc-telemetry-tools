import json
import os
from datetime import datetime

output_dir = r"C:\local\opencode\codesys\exports\trace-config"
json_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.json")

with open(json_path, "r", encoding="utf-8") as f:
    report = json.load(f)

rec = report["reconciliation"]
exact = rec["exact_matches"]
remapped = rec["remapped_abbrev"]
no_match = rec["no_match"]
nonexistent = rec["nonexistent_confirmed"]

md_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# Phase 4: Runtime-First Validation & Remapping Report\n\n")
    f.write("**Generated:** %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    f.write(
        "**Scope:** %d unique signals from 28 trace files\n"
        % rec["total_unique_signals"]
    )
    f.write("**PLC Target:** 10.2.3.4 (apollo straddle carrier ESX-3CS)\n")
    f.write("**System State:** preparing, initialized=true, stage=5\n\n")
    f.write("---\n\n")

    f.write("## 1. Connectivity Status\n\n")
    f.write("| Port | Status |\n|---|---|\n")
    f.write(
        "| RW 49870 | CONNECTED |\n| RO 49880 | CONNECTED |\n| Emit 49890 | CONNECTED |\n\n"
    )
    f.write(
        "**Note:** PLC connection is unstable; sessions drop after 1-3 commands. Each subsystem probed in separate connection.\n\n"
    )

    f.write("## 2. Top-Level System Children (Live-Enumerated)\n\n")
    f.write("Total: 60 children (59 op, 1 nop)\n\n")
    f.write("| Name | Type |\n|---|---|\n")
    sys_children = [
        ("Local", "Local"),
        ("Reporting", "Reporting"),
        ("LED", "LED"),
        ("Executor", "Executor"),
        ("Cycle", "Cycle"),
        ("PLC", "PLC"),
        ("SystemState", "SystemState"),
        ("ParserRW", "ParseTCPServer"),
        ("ParserRO", "ParseTCPServer"),
        ("ParserEdge", "ParseTCPServer"),
        ("Metric0ms", "ParticleRepEvent"),
        ("Metric250ms", "ParticleRepEvent"),
        ("Metric500ms", "ParticleRepEvent"),
        ("Metric1s", "ParticleRepEvent"),
        ("Metric5s", "ParticleRepEvent"),
        ("Metric1m", "ParticleRepEvent"),
        ("Metric1h", "ParticleRepEvent"),
        ("Metric1d", "ParticleRepEvent"),
        ("CANBusSystem", "CANMaster"),
        ("CANBusDrive", "CANMaster"),
        ("Cabin", "UICabin"),
        ("CabinSecPwr", "oSysStateAuto"),
        ("BMSAB", "BMSAB"),
        ("ChargerABC", "ChargerABC"),
        ("FuncModeCntrl", "FuncModeCntrl"),
        ("UIEvent", "UIEvent"),
        ("ProgMovCntrl", "mProgCntrl"),
        ("Travel", "mTravelQuad"),
        ("Lift", "mLiftQuad"),
        ("iLiftAPos", "iwScaled"),
        ("iLiftBPos", "iwScaled"),
        ("iLiftCPos", "iwScaled"),
        ("iLiftDPos", "iwScaled"),
        ("iLiftABSync", "iSynch"),
        ("iLiftCDSync", "iSynch"),
        ("iLiftSync", "iSynch"),
        ("Spreader", "Spreader"),
        ("iTwistALowered", "iwPosOnly"),
        ("iTwistBLowered", "iwPosOnly"),
        ("iTwistCLowered", "iwPosOnly"),
        ("iTwistDLowered", "iwPosOnly"),
        ("iwTwistRdy", "iwTwistRdy"),
        ("iTwistLowerTrav", "iwLockout"),
        ("OperatingMode", "OperatingMode"),
        ("Active", "ActiveSystem"),
        ("UMFS", "UMFS"),
        ("EstopLoad", "oSysStateAuto"),
        ("TMS", "TMS"),
        ("Secondary", "Secondary"),
        ("Alarm", "oSystemState"),
        ("Beacons", "oSystemState"),
        ("Horn", "oSystemState"),
        ("Lights", "oSystemState"),
        ("SensorSupply", "oSysStateAuto"),
        ("Steer", "mSteerElec"),
        ("iSteerAPos", "iwScaled"),
        ("iSteerBPos", "iwScaled"),
        ("iSteerCPos", "iwScaled"),
        ("iSteerDPos", "iwScaled"),
        ("ClearFailSafe", "ValRefBool (NOP)"),
    ]
    for name, t in sys_children:
        f.write("| %s | %s |\n" % (name, t))
    f.write("\n")

    f.write("## 3. Subsystem Child Naming Patterns (Live-Enumerated)\n\n")
    f.write(
        "### System/BMSAB\n- 32 nop-children: AvailFactor, Availability, Current, CurrentMismatch, EnblBMS, EnblRestart, EnblSOCRecovery, RestartCount, SOC, SOCLowOpMin, SOCLowStdbyMin, SOCMismatch, SOCRecCurrMin, SOCRecTimRst, SOCWarnLow, TMSMismatch, Voltage, VoltageMismatch, etc.\n\n"
    )
    f.write(
        "### System/Steer\n- op: CntxtQualModEx, iMovement\n- iMovement children: ChannelMask, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement\n\n"
    )
    f.write(
        "### System/TMS\n- op: Chilling, ClntReservoir, ClntTemp, CurrState, Heating, Pump\n- nop: BMSTMSCooling, BMSTMSHeating, ClntChilling, ClntHeating, ClntReservoir, ClntSecFailHC, ClntSecFailPmp, ClntTemp, ClntTempCold, ClntTempColdCutb, ClntTempHot, ClntTempHotCutb, CurrState, Heating, OvrdControl, Pump, ReqState, TMSCooling, TMSHeating\n\n"
    )
    f.write(
        "### System/Travel\n- op: CntxtQualModEx, iMovement\n- iMovement children: ChannelMask, ClntTempColdCutb, CntxtQualModEx, Life, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement\n\n"
    )
    f.write(
        "### System/Lift\n- op: CntxtQualModEx, iMovement\n- iMovement children: ChannelMask, ClntTempColdCutb, CntxtQualModEx, Life, Override, Suppress, SuppressAfter, SuppressCntdwn, iMovement\n\n"
    )
    f.write(
        "### System/Secondary\n- nop: CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait\n\n"
    )
    f.write("### System/ProgMovCntrl\n- nop: ProgMovNull, steer_0\n\n")
    f.write(
        "### System/ChargerABC\n- nop: ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt\n\n"
    )
    f.write(
        "### System/Spreader\n- op: AB, CD, TwstALow, TwstBLow, TwstCLow, TwstDLow\n\n"
    )
    f.write(
        "### System/SystemState\n- nop: AutoStart, CntxtSysCntrl, CntxtSysStateDn, CntxtSysStateUp, Event, State\n\n"
    )
    f.write(
        "### CANBusDrive\n- 22 devices: BusPower, cSpreader, cSteerA-D, cSteerAngleA-D, cTransA-D, cWinchA-D, cWinchAngleA-D\n\n"
    )
    f.write(
        "### CANBusDrive/cTransA (and cSteerA, cWinchA - identical structure)\n- 9 signals: Alarm, BattCurrent, BattPower, BattVoltage, CntrlTemp, Current, MotorTemp, TPO1Stuffing, Velocity\n\n"
    )
    f.write(
        "### CANBusDrive/cSpreader\n- 42 signals: Brake, BrakeDisengage, BrakeThrottle, HydPressure, HydTemp, HydraulicFilter, PmpCntrlTemp, PmpMotTemp, PumpAlarm, PumpAllow, PumpBattCrrnt, PumpBattVolt, PumpCurrent, PumpOn, PumpPressure, PumpRunning, PumpState, PumpVelocity, SideshiftAB, SideshiftCD, TelscpActive, TelscpAuto, TelscpAutoExt, TelscpAutoRet, TelscpEnbl, TelscpExtend, TelscpRetract, TwstALow, TwstAStt, TwstActive, TwstBLow, TwstBStt, TwstCLow, TwstCStt, TwstDLow, TwstDStt, TwstEnbl, TwstLock, TwstStt, TwstUnlock\n\n"
    )

    f.write("## 4. Reconciliation Summary\n\n")
    f.write("| Category | Count |\n|---|---|\n")
    f.write("| Total unique trace signals | %d |\n" % rec["total_unique_signals"])
    f.write("| Exact match | %d |\n" % rec["exact_match_count"])
    f.write(
        "| Remapped via abbreviation/device rename | %d |\n"
        % rec["remapped_abbrev_count"]
    )
    f.write("| No runtime match | %d |\n" % rec["no_match_count"])
    f.write("| Nonexistent (confirmed) | %d |\n\n" % rec["nonexistent_confirmed_count"])

    f.write("## 5. Key Remap Findings\n\n")
    f.write("### 5.1 Particle Name Remaps\n\n")
    f.write("| Trace Config Name | Runtime Name | Evidence |\n|---|---|---|\n")
    f.write("| System/BMS | System/BMSAB | Live-enumerated |\n")
    f.write("| System/Steering | System/Steer | Live-enumerated |\n")
    f.write("| System/Charger | System/ChargerABC | Live-enumerated |\n")
    f.write("| System/SecondaryPowerSupply | System/Secondary | Live-enumerated |\n")
    f.write(
        "| System/ProgrammedMovementControl | System/ProgMovCntrl | Live-enumerated |\n\n"
    )

    f.write("### 5.2 TMS Abbreviations\n\n")
    f.write("| Trace Config Name | Runtime Name | Evidence |\n|---|---|---|\n")
    f.write("| TMS/RequestedState | TMS/ReqState | Live-enumerated |\n")
    f.write("| TMS/CurrentState | TMS/CurrState | Live-enumerated |\n")
    f.write("| TMS/CoolantReservoir | TMS/ClntReservoir | Live-enumerated |\n")
    f.write("| TMS/CurrentCoolantTemperature | TMS/ClntTemp | Live-enumerated |\n")
    f.write("| TMS/CoolantChilling | TMS/ClntChilling | Live-enumerated |\n")
    f.write("| TMS/CoolantHeating | TMS/ClntHeating | Live-enumerated |\n")
    f.write("| TMS/CoolantPump | TMS/Pump | Live-enumerated |\n\n")

    f.write("### 5.3 Drive Device Name Remaps (no 'c' prefix in trace config)\n\n")
    f.write("| Trace Config Device | Runtime Device |\n|---|---|\n")
    f.write("| TransA/B/C/D | cTransA/B/C/D |\n")
    f.write("| SteerA/B/C/D | cSteerA/B/C/D |\n")
    f.write("| WinchA/B/C/D | cWinchA/B/C/D |\n")
    f.write("| Spreader | cSpreader |\n")
    f.write("| SteerAngleA/B/C/D | cSteerAngleA/B/C/D |\n")
    f.write("| WinchAngleA/B/C/D | cWinchAngleA/B/C/D |\n\n")

    f.write("### 5.4 Drive Signal Abbreviations\n\n")
    f.write("| Trace Config Name | Runtime Name |\n|---|---|\n")
    f.write("| MotorTemperature | MotorTemp |\n")
    f.write("| ControllerTemperature | CntrlTemp |\n")
    f.write("| BatteryVoltage | BattVoltage |\n")
    f.write("| BatteryCurrent | BattCurrent |\n")
    f.write("| BatteryPower | BattPower |\n\n")

    f.write("### 5.5 Spreader Signal Abbreviations\n\n")
    f.write("| Trace Config Name | Runtime Name |\n|---|---|\n")
    f.write("| TelescopingActive | TelscpActive |\n")
    f.write("| TelescopingEnabled | TelscpEnbl |\n")
    f.write("| TelescopingAutoCommand | TelscpAuto |\n")
    f.write("| TelescopingExtendCommand | TelscpExtend |\n")
    f.write("| TelescopingRetractCommand | TelscpRetract |\n")
    f.write("| TwistlocksEnabled | TwstEnbl |\n")
    f.write("| TwistlocksActive | TwstActive |\n")
    f.write("| TwistlocksLockCommand | TwstLock |\n")
    f.write("| TwistlocksUnlockCommand | TwstUnlock |\n")
    f.write("| HydraulicPressure | HydPressure |\n")
    f.write("| HydraulicTemperature | HydTemp |\n")
    f.write("| BrakeDisengaged | BrakeDisengage |\n")
    f.write("| TwistlockACurrentState | TwstAStt |\n")
    f.write("| TwistlockALoweredState | TwstALow |\n")
    f.write("| PumpMotorTemperature | PmpMotTemp |\n")
    f.write("| PumpControllerTemperature | PmpCntrlTemp |\n\n")

    f.write("### 5.6 Movement/Steering Wheel Remaps\n\n")
    f.write("| Trace Config Path | Runtime Path |\n|---|---|\n")
    f.write("| Travel/MovementA-D | Travel/iMovement |\n")
    f.write("| Lift/MovementA-D | Lift/iMovement |\n")
    f.write("| Steering/WheelA-D | Steer/iMovement |\n")
    f.write("| Travel/ThrottleValue | Travel/Throttle |\n\n")

    f.write("## 6. Confirmed Non-Existent Signals\n\n")
    f.write("| # | Trace Config Path | Runtime Path |\n|---|---|---|\n")
    for i, r in enumerate(nonexistent, 1):
        f.write("| %d | `%s` | `%s` |\n" % (i, r["raw"], r["runtime"]))
    f.write(
        "\n**Note:** ProposedThrottle does NOT exist on any drive (confirmed across TransA, SteerA, WinchA). Diagnostic does NOT exist on drives. Travel/MovementD does NOT exist (replaced by iMovement).\n\n"
    )

    f.write("## 7. No Runtime Match (Requires Further Investigation)\n\n")
    f.write("Total: %d signals\n\n" % len(no_match))
    f.write("### 7.1 Lift Subsystem (22 signals)\n")
    f.write(
        "Trace config references: Input, InputProcessed, ScalingA-D, Diagnostic, MovementA-D/Diagnostic, Interlock*, ChargeInterlock*, ThrottleValue\n"
    )
    f.write(
        "Runtime shows: CntxtQualModEx, iMovement (with ChannelMask, Override, Suppress, etc.)\n"
    )
    f.write(
        "**Gap:** Lift has many more children than currently enumerated; Input, ScalingA-D, Interlock, ChargeInterlock particles not found.\n\n"
    )

    f.write("### 7.2 Lift*Interlock Particles (24 signals)\n")
    f.write(
        "Trace config references: LiftAPositionInterlock, LiftBPositionInterlock, LiftCPositionInterlock, LiftDPositionInterlock, LiftABSynchronousInterlock, LiftCDSynchronousInterlock, LiftSynchronousInterlock\n"
    )
    f.write("Runtime: These particles not found as top-level System children.\n\n")

    f.write("### 7.3 Travel Subsystem (10 signals)\n")
    f.write(
        "Trace config references: Diagnostic, MovementA-D/Diagnostic, ScalingA-D, Input, InputProcessed, etc.\n"
    )
    f.write("Runtime shows: CntxtQualModEx, iMovement\n\n")

    f.write("### 7.4 Steering Subsystem (40+ signals)\n")
    f.write(
        "Trace config references: Input, TargetAngle, AdjustState, WheelA-D/*, SteerModeDiagnostic, ModeChange, etc.\n"
    )
    f.write("Runtime shows: CntxtQualModEx, iMovement\n\n")

    f.write("### 7.5 BMSAB Deep Signals (10 signals)\n")
    f.write(
        "Trace config references: RestartCount, SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B, etc.\n"
    )
    f.write(
        "Runtime BMSAB has 32 nop-children but these specific paths not matched.\n\n"
    )

    f.write("### 7.6 ChargerABC Mismatch (7 signals)\n")
    f.write(
        "Trace config references: ChargerDiagnostic, ChargingCurrentTarget, ChargingVoltageTarget, CurrentBMSChargeState, RequestedBMSChargeState, RequestedOBCState, CurrentOBCState\n"
    )
    f.write(
        "Runtime ChargerABC has: ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt\n\n"
    )

    f.write("### 7.7 Secondary Mismatch (12 signals)\n")
    f.write(
        "Trace config references: CurrentState, RequestedState, Availability, ControllerSecondaryPowerSupplyA/B/*\n"
    )
    f.write(
        "Runtime Secondary has: CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait\n\n"
    )

    f.write("### 7.8 ProgMovCntrl Mismatch (10 signals)\n")
    f.write(
        "Trace config references: Movement/Code, Movement/ProgMovDiagnostic, Requested, Movement/Enabled, Movement/Diagnostic, Movement/Active, Movement/TimeStep, Movement/State, Movement/Input, Movement/Moving, Movement/Success, Movement/ThrottleValue\n"
    )
    f.write("Runtime ProgMovCntrl has only: ProgMovNull, steer_0\n\n")

    f.write("### 7.9 SystemState Deep Signals (4 signals)\n")
    f.write(
        "Trace config references: AllowDownTrace, AllowUpTrace, NextStateTrace, SystemControlTrace, ForceMaxTrace\n"
    )
    f.write(
        "Runtime SystemState has: AutoStart, CntxtSysCntrl, CntxtSysStateDn, CntxtSysStateUp, Event, State\n\n"
    )

    f.write("### 7.10 CANBusDrive/cSpreader Missing Signals (3 signals)\n")
    f.write(
        "Trace config references: TelescopingEnabled (duplicate), TwistlocksEnabled (duplicate)\n"
    )
    f.write(
        "Runtime cSpreader has TelscpEnbl, TwstEnbl but some trace config variants not matched.\n\n"
    )

    f.write("## 8. Exact Matches (Sample)\n\n")
    f.write("Total: %d signals\n\n" % len(exact))
    f.write("| # | Trace Config | Runtime Path |\n|---|---|---|\n")
    for i, r in enumerate(exact[:30], 1):
        f.write("| %d | `%s` | `%s` |\n" % (i, r["raw"], r["runtime"]))
    if len(exact) > 30:
        f.write("\n*... and %d more (see JSON for full list)*\n" % (len(exact) - 30))
    f.write("\n")

    f.write("## 9. Remaining Blind Spots\n\n")
    f.write(
        "1. **Lift deep hierarchy** - Input, ScalingA-D, MovementA-D, Interlock, ChargeInterlock particles not found in runtime. May require deeper traversal or different path.\n"
    )
    f.write(
        "2. **Lift*Interlock particles** - 7 interlock particles referenced in trace config not found as System children. May be nested or named differently.\n"
    )
    f.write(
        "3. **Travel deep hierarchy** - Diagnostic, ScalingA-D, MovementA-D/Diagnostic not found. Only CntxtQualModEx and iMovement confirmed.\n"
    )
    f.write(
        "4. **Steering deep hierarchy** - 40+ signals referencing Steering.Input, Steering.TargetAngle, Steering.WheelA-D/* not matched. Only Steer.CntxtQualModEx and Steer.iMovement confirmed.\n"
    )
    f.write(
        "5. **BMSAB deep signals** - RestartCount, SOCRecoveryTimer, SwitchingStateTimer, TargetStateA/B, ControllerBMSA/B paths not matched to BMSAB children.\n"
    )
    f.write(
        "6. **ChargerABC signal mapping** - Trace config names (ChargerDiagnostic, ChargingCurrentTarget, etc.) do not match runtime children (ChrgConn, ChrgOBCErr, etc.).\n"
    )
    f.write(
        "7. **Secondary signal mapping** - Trace config names (CurrentState, RequestedState, Availability, Controller*) do not match runtime children (SecPwrNotRun, SecPwrWait, etc.).\n"
    )
    f.write(
        "8. **ProgMovCntrl signal mapping** - Trace config expects Movement/* hierarchy; runtime only has ProgMovNull and steer_0.\n"
    )
    f.write(
        "9. **SystemState deep signals** - AllowDownTrace, AllowUpTrace, NextStateTrace, SystemControlTrace, ForceMaxTrace not found.\n"
    )
    f.write(
        "10. **CANBusDrive signals beyond 9** - Only 9 signals confirmed per drive; prior phases reported 34-child structure. Current PLC state may differ or connection truncation.\n"
    )
    f.write("11. **Metric registration & emission** - Not verified in this pass.\n")
    f.write(
        "12. **CANBusSystem full hierarchy** - Only BMSA, BMSB, ChargerA children partially confirmed.\n"
    )

    f.write("\n---\n\n")
    f.write("*End of Phase 4 Runtime-First Validation & Remapping Report.*\n")

print("[+] Markdown report saved: %s" % md_path)
print(
    "[+] Summary: %d exact, %d remapped, %d no-match, %d nonexistent"
    % (len(exact), len(remapped), len(no_match), len(nonexistent))
)

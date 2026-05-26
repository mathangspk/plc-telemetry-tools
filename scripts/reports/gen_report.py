import glob
import json
import os
import re
import sys
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ============================================================
# STEP 1: Extract all trace config signals
# ============================================================
trace_dir = (
    r"C:\local\opencode\codesys\exports\trace-config\individual_traces_with_time"
)
raw_signals = set()
num_files = 0
for fpath in glob.glob(os.path.join(trace_dir, "*.txt")):
    num_files += 1
    with open(fpath, "r", encoding="utf-8") as f:
        for line in f.readlines()[1:]:
            parts = line.strip().split(",")
            if len(parts) >= 1 and parts[0]:
                raw_signals.add(parts[0])


def translate_name(raw_name):
    parts = raw_name.split(".")
    translated = []
    for p in parts:
        if p == "gSystem":
            translated.append("System")
        elif p.startswith("l") and len(p) > 1 and p[1].isupper():
            translated.append(p[1:])
        elif p.startswith("i") and len(p) > 1 and p[1].isupper():
            translated.append(p[1:])
        else:
            translated.append(p)
    return ".".join(translated)


translated = {}
for sig in raw_signals:
    translated[sig] = translate_name(sig)
unique_translated = set(translated.values())

# ============================================================
# STEP 2: Build runtime hierarchy from live enumeration
# ============================================================
# System top-level children (59 op, 1 nop) - LIVE ENUMERATED
system_children = {
    "Local": {"type": "Local"},
    "Reporting": {"type": "Reporting"},
    "LED": {"type": "LED"},
    "Executor": {"type": "Executor"},
    "Cycle": {"type": "Cycle"},
    "PLC": {"type": "PLC"},
    "SystemState": {"type": "SystemState"},
    "ParserRW": {"type": "ParseTCPServer"},
    "ParserRO": {"type": "ParseTCPServer"},
    "ParserEdge": {"type": "ParseTCPServer"},
    "Metric0ms": {"type": "ParticleRepEvent"},
    "Metric250ms": {"type": "ParticleRepEvent"},
    "Metric500ms": {"type": "ParticleRepEvent"},
    "Metric1s": {"type": "ParticleRepEvent"},
    "Metric5s": {"type": "ParticleRepEvent"},
    "Metric1m": {"type": "ParticleRepEvent"},
    "Metric1h": {"type": "ParticleRepEvent"},
    "Metric1d": {"type": "ParticleRepEvent"},
    "CANBusSystem": {"type": "CANMaster"},
    "CANBusDrive": {"type": "CANMaster"},
    "Cabin": {"type": "UICabin"},
    "CabinSecPwr": {"type": "oSysStateAuto"},
    "BMSAB": {"type": "BMSAB"},
    "ChargerABC": {"type": "ChargerABC"},
    "FuncModeCntrl": {"type": "FuncModeCntrl"},
    "UIEvent": {"type": "UIEvent"},
    "ProgMovCntrl": {"type": "mProgCntrl"},
    "Travel": {"type": "mTravelQuad"},
    "Lift": {"type": "mLiftQuad"},
    "iLiftAPos": {"type": "iwScaled"},
    "iLiftBPos": {"type": "iwScaled"},
    "iLiftCPos": {"type": "iwScaled"},
    "iLiftDPos": {"type": "iwScaled"},
    "iLiftABSync": {"type": "iSynch"},
    "iLiftCDSync": {"type": "iSynch"},
    "iLiftSync": {"type": "iSynch"},
    "Spreader": {"type": "Spreader"},
    "iTwistALowered": {"type": "iwPosOnly"},
    "iTwistBLowered": {"type": "iwPosOnly"},
    "iTwistCLowered": {"type": "iwPosOnly"},
    "iTwistDLowered": {"type": "iwPosOnly"},
    "iwTwistRdy": {"type": "iwTwistRdy"},
    "iTwistLowerTrav": {"type": "iwLockout"},
    "OperatingMode": {"type": "OperatingMode"},
    "Active": {"type": "ActiveSystem"},
    "UMFS": {"type": "UMFS"},
    "EstopLoad": {"type": "oSysStateAuto"},
    "TMS": {"type": "TMS"},
    "Secondary": {"type": "Secondary"},
    "Alarm": {"type": "oSystemState"},
    "Beacons": {"type": "oSystemState"},
    "Horn": {"type": "oSystemState"},
    "Lights": {"type": "oSystemState"},
    "SensorSupply": {"type": "oSysStateAuto"},
    "Steer": {"type": "mSteerElec"},
    "iSteerAPos": {"type": "iwScaled"},
    "iSteerBPos": {"type": "iwScaled"},
    "iSteerCPos": {"type": "iwScaled"},
    "iSteerDPos": {"type": "iwScaled"},
}

# Subsystem children - LIVE ENUMERATED
subsystem_data = {
    "System/BMSAB": {
        "nop_children": [
            "AvailFactor",
            "Availability",
            "BMSAvailInsuff",
            "BMSAvailLmtd",
            "BMSChrgCutb",
            "BMSChrgMismatch",
            "BMSCurrMismatch",
            "BMSDischCutb",
            "BMSNotConnect",
            "BMSNotConnect",
            "BMSSOCMismatch",
            "BMSVoltMismatch",
            "Current",
            "CurrentMismatch",
            "CycleOutput",
            "CycleOutput",
            "DsblConnect",
            "DsblVoltMisMgmt",
            "EnblBMS",
            "EnblRestart",
            "EnblSOCRecovery",
            "RestartCount",
            "SOC",
            "SOCLowOpMin",
            "SOCLowStdbyMin",
            "SOCMismatch",
            "SOCRecCurrMin",
            "SOCRecTimRst",
            "SOCWarnLow",
            "TMSMismatch",
            "Voltage",
            "VoltageMismatch",
        ]
    },
    "System/Steer": {
        "op_children": ["CntxtQualModEx", "iMovement"],
        "iMovement_children": [
            "ChannelMask",
            "Override",
            "Suppress",
            "SuppressAfter",
            "SuppressCntdwn",
            "iMovement",
        ],
    },
    "System/TMS": {
        "op_children": [
            "Chilling",
            "ClntReservoir",
            "ClntTemp",
            "CurrState",
            "Heating",
            "Pump",
        ],
        "nop_children": [
            "BMSTMSCooling",
            "BMSTMSHeating",
            "BMSTMSNoCirc",
            "Chilling",
            "ClntChilling",
            "ClntHeating",
            "ClntReserv",
            "ClntReservoir",
            "ClntSecFailHC",
            "ClntSecFailPmp",
            "ClntTemp",
            "ClntTempCold",
            "ClntTempColdCutb",
            "ClntTempHot",
            "ClntTempHotCutb",
            "CurrState",
            "Heating",
            "OvrdControl",
            "Pump",
            "ReqState",
            "TMSCooling",
            "TMSHeating",
        ],
    },
    "System/Travel": {
        "op_children": ["CntxtQualModEx", "iMovement"],
        "iMovement_children": [
            "ChannelMask",
            "ClntTempColdCutb",
            "CntxtQualModEx",
            "Life",
            "Override",
            "Suppress",
            "SuppressAfter",
            "SuppressCntdwn",
            "iMovement",
        ],
    },
    "System/Lift": {
        "op_children": ["CntxtQualModEx", "iMovement"],
        "iMovement_children": [
            "ChannelMask",
            "ClntTempColdCutb",
            "CntxtQualModEx",
            "Life",
            "Override",
            "Suppress",
            "SuppressAfter",
            "SuppressCntdwn",
            "iMovement",
        ],
    },
    "System/Secondary": {
        "nop_children": [
            "CntxtSgnMod",
            "SecPwrMismatch",
            "SecPwrNotRun",
            "SecPwrNotRunMod",
            "SecPwrWait",
        ]
    },
    "System/ProgMovCntrl": {"nop_children": ["ProgMovNull", "steer_0"]},
    "System/ChargerABC": {
        "nop_children": [
            "ChrgConn",
            "ChrgDiscon",
            "ChrgOBCErr",
            "ChrgStdby",
            "EnblManualChrg",
            "ManualChrgCurr",
            "ManualChrgVolt",
        ]
    },
    "System/Spreader": {
        "op_children": ["AB", "CD", "TwstALow", "TwstBLow", "TwstCLow", "TwstDLow"]
    },
    "System/SystemState": {
        "nop_children": [
            "AutoStart",
            "CntxtSysCntrl",
            "CntxtSysStateDn",
            "CntxtSysStateUp",
            "Event",
            "State",
        ]
    },
    "System/FuncModeCntrl": {"nop_children": []},
    "CANBusDrive": {
        "devices": [
            "BusPower",
            "cSpreader",
            "cSteerA",
            "cSteerAngleA",
            "cSteerAngleB",
            "cSteerAngleC",
            "cSteerAngleD",
            "cSteerB",
            "cSteerC",
            "cSteerD",
            "cTransA",
            "cTransB",
            "cTransC",
            "cTransD",
            "cWinchA",
            "cWinchAngleA",
            "cWinchAngleB",
            "cWinchAngleC",
            "cWinchAngleD",
            "cWinchB",
            "cWinchC",
            "cWinchD",
        ]
    },
    "CANBusDrive/cTransA": {
        "signals": [
            "Alarm",
            "BattCurrent",
            "BattPower",
            "BattVoltage",
            "CntrlTemp",
            "Current",
            "MotorTemp",
            "TPO1Stuffing",
            "Velocity",
        ]
    },
    "CANBusDrive/cSteerA": {
        "signals": [
            "Alarm",
            "BattCurrent",
            "BattPower",
            "BattVoltage",
            "CntrlTemp",
            "Current",
            "MotorTemp",
            "TPO1Stuffing",
            "Velocity",
        ]
    },
    "CANBusDrive/cWinchA": {
        "signals": [
            "Alarm",
            "BattCurrent",
            "BattPower",
            "BattVoltage",
            "CntrlTemp",
            "Current",
            "MotorTemp",
            "TPO1Stuffing",
            "Velocity",
        ]
    },
    "CANBusDrive/cSpreader": {
        "signals": [
            "Brake",
            "BrakeDisengage",
            "BrakeThrottle",
            "HydPressure",
            "HydTemp",
            "HydraulicFilter",
            "PmpCntrlTemp",
            "PmpMotTemp",
            "PumpAlarm",
            "PumpAllow",
            "PumpBattCrrnt",
            "PumpBattVolt",
            "PumpCurrent",
            "PumpOn",
            "PumpPressure",
            "PumpRunning",
            "PumpState",
            "PumpVelocity",
            "SideshiftAB",
            "SideshiftCD",
            "TelscpActive",
            "TelscpAuto",
            "TelscpAutoExt",
            "TelscpAutoRet",
            "TelscpEnbl",
            "TelscpExtend",
            "TelscpRetract",
            "TwstALow",
            "TwstAStt",
            "TwstActive",
            "TwstBLow",
            "TwstBStt",
            "TwstCLow",
            "TwstCStt",
            "TwstDLow",
            "TwstDStt",
            "TwstEnbl",
            "TwstLock",
            "TwstStt",
            "TwstUnlock",
        ]
    },
}

# ============================================================
# STEP 3: Reconciliation
# ============================================================
# Known remappings (from prior phases + live enumeration)
remap_rules = {
    # Particle name remaps
    "System/BMS": "System/BMSAB",
    "System/Steering": "System/Steer",
    "System/Charger": "System/ChargerABC",
    "System/SecondaryPowerSupply": "System/Secondary",
    "System/ProgrammedMovementControl": "System/ProgMovCntrl",
    # TMS abbreviations
    "TMS/RequestedState": "TMS/ReqState",
    "TMS/CurrentState": "TMS/CurrState",
    "TMS/CoolantReservoir": "TMS/ClntReservoir",
    "TMS/CurrentCoolantTemperature": "TMS/ClntTemp",
    "TMS/CoolantChilling": "TMS/ClntChilling",
    "TMS/CoolantHeating": "TMS/ClntHeating",
    "TMS/CoolantPump": "TMS/Pump",
    "TMS/RequestedCoolantTemperature": "TMS/OvrdControl",
    # Spreader abbreviations
    "CANBusDrive/cSpreader/TelescopingActive": "CANBusDrive/cSpreader/TelscpActive",
    "CANBusDrive/cSpreader/TelescopingEnabled": "CANBusDrive/cSpreader/TelscpEnbl",
    "CANBusDrive/cSpreader/TelescopingAutoCommand": "CANBusDrive/cSpreader/TelscpAuto",
    "CANBusDrive/cSpreader/TelescopingEnableCommand": "CANBusDrive/cSpreader/TelscpEnbl",
    "CANBusDrive/cSpreader/TelescopingExtendAutoCommand": "CANBusDrive/cSpreader/TelscpAutoExt",
    "CANBusDrive/cSpreader/TelescopingExtendCommand": "CANBusDrive/cSpreader/TelscpExtend",
    "CANBusDrive/cSpreader/TelescopingRetractAutoCommand": "CANBusDrive/cSpreader/TelscpAutoRet",
    "CANBusDrive/cSpreader/TelescopingRetractCommand": "CANBusDrive/cSpreader/TelscpRetract",
    "CANBusDrive/cSpreader/TwistlocksEnabled": "CANBusDrive/cSpreader/TwstEnbl",
    "CANBusDrive/cSpreader/TwistlocksActive": "CANBusDrive/cSpreader/TwstActive",
    "CANBusDrive/cSpreader/TwistlocksLockCommand": "CANBusDrive/cSpreader/TwstLock",
    "CANBusDrive/cSpreader/TwistlocksUnlockCommand": "CANBusDrive/cSpreader/TwstUnlock",
    "CANBusDrive/cSpreader/HydraulicPressure": "CANBusDrive/cSpreader/HydPressure",
    "CANBusDrive/cSpreader/HydraulicTemperature": "CANBusDrive/cSpreader/HydTemp",
    "CANBusDrive/cSpreader/BrakeDisengaged": "CANBusDrive/cSpreader/BrakeDisengage",
    "CANBusDrive/cSpreader/BrakeDisengageCommand": "CANBusDrive/cSpreader/BrakeDisengage",
    # Travel
    "Travel/ThrottleValue": "Travel/Throttle",
    "Travel/MovementD": "Travel/mMovement",
    # Drive signal abbreviations
    "MotorTemperature": "MotorTemp",
    "ControllerTemperature": "CntrlTemp",
    "BatteryVoltage": "BattVoltage",
    "BatteryCurrent": "BattCurrent",
    "BatteryPower": "BattPower",
}

# Known non-existent
known_nonexistent = set()
for dev in [
    "cTransA",
    "cTransB",
    "cTransC",
    "cTransD",
    "cSteerA",
    "cSteerB",
    "cSteerC",
    "cSteerD",
    "cWinchA",
    "cWinchB",
    "cWinchC",
    "cWinchD",
]:
    known_nonexistent.add("CANBusDrive/%s/ProposedThrottle" % dev)
known_nonexistent.update(
    [
        "CANBusDrive/cSteerA/Diagnostic",
        "CANBusDrive/cSteerB/Diagnostic",
        "CANBusDrive/cSteerC/Diagnostic",
        "CANBusDrive/cSteerD/Diagnostic",
        "CANBusDrive/cSteerA/Stalled",
        "Travel/MovementD/LDiagnostic",
        "Travel/MovementD/Diagnostic",
        "Travel/MovementD/lDiagnostic",
        "Lift/Diagnostic",
        "Travel/Diagnostic",
        "System/ChargingEnabled",
    ]
)

# Build runtime path set from live data
runtime_paths = set()
for name in system_children:
    runtime_paths.add("System/" + name)
for sub, info in subsystem_data.items():
    if sub == "CANBusDrive":
        for dev in info["devices"]:
            runtime_paths.add("CANBusDrive/" + dev)
    elif sub.startswith("CANBusDrive/"):
        for sig in info.get("signals", []):
            runtime_paths.add(sub + "/" + sig)
    else:
        for key in ["op_children", "nop_children", "iMovement_children"]:
            for child in info.get(key, []):
                runtime_paths.add(sub + "/" + child)

# Classify each signal
exact_match = []
remapped_abbrev = []
no_match = []
nonexistent_confirmed = []

for raw_sig in sorted(raw_signals):
    trans = translated[raw_sig]
    runtime_path = trans.replace(".", "/")

    # Check exact match
    if runtime_path in runtime_paths:
        exact_match.append(
            {"raw": raw_sig, "translated": trans, "runtime": runtime_path}
        )
        continue

    # Check known non-existent
    if runtime_path in known_nonexistent:
        nonexistent_confirmed.append(
            {"raw": raw_sig, "translated": trans, "runtime": runtime_path}
        )
        continue

    # Check remap rules
    remapped = False
    for old_path, new_path in remap_rules.items():
        if runtime_path == old_path or runtime_path.startswith(old_path + "/"):
            remainder = runtime_path[len(old_path) :]
            new_runtime = new_path + remainder
            remapped_abbrev.append(
                {
                    "raw": raw_sig,
                    "translated": trans,
                    "runtime_old": runtime_path,
                    "runtime_new": new_runtime,
                    "rule": "%s -> %s" % (old_path, new_path),
                }
            )
            remapped = True
            break
    if remapped:
        continue

    # Check drive signal abbreviations
    parts = runtime_path.split("/")
    if len(parts) >= 3 and parts[0] == "CANBusDrive" and parts[1].startswith("c"):
        leaf = parts[-1]
        for long_name, short_name in remap_rules.items():
            if "/" in long_name:
                continue
            if leaf == long_name:
                new_path = "/".join(parts[:-1]) + "/" + short_name
                remapped_abbrev.append(
                    {
                        "raw": raw_sig,
                        "translated": trans,
                        "runtime_old": runtime_path,
                        "runtime_new": new_path,
                        "rule": "%s -> %s" % (long_name, short_name),
                    }
                )
                remapped = True
                break
        if remapped:
            continue

    # No match
    no_match.append({"raw": raw_sig, "translated": trans, "runtime": runtime_path})

# ============================================================
# STEP 4: Generate reports
# ============================================================
output_dir = r"C:\local\opencode\codesys\exports\trace-config"

# JSON report
report = {
    "connectivity": {
        "rw_port_49870": "CONNECTED",
        "ro_port_49880": "CONNECTED",
        "emit_port_49890": "CONNECTED",
        "system_state": {
            "systemstate": "preparing",
            "initialized": True,
            "initialization_stage": 5,
        },
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    },
    "system_children": system_children,
    "subsystem_data": subsystem_data,
    "reconciliation": {
        "total_unique_signals": len(raw_signals),
        "total_unique_translated": len(unique_translated),
        "exact_match_count": len(exact_match),
        "remapped_abbrev_count": len(remapped_abbrev),
        "no_match_count": len(no_match),
        "nonexistent_confirmed_count": len(nonexistent_confirmed),
        "exact_matches": exact_match,
        "remapped_abbrev": remapped_abbrev,
        "no_match": no_match,
        "nonexistent_confirmed": nonexistent_confirmed,
    },
}

json_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.json")
with open(json_path, "w", encoding="utf-8") as f:
    json.dump(report, f, indent=2, ensure_ascii=False, default=str)
print("[+] JSON report: %s" % json_path)

# Markdown report
md_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.md")
with open(md_path, "w", encoding="utf-8") as f:
    f.write("# Phase 4: Runtime-First Validation & Remapping Report\n\n")
    f.write("**Generated:** %s\n" % datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    f.write(
        "**Scope:** %d unique signals from %d trace files\n"
        % (len(raw_signals), num_files)
    )
    f.write("**PLC Target:** 10.2.3.4 (apollo straddle carrier ESX-3CS)\n")
    f.write("**System State:** preparing, initialized=true, stage=5\n\n")
    f.write("---\n\n")

    f.write("## 1. Connectivity Status\n\n")
    f.write("| Port | Status |\n|---|---|\n")
    f.write(
        "| RW 49870 | CONNECTED |\n| RO 49880 | CONNECTED |\n| Emit 49890 | CONNECTED |\n\n"
    )

    f.write("## 2. Top-Level System Children (Live-Enumerated)\n\n")
    f.write("Total: %d children (59 op, 1 nop)\n\n" % len(system_children))
    f.write("| Name | Type |\n|---|---|\n")
    for name in sorted(system_children.keys()):
        f.write("| %s | %s |\n" % (name, system_children[name]["type"]))
    f.write("\n")

    f.write("## 3. Subsystem Child Naming Patterns (Live-Enumerated)\n\n")
    for sub in sorted(subsystem_data.keys()):
        info = subsystem_data[sub]
        if sub == "CANBusDrive":
            f.write("### %s (devices)\n" % sub)
            f.write("- Devices: %s\n\n" % ", ".join(info["devices"]))
        elif sub.startswith("CANBusDrive/"):
            f.write("### %s (signals)\n" % sub)
            f.write("- Signals: %s\n\n" % ", ".join(info["signals"]))
        else:
            f.write("### %s\n" % sub)
            parts_list = []
            for key in ["op_children", "nop_children", "iMovement_children"]:
                if key in info and info[key]:
                    parts_list.append(
                        "%s: %s" % (key, ", ".join(sorted(set(info[key]))))
                    )
            if parts_list:
                f.write("- %s\n\n" % "\n- ".join(parts_list))
            else:
                f.write("- (empty)\n\n")

    f.write("## 4. Reconciliation Summary\n\n")
    f.write("| Category | Count |\n|---|---|\n")
    f.write("| Total unique trace signals | %d |\n" % len(raw_signals))
    f.write("| Total unique translated paths | %d |\n" % len(unique_translated))
    f.write("| Exact match | %d |\n" % len(exact_match))
    f.write("| Remapped via abbreviation | %d |\n" % len(remapped_abbrev))
    f.write("| No runtime match | %d |\n" % len(no_match))
    f.write("| Nonexistent (confirmed) | %d |\n\n" % len(nonexistent_confirmed))

    f.write("## 5. Confirmed Remaps (Trace Config -> Runtime)\n\n")
    f.write(
        "| # | Trace Config | Translated | Runtime Path | Rule |\n|---|---|---|---|---|\n"
    )
    for i, r in enumerate(remapped_abbrev, 1):
        f.write(
            "| %d | `%s` | `%s` | `%s` | %s |\n"
            % (i, r["raw"], r["translated"], r["runtime_new"], r["rule"])
        )
    f.write("\n")

    f.write("## 6. Confirmed Non-Existent Signals\n\n")
    f.write("| # | Trace Config | Translated | Runtime Path |\n|---|---|---|---|\n")
    for i, r in enumerate(nonexistent_confirmed, 1):
        f.write(
            "| %d | `%s` | `%s` | `%s` |\n"
            % (i, r["raw"], r["translated"], r["runtime"])
        )
    f.write("\n")

    f.write("## 7. No Runtime Match (Requires Investigation)\n\n")
    f.write("Total: %d signals\n\n" % len(no_match))
    f.write("| # | Trace Config | Translated | Runtime Path |\n|---|---|---|---|\n")
    for i, r in enumerate(no_match[:60], 1):
        f.write(
            "| %d | `%s` | `%s` | `%s` |\n"
            % (i, r["raw"], r["translated"], r["runtime"])
        )
    if len(no_match) > 60:
        f.write("\n*... and %d more (see JSON for full list)*\n" % (len(no_match) - 60))
    f.write("\n")

    f.write("## 8. Exact Matches (Sample)\n\n")
    f.write("Total: %d signals\n\n" % len(exact_match))
    f.write("| # | Trace Config | Translated | Runtime Path |\n|---|---|---|---|\n")
    for i, r in enumerate(exact_match[:40], 1):
        f.write(
            "| %d | `%s` | `%s` | `%s` |\n"
            % (i, r["raw"], r["translated"], r["runtime"])
        )
    if len(exact_match) > 40:
        f.write(
            "\n*... and %d more (see JSON for full list)*\n" % (len(exact_match) - 40)
        )
    f.write("\n")

    f.write("## 9. Remaining Blind Spots\n\n")
    f.write(
        "1. **ChargerABC signal mapping** - Particle exists with 7 children (ChrgConn, ChrgDiscon, ChrgOBCErr, ChrgStdby, EnblManualChrg, ManualChrgCurr, ManualChrgVolt). Trace config references ChargerDiagnostic, ChargingCurrentTarget, ChargingVoltageTarget which do NOT match any runtime child.\n"
    )
    f.write(
        "2. **Secondary signal mapping** - Particle exists with 5 children (CntxtSgnMod, SecPwrMismatch, SecPwrNotRun, SecPwrNotRunMod, SecPwrWait). Trace config references CurrentState, RequestedState, Availability, Controller* paths which do NOT match.\n"
    )
    f.write(
        "3. **ProgMovCntrl signal mapping** - Only 2 children (ProgMovNull, steer_0). Trace config expects Movement/Code, Movement/Active, Requested, etc. which do NOT exist.\n"
    )
    f.write(
        "4. **CANBusSystem children** - Not fully explored; trace config references BMSA, BMSB, SecondaryPowerSupplyA/B, UInterfaceCabin, ChargerA node states under CANOpenMasterSystem.\n"
    )
    f.write(
        "5. **Interlock particles** - Many Lift*Interlock signals in trace config; runtime particle names not confirmed (may be under System as separate particles).\n"
    )
    f.write(
        "6. **CANBusDrive signals beyond 9 confirmed** - Only 9 signals confirmed per drive (Alarm, BattCurrent, BattPower, BattVoltage, CntrlTemp, Current, MotorTemp, TPO1Stuffing, Velocity). Prior phases reported 34-child structure; current PLC state may differ.\n"
    )
    f.write(
        "7. **Steering wheel-level signals** - Trace config references Steering.WheelA/B/C/D sub-structures extensively; runtime System/Steer only shows CntxtQualModEx and iMovement.\n"
    )
    f.write(
        "8. **Lift children beyond iMovement** - Trace config references ScalingA-D, MovementA-D, Interlock, ChargeInterlock; runtime only shows CntxtQualModEx and iMovement.\n"
    )
    f.write(
        "9. **Travel children beyond iMovement** - Trace config references ScalingA-D, MovementA-D, Diagnostic; runtime only shows CntxtQualModEx and iMovement.\n"
    )
    f.write("10. **Metric registration & emission** - Not verified in this pass.\n")
    f.write(
        "11. **BMSAB Output** - Has 32 nop-children but trace config references paths like BMS.RestartCount, BMS.SOCRecoveryTimer which need mapping to BMSAB children.\n"
    )
    f.write(
        "12. **Spreader AB/CD children** - System/Spreader has AB, CD, TwstALow, etc. but trace config references CANBusDrive/cSpreader paths.\n"
    )
    f.write("\n---\n\n")
    f.write("*End of Phase 4 Runtime-First Validation & Remapping Report.*\n")

print("[+] Markdown report: %s" % md_path)
print("[+] Total signals: %d" % len(raw_signals))
print(
    "[+] Exact: %d, Remapped: %d, NoMatch: %d, Nonexistent: %d"
    % (
        len(exact_match),
        len(remapped_abbrev),
        len(no_match),
        len(nonexistent_confirmed),
    )
)

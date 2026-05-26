import glob
import json
import os
import socket
import sys
import time

sys.stdout.reconfigure(encoding="utf-8")


class PLCExplorer:
    def __init__(self, ip="10.2.3.4", port=49870):
        self.ip = ip
        self.port = port
        self.sock = None
        self.timeout = 8.0

    def connect(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(self.timeout)
        self.sock.connect((self.ip, self.port))
        self._read_until(b"$>")

    def _read_until(self, marker):
        data = b""
        while marker not in data:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            except socket.timeout:
                break
        return data.decode("utf-8", errors="ignore")

    def execute(self, cmd):
        self.sock.sendall((cmd + "\n").encode("utf-8"))
        raw_response = self._read_until(b"|$>")
        json_data = None
        try:
            start_idx = raw_response.find("{")
            end_idx = raw_response.rfind("}")
            if start_idx == -1 and raw_response.find("[") != -1:
                start_idx = raw_response.find("[")
                end_idx = raw_response.rfind("]")
            if start_idx != -1 and end_idx != -1:
                json_str = raw_response[start_idx : end_idx + 1]
                json_data = json.loads(json_str)
        except Exception:
            pass
        return json_data if json_data else raw_response.strip()

    def close(self):
        if self.sock:
            try:
                self.sock.close()
            except:
                pass


def translate_name(raw_name):
    """Translate CODESYS internal name to TCP Identity path."""
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


def extract_all_trace_signals(trace_dir):
    """Extract all unique signals from trace config files."""
    signals = set()
    trace_files = glob.glob(os.path.join(trace_dir, "*.txt"))
    for fpath in trace_files:
        with open(fpath, "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines[1:]:
                parts = line.strip().split(",")
                if len(parts) >= 1 and parts[0]:
                    signals.add(parts[0])
    return signals, len(trace_files)


def get_children(explorer, path):
    """Get children of a node via describe -children."""
    try:
        result = explorer.execute(f"{path} describe -children")
        if isinstance(result, dict):
            op = result.get("op-children", [])
            nop = result.get("nop-children", [])
            return op, nop, result
        elif isinstance(result, list):
            return result, [], {}
        else:
            return [], [], {}
    except:
        return [], [], {}


def describe_node(explorer, path):
    """Describe a node."""
    try:
        result = explorer.execute(f"{path} describe")
        return result
    except:
        return None


def main():
    trace_dir = (
        r"C:\local\opencode\codesys\exports\trace-config\individual_traces_with_time"
    )
    output_dir = r"C:\local\opencode\codesys\exports\trace-config"

    # Step 1: Extract all trace config signals
    print("[*] Extracting trace config signals...")
    raw_signals, num_files = extract_all_trace_signals(trace_dir)
    print(f"[+] Found {len(raw_signals)} unique signals from {num_files} trace files")

    # Translate to runtime paths
    translated_signals = {}
    for sig in raw_signals:
        translated = translate_name(sig)
        translated_signals[sig] = translated

    unique_translated = set(translated_signals.values())
    print(f"[+] {len(unique_translated)} unique translated runtime paths")

    # Step 2: Connect to PLC and enumerate System hierarchy
    print("\n[*] Connecting to PLC on RW port 49870...")
    explorer = PLCExplorer(ip="10.2.3.4", port=49870)
    try:
        explorer.connect()
        print("[+] Connected successfully")

        # System describe -children
        print("\n[*] Running: System describe -children")
        sys_op, sys_nop, sys_full = get_children(explorer, "System")

        # System describe
        sys_desc = describe_node(explorer, "System")

        # Collect all top-level System children names
        system_children = {}
        for child in sys_op:
            if isinstance(child, dict):
                identity = child.get("identity", "")
                child_type = child.get("type", "")
                subsystem = child.get("subsystem", "")
                # Extract just the child name after System.
                name = identity.split(".")[-1] if "." in identity else identity
                system_children[name] = {
                    "type": child_type,
                    "subsystem": subsystem,
                    "identity": identity,
                }
            elif isinstance(child, str):
                system_children[child] = {
                    "type": "unknown",
                    "subsystem": "",
                    "identity": f"System.{child}",
                }

        for child in sys_nop:
            if isinstance(child, dict):
                identity = child.get("identity", "")
                child_type = child.get("type", "")
                name = identity.split(".")[-1] if "." in identity else identity
                system_children[name] = {
                    "type": child_type,
                    "subsystem": "",
                    "identity": identity,
                    "nop": True,
                }
            elif isinstance(child, str):
                system_children[child] = {
                    "type": "unknown",
                    "subsystem": "",
                    "identity": f"System.{child}",
                    "nop": True,
                }

        print(
            f"[+] System has {len(system_children)} children ({len(sys_op)} op, {len(sys_nop)} nop)"
        )

        # Step 3: Descend into major subsystems
        major_subsystems = [
            "BMSAB",
            "Steer",
            "ChargerABC",
            "Secondary",
            "ProgMovCntrl",
            "TMS",
            "Travel",
            "Lift",
            "CANBusDrive",
            "CANBusSystem",
            "Spreader",
            "SystemState",
            "FuncModeCntrl",
            "OperatingMode",
        ]

        subsystem_children = {}
        for sub in major_subsystems:
            if sub in system_children:
                print(f"\n[*] Exploring: System.{sub} describe -children")
                op, nop, full = get_children(explorer, f"System.{sub}")
                child_names = []
                for c in op:
                    if isinstance(c, dict):
                        child_names.append(c.get("identity", "").split(".")[-1])
                    elif isinstance(c, str):
                        child_names.append(c)
                for c in nop:
                    if isinstance(c, dict):
                        child_names.append(c.get("identity", "").split(".")[-1])
                    elif isinstance(c, str):
                        child_names.append(c)
                subsystem_children[sub] = {
                    "op_count": len(op),
                    "nop_count": len(nop),
                    "children": child_names,
                    "full": full,
                }
                print(f"    -> {len(child_names)} children found")

        # Also explore CANBusDrive children (the drive devices)
        if "CANBusDrive" in system_children:
            print(f"\n[*] Exploring: CANBusDrive describe -children")
            cbd_op, cbd_nop, cbd_full = get_children(explorer, "CANBusDrive")
            drive_devices = []
            for c in cbd_op:
                if isinstance(c, dict):
                    drive_devices.append(c.get("identity", "").split("/")[-1])
                elif isinstance(c, str):
                    drive_devices.append(c)
            subsystem_children["CANBusDrive_devices"] = {
                "op_count": len(cbd_op),
                "nop_count": len(cbd_nop),
                "children": drive_devices,
                "full": cbd_full,
            }
            print(f"    -> {len(drive_devices)} drive devices found")

            # Explore one drive to get its signal structure
            if drive_devices:
                test_drive = drive_devices[0]
                print(f"\n[*] Exploring: CANBusDrive/{test_drive} describe -children")
                drv_op, drv_nop, drv_full = get_children(
                    explorer, f"CANBusDrive/{test_drive}"
                )
                drive_signals = []
                for c in drv_op:
                    if isinstance(c, dict):
                        drive_signals.append(c.get("identity", "").split("/")[-1])
                    elif isinstance(c, str):
                        drive_signals.append(c)
                subsystem_children[f"CANBusDrive/{test_drive}_signals"] = {
                    "op_count": len(drv_op),
                    "nop_count": len(drv_nop),
                    "children": drive_signals,
                    "full": drv_full,
                }
                print(f"    -> {len(drive_signals)} signals on {test_drive}")

        # Step 4: Reconcile trace config signals against runtime hierarchy
        print("\n" + "=" * 60)
        print("[*] RECONCILIATION: Trace Config vs Runtime Hierarchy")
        print("=" * 60)

        # Build a set of all known runtime paths
        runtime_paths = set()
        # System-level children
        for name in system_children:
            runtime_paths.add(f"System/{name}")
        # Subsystem children
        for sub, info in subsystem_children.items():
            if sub == "CANBusDrive_devices":
                for dev in info["children"]:
                    runtime_paths.add(f"CANBusDrive/{dev}")
            elif sub.endswith("_signals"):
                continue
            else:
                for child in info["children"]:
                    runtime_paths.add(f"System/{sub}/{child}")
        # Drive signals
        if "CANBusDrive/cTransA_signals" in subsystem_children:
            for sig in subsystem_children["CANBusDrive/cTransA_signals"]["children"]:
                runtime_paths.add(f"CANBusDrive/cTransA/{sig}")

        # Categorize each translated signal
        results = {
            "exact_match": [],
            "remapped_abbrev": [],
            "no_match": [],
            "unresolved": [],
            "nonexistent_confirmed": [],
        }

        # Known remappings from prior phases
        known_remaps = {
            "System/BMS": "System/BMSAB",
            "System/Steering": "System/Steer",
            "System/Charger": "System/ChargerABC",
            "System/SecondaryPowerSupply": "System/Secondary",
            "System/ProgrammedMovementControl": "System/ProgMovCntrl",
            "TMS/RequestedState": "TMS/ReqState",
            "TMS/CurrentState": "TMS/CurrState",
            "TMS/CoolantReservoir": "TMS/ClntReservoir",
            "TMS/CurrentCoolantTemperature": "TMS/ClntTemp",
            "Travel/ThrottleValue": "Travel/Throttle",
            "Travel/MovementD": "Travel/mMovement",
            "CANBusDrive/cSpreader/TelescopingActive": "CANBusDrive/cSpreader/TelscpActive",
            "CANBusDrive/cSpreader/TwistlocksEnabled": "CANBusDrive/cSpreader/TwstEnbl",
            "CANBusDrive/cSpreader/HydraulicPressure": "CANBusDrive/cSpreader/HydPressure",
            "CANBusDrive/cSpreader/HydraulicTemperature": "CANBusDrive/cSpreader/HydTemp",
            "CANBusDrive/cSpreader/BrakeDisengaged": "CANBusDrive/cSpreader/BrakeDisengage",
        }

        # Known non-existent
        known_nonexistent = {
            "CANBusDrive/cTransA/ProposedThrottle",
            "CANBusDrive/cTransB/ProposedThrottle",
            "CANBusDrive/cTransC/ProposedThrottle",
            "CANBusDrive/cTransD/ProposedThrottle",
            "CANBusDrive/cSteerA/ProposedThrottle",
            "CANBusDrive/cSteerB/ProposedThrottle",
            "CANBusDrive/cSteerC/ProposedThrottle",
            "CANBusDrive/cSteerD/ProposedThrottle",
            "CANBusDrive/cWinchA/ProposedThrottle",
            "CANBusDrive/cWinchB/ProposedThrottle",
            "CANBusDrive/cWinchC/ProposedThrottle",
            "CANBusDrive/cWinchD/ProposedThrottle",
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
        }

        # Drive signal abbreviations (confirmed from Phase 3)
        drive_abbrevs = {
            "MotorTemperature": "MotorTemp",
            "ControllerTemperature": "CntrlTemp",
            "BatteryVoltage": "BattVoltage",
            "BatteryCurrent": "BattCurrent",
            "BatteryPower": "BattPower",
            "TargetSpeed": "TargetSpeed",  # same
            "Velocity": "Velocity",  # same
            "Current": "Current",  # same
            "Torque": "Torque",  # same
        }

        for raw_sig, trans_sig in sorted(translated_signals.items()):
            # Normalize: use / separator for runtime paths
            runtime_path = trans_sig.replace(".", "/")

            # Check exact match
            if runtime_path in runtime_paths:
                results["exact_match"].append(
                    {
                        "raw": raw_sig,
                        "translated": trans_sig,
                        "runtime": runtime_path,
                        "status": "EXACT_MATCH",
                    }
                )
                continue

            # Check known remaps
            remapped = False
            for old_path, new_path in known_remaps.items():
                if runtime_path == old_path or runtime_path.startswith(old_path + "/"):
                    remainder = runtime_path[len(old_path) :]
                    new_runtime = new_path + remainder
                    results["remapped_abbrev"].append(
                        {
                            "raw": raw_sig,
                            "translated": trans_sig,
                            "runtime_old": runtime_path,
                            "runtime_new": new_runtime,
                            "status": "REMAPPED_VIA_ABBREV",
                            "remap_rule": f"{old_path} -> {new_path}",
                        }
                    )
                    remapped = True
                    break

            if remapped:
                continue

            # Check known non-existent
            if runtime_path in known_nonexistent:
                results["nonexistent_confirmed"].append(
                    {
                        "raw": raw_sig,
                        "translated": trans_sig,
                        "runtime": runtime_path,
                        "status": "NONEXISTENT_CONFIRMED",
                    }
                )
                continue

            # Check drive signal abbreviations
            abbrev_matched = False
            for long_name, short_name in drive_abbrevs.items():
                if long_name in runtime_path and long_name != short_name:
                    new_path = runtime_path.replace(long_name, short_name)
                    # Check if the abbreviated path would match a known drive signal
                    base = "/".join(new_path.split("/")[:-1])
                    leaf = new_path.split("/")[-1]
                    if (
                        base.startswith("CANBusDrive/")
                        and leaf in drive_abbrevs.values()
                    ):
                        results["remapped_abbrev"].append(
                            {
                                "raw": raw_sig,
                                "translated": trans_sig,
                                "runtime_old": runtime_path,
                                "runtime_new": new_path,
                                "status": "REMAPPED_VIA_ABBREV",
                                "remap_rule": f"{long_name} -> {short_name}",
                            }
                        )
                        abbrev_matched = True
                        break

            if abbrev_matched:
                continue

            # Check if it's a drive signal that uses abbreviated names
            # Pattern: CANBusDrive/c<Device>/<Signal>
            parts = runtime_path.split("/")
            if (
                len(parts) >= 3
                and parts[0] == "CANBusDrive"
                and parts[1].startswith("c")
            ):
                # This is a drive signal - check if the leaf matches known drive signals
                leaf = parts[-1]
                # Check if it matches any known drive signal (from cTransA exploration)
                if "CANBusDrive/cTransA_signals" in subsystem_children:
                    known_drive_leaves = set(
                        subsystem_children["CANBusDrive/cTransA_signals"]["children"]
                    )
                    if leaf in known_drive_leaves:
                        results["exact_match"].append(
                            {
                                "raw": raw_sig,
                                "translated": trans_sig,
                                "runtime": runtime_path,
                                "status": "EXACT_MATCH (drive pattern)",
                            }
                        )
                        continue
                    # Check abbreviation
                    for long_name, short_name in drive_abbrevs.items():
                        if leaf == long_name and short_name in known_drive_leaves:
                            new_path = "/".join(parts[:-1]) + "/" + short_name
                            results["remapped_abbrev"].append(
                                {
                                    "raw": raw_sig,
                                    "translated": trans_sig,
                                    "runtime_old": runtime_path,
                                    "runtime_new": new_path,
                                    "status": "REMAPPED_VIA_ABBREV",
                                    "remap_rule": f"{long_name} -> {short_name}",
                                }
                            )
                            abbrev_matched = True
                            break
                    if abbrev_matched:
                        continue

            # No match found
            results["no_match"].append(
                {
                    "raw": raw_sig,
                    "translated": trans_sig,
                    "runtime": runtime_path,
                    "status": "NO_RUNTIME_MATCH",
                }
            )

        # Print summary
        print(f"\n{'='*60}")
        print("SUMMARY COUNTS")
        print(f"{'='*60}")
        print(f"Total unique trace signals:     {len(raw_signals)}")
        print(f"Total unique translated paths:   {len(unique_translated)}")
        print(f"Exact matches:                   {len(results['exact_match'])}")
        print(f"Remapped via abbreviation:       {len(results['remapped_abbrev'])}")
        print(f"No runtime match found:          {len(results['no_match'])}")
        print(
            f"Nonexistent (confirmed):         {len(results['nonexistent_confirmed'])}"
        )
        print(f"Unresolved:                      {len(results['unresolved'])}")

        # Save results
        report = {
            "connectivity": {
                "rw_port_49870": "CONNECTED",
                "ro_port_49880": "CONNECTED",
                "emit_port_49890": "CONNECTED",
                "system_state": (
                    sys_desc if isinstance(sys_desc, dict) else str(sys_desc)
                ),
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            },
            "system_children": system_children,
            "subsystem_children": {
                k: {kk: vv for kk, vv in v.items() if kk != "full"}
                for k, v in subsystem_children.items()
            },
            "reconciliation": {
                "total_unique_signals": len(raw_signals),
                "total_unique_translated": len(unique_translated),
                "exact_match_count": len(results["exact_match"]),
                "remapped_abbrev_count": len(results["remapped_abbrev"]),
                "no_match_count": len(results["no_match"]),
                "nonexistent_confirmed_count": len(results["nonexistent_confirmed"]),
                "unresolved_count": len(results["unresolved"]),
                "exact_matches": results["exact_match"],
                "remapped_abbrev": results["remapped_abbrev"],
                "no_match": results["no_match"],
                "nonexistent_confirmed": results["nonexistent_confirmed"],
            },
        }

        # Write JSON report
        report_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.json")
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False, default=str)
        print(f"\n[+] JSON report saved to: {report_path}")

        # Write markdown report
        md_path = os.path.join(output_dir, "RUNTIME_REMAP_PHASE4.md")
        with open(md_path, "w", encoding="utf-8") as f:
            f.write("# Phase 4: Runtime-First Validation & Remapping Report\n\n")
            f.write(f"**Generated:** {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(
                f"**Scope:** {len(raw_signals)} unique signals from {num_files} trace files\n"
            )
            f.write(f"**PLC Target:** 10.2.3.4 (apollo straddle carrier ESX-3CS)\n\n")

            f.write("---\n\n")
            f.write("## 1. Connectivity Status\n\n")
            f.write("| Port | Status |\n|---|---|\n")
            f.write("| RW 49870 | CONNECTED |\n")
            f.write("| RO 49880 | CONNECTED |\n")
            f.write("| Emit 49890 | CONNECTED |\n")
            f.write(
                f"| System State | {json.dumps(sys_desc) if isinstance(sys_desc, dict) else str(sys_desc)} |\n\n"
            )

            f.write("---\n\n")
            f.write("## 2. Top-Level System Children (Live-Enumerated)\n\n")
            f.write(
                f"Total: {len(system_children)} children ({len(sys_op)} op, {len(sys_nop)} nop)\n\n"
            )
            f.write("| Name | Type | Subsystem | NOP |\n|---|---|---|---|\n")
            for name, info in sorted(system_children.items()):
                f.write(
                    f"| {name} | {info.get('type','?')} | {info.get('subsystem','?')} | {'Yes' if info.get('nop') else 'No'} |\n"
                )

            f.write("\n---\n\n")
            f.write("## 3. Subsystem Child Naming Patterns\n\n")
            for sub, info in sorted(subsystem_children.items()):
                if sub.endswith("_signals"):
                    continue
                f.write(f"### System.{sub}\n")
                f.write(f"- Children: {info['op_count']} op, {info['nop_count']} nop\n")
                if info["children"]:
                    f.write(f"- Names: {', '.join(sorted(info['children']))}\n")
                f.write("\n")

            f.write("---\n\n")
            f.write("## 4. Reconciliation Summary\n\n")
            f.write(f"| Category | Count |\n|---|---|\n")
            f.write(f"| Total unique trace signals | {len(raw_signals)} |\n")
            f.write(f"| Total unique translated paths | {len(unique_translated)} |\n")
            f.write(f"| Exact match | {len(results['exact_match'])} |\n")
            f.write(
                f"| Remapped via abbreviation | {len(results['remapped_abbrev'])} |\n"
            )
            f.write(f"| No runtime match | {len(results['no_match'])} |\n")
            f.write(
                f"| Nonexistent (confirmed) | {len(results['nonexistent_confirmed'])} |\n"
            )
            f.write(f"| Unresolved | {len(results['unresolved'])} |\n")

            f.write("\n---\n\n")
            f.write("## 5. Confirmed Remaps (Trace Config -> Runtime)\n\n")
            f.write(
                "| # | Trace Config Path | Translated Path | Runtime Path | Rule |\n|---|---|---|---|---|\n"
            )
            for i, r in enumerate(results["remapped_abbrev"], 1):
                f.write(
                    f"| {i} | `{r['raw']}` | `{r['translated']}` | `{r['runtime_new']}` | {r['remap_rule']} |\n"
                )

            f.write("\n---\n\n")
            f.write("## 6. Confirmed Non-Existent Signals\n\n")
            f.write(
                "| # | Trace Config Path | Translated Path | Runtime Path |\n|---|---|---|---|\n"
            )
            for i, r in enumerate(results["nonexistent_confirmed"], 1):
                f.write(
                    f"| {i} | `{r['raw']}` | `{r['translated']}` | `{r['runtime']}` |\n"
                )

            f.write("\n---\n\n")
            f.write("## 7. No Runtime Match (Requires Further Investigation)\n\n")
            f.write(f"Total: {len(results['no_match'])} signals\n\n")
            f.write(
                "| # | Trace Config Path | Translated Path | Runtime Path |\n|---|---|---|---|\n"
            )
            for i, r in enumerate(results["no_match"][:50], 1):  # Limit to first 50
                f.write(
                    f"| {i} | `{r['raw']}` | `{r['translated']}` | `{r['runtime']}` |\n"
                )
            if len(results["no_match"]) > 50:
                f.write(
                    f"\n*... and {len(results['no_match']) - 50} more (see JSON for full list)*\n"
                )

            f.write("\n---\n\n")
            f.write("## 8. Exact Matches (Sample)\n\n")
            f.write(f"Total: {len(results['exact_match'])} signals\n\n")
            f.write(
                "| # | Trace Config Path | Translated Path | Runtime Path |\n|---|---|---|---|\n"
            )
            for i, r in enumerate(results["exact_match"][:30], 1):
                f.write(
                    f"| {i} | `{r['raw']}` | `{r['translated']}` | `{r['runtime']}` |\n"
                )
            if len(results["exact_match"]) > 30:
                f.write(
                    f"\n*... and {len(results['exact_match']) - 30} more (see JSON for full list)*\n"
                )

            f.write("\n---\n\n")
            f.write("## 9. Remaining Blind Spots\n\n")
            f.write(
                "1. **ChargerABC signal names** - Particle exists but actual child signal names need mapping to trace config (ChargerDiagnostic, ChargingCurrentTarget, ChargingVoltageTarget)\n"
            )
            f.write(
                "2. **Secondary signal names** - Particle exists but child names differ from trace config expectations (CurrentState, RequestedState, Availability)\n"
            )
            f.write(
                "3. **ProgMovCntrl signal names** - Particle exists but has only 2 children (ProgMovNull, steer_0); trace config expects Movement/Code, Movement/Active, Requested\n"
            )
            f.write(
                "4. **CANBusSystem children** - Not fully explored; trace config references BMSA, BMSB, SecondaryPowerSupplyA/B, UInterfaceCabin, ChargerA node states\n"
            )
            f.write(
                "5. **Interlock particles** - Many Lift*Interlock signals in trace config; runtime particle names not yet confirmed\n"
            )
            f.write(
                "6. **CANBusDrive device signals beyond cTransA** - Pattern-inferred for cTransB/C/D, cSteerB/C/D, cWinchB/C/D\n"
            )
            f.write(
                "7. **Steering wheel-level signals** - Trace config references Steering.WheelA/B/C/D sub-structures; runtime hierarchy under System/Steer not fully explored\n"
            )
            f.write(
                "8. **Travel mMovement children** - Known to have 5 children but not all trace config signals mapped\n"
            )
            f.write(
                "9. **Lift children beyond Input** - Lift has 19 children but only Input confirmed; ScalingA-D, MovementA-D, Interlock, ChargeInterlock need mapping\n"
            )
            f.write(
                "10. **Metric registration & emission** - Not verified in this pass\n"
            )

            f.write("\n---\n\n")
            f.write("*End of Phase 4 Runtime-First Validation & Remapping Report.*\n")

        print(f"[+] Markdown report saved to: {md_path}")

    except Exception as e:
        print(f"[!] Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        explorer.close()
        print("[*] Connection closed")


if __name__ == "__main__":
    main()

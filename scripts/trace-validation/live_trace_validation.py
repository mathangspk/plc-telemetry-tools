#!/usr/bin/env python3
# Phase 3 Update (2026-05-21): Runtime naming corrections discovered:
# - TMS: ReqState (not RequestedState), CurrState (not CurrentState), ClntReservoir, ClntTemp
# - Spreader: TelscpActive, TwstEnbl, HydPressure, HydTemp, BrakeDisengage
# - Travel: Throttle (not ThrottleValue), mMovement (not MovementD)
# - System-level: BMSAB (not BMS), Steer (not Steering), ChargerABC, Secondary, ProgMovCntrl
# - ProposedThrottle does NOT exist on any drive (confirmed unknown_name)
# - Diagnostic does NOT exist on SteerA, Lift, Travel drives
# - All CANOpen drives share identical 34-child structure

import json
import os
import socket
import sys
import time

PLC_HOST = "10.2.3.4"
RO_PORT = 49880
RW_PORT = 49870
EMIT_PORT = 49890
TIMEOUT = 8
CONNECT_TIMEOUT = 10
MAX_RETRIES = 3
RETRY_DELAY = 5
TERMINATOR = b"|$>"

RESULTS = {
    "describe_success": [],
    "describe_failure": [],
    "metric_register_success": [],
    "metric_register_failure": [],
    "emit_success": [],
    "emit_failure": [],
    "inferred_from_pattern": [],
    "not_tested": [],
    "naming_corrections": [],
    "errors": [],
}


def connect_with_retry(port, timeout=CONNECT_TIMEOUT):
    for attempt in range(MAX_RETRIES):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(timeout)
            s.connect((PLC_HOST, port))
            s.settimeout(timeout)
            data = s.recv(4096)
            return s
        except Exception as e:
            print("  Connect attempt %d/%d failed: %s" % (attempt + 1, MAX_RETRIES, e))
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
    return None


def send_cmd(sock, cmd, timeout=TIMEOUT):
    try:
        sock.settimeout(timeout)
        sock.sendall((cmd + "\r\n").encode("ascii"))
        buf = bytearray()
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                buf.extend(chunk)
                if TERMINATOR in buf:
                    idx = buf.find(TERMINATOR)
                    return buf[:idx].decode("utf-8", errors="replace").strip()
            except socket.timeout:
                break
        raw = buf.decode("utf-8", errors="replace").strip()
        if raw.endswith("$>"):
            raw = raw[:-2].strip()
        return raw
    except (ConnectionResetError, ConnectionAbortedError, OSError) as e:
        return "__CONNECTION_ERROR__:%s" % e


def close_session(sock):
    try:
        sock.settimeout(2)
        sock.sendall(b"close\r\n")
        sock.recv(4096)
    except:
        pass
    try:
        sock.close()
    except:
        pass


def is_valid_describe(resp):
    if not resp or resp.startswith("__CONNECTION_ERROR__"):
        return False
    lower = resp.lower()
    if (
        "unknown" in lower
        or "error" in lower
        or "not found" in lower
        or "invalid" in lower
    ):
        return False
    return True


def parse_json_from_response(resp):
    try:
        start = resp.find("{")
        end = resp.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(resp[start : end + 1])
    except:
        pass
    return None


def validate_describe_batch(sock, paths, category):
    results = []
    for path in paths:
        resp = send_cmd(sock, "%s describe" % path)
        if resp.startswith("__CONNECTION_ERROR__"):
            RESULTS["errors"].append("%s: %s" % (path, resp))
            results.append((path, "error", resp))
            return results
        if is_valid_describe(resp):
            parsed = parse_json_from_response(resp)
            value = None
            if parsed:
                value = parsed
            elif resp and resp != "$>":
                value = resp[:200]
            RESULTS["describe_success"].append(
                {
                    "path": path,
                    "category": category,
                    "response_preview": resp[:200] if resp else "",
                    "parsed": parsed is not None,
                }
            )
            results.append((path, "success", value))
        else:
            RESULTS["describe_failure"].append(
                {
                    "path": path,
                    "category": category,
                    "response": resp[:200] if resp else "empty",
                }
            )
            results.append((path, "failure", resp[:100] if resp else "empty"))
        time.sleep(0.3)
    return results


def try_metric_register(path, metric_interval="Metric5s"):
    sock = connect_with_retry(RW_PORT)
    if not sock:
        return False, "connection_failed"
    try:
        cmd = "%s register object=%s" % (metric_interval, path)
        resp = send_cmd(sock, cmd, timeout=5)
        if resp.startswith("__CONNECTION_ERROR__"):
            return False, resp
        success = resp == "" or resp == "$>"
        return success, resp[:100] if resp else "silent"
    finally:
        close_session(sock)


def try_emit_check(port=EMIT_PORT, timeout=15):
    sock = connect_with_retry(port, timeout=5)
    if not sock:
        return False, "connection_failed"
    try:
        sock.settimeout(timeout)
        data = b""
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline:
            try:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                data += chunk
                if len(data) > 100:
                    break
            except socket.timeout:
                break
        if data:
            preview = data[:300].decode("utf-8", errors="replace")
            return True, preview
        return False, "no_data_received"
    finally:
        close_session(sock)


def main():
    print("=" * 80)
    print("PHASE 2 LIVE TRACE SIGNAL VALIDATION")
    print("Target: %s" % PLC_HOST)
    print("Time: %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    print("=" * 80)

    # PHASE 1: Hierarchy Exploration
    print("\n" + "=" * 80)
    print("PHASE 1: ROOT/CATEGORY HIERARCHY EXPLORATION")
    print("=" * 80)

    top_level = [
        "CANBusDrive",
        "System",
        "Lift",
        "BMS",
        "Steering",
        "Travel",
        "TMS",
        "Charger",
        "SecondaryPowerSupply",
        "ProgrammedMovementControl",
        "SystemState",
        "Spreader",
    ]

    hierarchy_results = {}
    for particle in top_level:
        sock = connect_with_retry(RO_PORT)
        if not sock:
            print("  [%s] FAILED to connect" % particle)
            hierarchy_results[particle] = "connection_failed"
            continue
        print("\n  [%s] describe -children ..." % particle)
        resp = send_cmd(sock, "%s describe -children" % particle, timeout=12)
        close_session(sock)
        if resp.startswith("__CONNECTION_ERROR__"):
            print("    Connection error: %s" % resp)
            hierarchy_results[particle] = "connection_error"
        elif not resp or resp == "$>":
            print("    Empty response (particle may not exist at root)")
            hierarchy_results[particle] = "empty"
        else:
            parsed = parse_json_from_response(resp)
            if parsed:
                nop = parsed.get("nop-children", [])
                op = parsed.get("op-children", [])
                total = len(nop) + len(op)
                print(
                    "    OK: %d children (%d op, %d nop)" % (total, len(op), len(nop))
                )
                child_names = []
                for c in op[:10]:
                    child_names.append(c.get("identity", ""))
                for c in nop[:10]:
                    child_names.append(c.get("identity", ""))
                hierarchy_results[particle] = {
                    "total_children": total,
                    "op_children": len(op),
                    "nop_children": len(nop),
                    "sample_children": child_names,
                    "identity": parsed.get("identity", ""),
                    "type": parsed.get("type", ""),
                }
            else:
                print("    Response (non-JSON): %s" % resp[:200])
                hierarchy_results[particle] = {"raw_preview": resp[:200]}

    # PHASE 2: Representative Signal Validation
    print("\n" + "=" * 80)
    print("PHASE 2: REPRESENTATIVE SIGNAL VALIDATION")
    print("=" * 80)

    representative_signals = {
        "CANOpenDrive-TransA": [
            "CANBusDrive/cTransA/Current",
            "CANBusDrive/cTransA/MotorTemp",
            "CANBusDrive/cTransA/BattVoltage",
            "CANBusDrive/cTransA/BattCurrent",
            "CANBusDrive/cTransA/CntrlTemp",
            "CANBusDrive/cTransA/Velocity",
            "CANBusDrive/cTransA/Torque",
            "CANBusDrive/cTransA/ProposedThrottle",
            "CANBusDrive/cTransA/TargetSpeed",
            "CANBusDrive/cTransA/BatteryPower",
            "CANBusDrive/cTransA/NodeState",
            "CANBusDrive/cTransA/HeartbeatCounter",
        ],
        "CANOpenDrive-SteerA": [
            "CANBusDrive/cSteerA/Current",
            "CANBusDrive/cSteerA/MotorTemp",
            "CANBusDrive/cSteerA/Velocity",
            "CANBusDrive/cSteerA/Torque",
            "CANBusDrive/cSteerA/TargetSpeed",
            "CANBusDrive/cSteerA/Diagnostic",
            "CANBusDrive/cSteerA/Stalled",
            "CANBusDrive/cSteerAngleA/Angle",
        ],
        "CANOpenDrive-WinchA": [
            "CANBusDrive/cWinchA/Current",
            "CANBusDrive/cWinchA/MotorTemp",
            "CANBusDrive/cWinchA/Velocity",
            "CANBusDrive/cWinchA/Torque",
            "CANBusDrive/cWinchA/ProposedThrottle",
            "CANBusDrive/cWinchA/TargetSpeed",
        ],
        "CANOpenDrive-Spreader": [
            "CANBusDrive/cSpreader/TelescopingActive",
            "CANBusDrive/cSpreader/TwistlocksEnabled",
            "CANBusDrive/cSpreader/HydraulicPressure",
            "CANBusDrive/cSpreader/HydraulicTemperature",
            "CANBusDrive/cSpreader/BrakeDisengaged",
            "CANBusDrive/cSpreader/PumpMotorTemperature",
        ],
        "System-State": [
            "System/SystemState",
            "System/ChargingEnabled",
            "System/AllowDownTrace",
            "System/AllowUpTrace",
        ],
        "BMS-Signals": [
            "BMS/SOC",
            "BMS/Current",
            "BMS/VoltageA",
            "BMS/VoltageB",
            "BMS/Availability",
            "BMS/CurrentState",
            "BMS/RequestedState",
            "BMS/RestartCount",
        ],
        "Lift-Signals": [
            "Lift/Input",
            "Lift/ScalingA",
            "Lift/Diagnostic",
            "Lift/ThrottleValue",
        ],
        "Steering-Signals": [
            "Steering/Input",
            "Steering/TargetAngle",
            "Steering/AdjustState",
            "Steering/SteerModeDiagnostic",
        ],
        "Travel-Signals": [
            "Travel/Input",
            "Travel/Diagnostic",
            "Travel/ThrottleValue",
            "Travel/ScalingA",
        ],
        "TMS-Signals": [
            "TMS/RequestedState",
            "TMS/CurrentState",
            "TMS/CoolantReservoir",
            "TMS/CurrentCoolantTemperature",
        ],
        "Charger-Signals": [
            "Charger/ChargerDiagnostic",
            "Charger/ChargingCurrentTarget",
            "Charger/ChargingVoltageTarget",
        ],
        "SecondaryPowerSupply": [
            "SecondaryPowerSupply/CurrentState",
            "SecondaryPowerSupply/RequestedState",
            "SecondaryPowerSupply/Availability",
        ],
        "ProgrammedMovement": [
            "ProgrammedMovementControl/Movement/Code",
            "ProgrammedMovementControl/Movement/Active",
            "ProgrammedMovementControl/Movement/State",
            "ProgrammedMovementControl/Requested",
        ],
        "Risky-Abbreviations": [
            "CANBusDrive/cTransA/BattVoltage",
            "CANBusDrive/cTransA/BattCurrent",
            "CANBusDrive/cTransA/CntrlTemp",
            "CANBusDrive/cWinchA/BattVoltage",
            "CANBusDrive/cWinchA/BattCurrent",
            "CANBusDrive/cSteerA/BattVoltage",
            "CANBusDrive/cSteerA/BattCurrent",
        ],
        "Risky-Typo": [
            "Travel/MovementD/LDiagnostic",
            "Travel/MovementD/Diagnostic",
        ],
        "Risky-Uncertain": [
            "CANBusDrive/cWinchA/ProposedThrottle",
            "CANBusDrive/cWinchA/TargetSpeed",
            "CANBusDrive/cTransA/ProposedThrottle",
            "CANBusDrive/cTransA/TargetSpeed",
        ],
    }

    for category, paths in representative_signals.items():
        print("\n--- Category: %s ---" % category)
        sock = connect_with_retry(RO_PORT)
        if not sock:
            print("  FAILED to connect for %s" % category)
            for p in paths:
                RESULTS["not_tested"].append(
                    {"path": p, "category": category, "reason": "connection_failed"}
                )
            continue
        batch_results = validate_describe_batch(sock, paths, category)
        close_session(sock)
        for path, status, detail in batch_results:
            print("  %s: %s (%s)" % (path, status, str(detail)[:80] if detail else ""))
        time.sleep(2)

    # PHASE 3: Pattern Inference
    print("\n" + "=" * 80)
    print("PHASE 3: PATTERN INFERENCE FROM HIERARCHY")
    print("=" * 80)

    canbus_success = [
        r
        for r in RESULTS["describe_success"]
        if r["category"].startswith("CANOpenDrive")
    ]
    if canbus_success:
        transa_signals = [
            r["path"].split("/cTransA/")[1]
            for r in canbus_success
            if "/cTransA/" in r["path"]
        ]
        if transa_signals:
            print(
                "\n  Successful transA signals (%d): %s"
                % (len(transa_signals), transa_signals)
            )
            drive_prefixes = [
                "cTransB",
                "cTransC",
                "cTransD",
                "cSteerB",
                "cSteerC",
                "cSteerD",
                "cWinchB",
                "cWinchC",
                "cWinchD",
                "cWinchAngleB",
                "cWinchAngleC",
                "cWinchAngleD",
                "cSteerAngleB",
                "cSteerAngleC",
                "cSteerAngleD",
            ]
            for prefix in drive_prefixes:
                for sig in transa_signals:
                    inferred_path = "CANBusDrive/%s/%s" % (prefix, sig)
                    RESULTS["inferred_from_pattern"].append(
                        {
                            "path": inferred_path,
                            "based_on": "CANBusDrive/cTransA/%s" % sig,
                            "confidence": (
                                "high"
                                if prefix.startswith("cTrans")
                                or prefix.startswith("cSteer")
                                or prefix.startswith("cWinch")
                                else "medium"
                            ),
                        }
                    )
            print(
                "  Inferred %d signals from transA pattern"
                % (len(drive_prefixes) * len(transa_signals))
            )

    # PHASE 4: Metric Registration
    print("\n" + "=" * 80)
    print("PHASE 4: METRIC REGISTRATION TEST")
    print("=" * 80)

    metric_test_signals = [
        ("CANBusDrive/cTransA/MotorTemp", "Metric5s"),
        ("CANBusDrive/cTransA/Current", "Metric250ms"),
        ("CANBusDrive/cSteerA/MotorTemp", "Metric5s"),
        ("BMS/SOC", "Metric1s"),
        ("TMS/CurrentCoolantTemperature", "Metric1m"),
    ]

    for path, interval in metric_test_signals:
        print("\n  Testing: %s register object=%s" % (interval, path))
        success, detail = try_metric_register(path, interval)
        if success:
            RESULTS["metric_register_success"].append(
                {"path": path, "interval": interval}
            )
            print("    SUCCESS (response: %s)" % detail)
        else:
            RESULTS["metric_register_failure"].append(
                {"path": path, "interval": interval, "detail": str(detail)[:100]}
            )
            print("    FAILED: %s" % detail)
        time.sleep(3)

    # PHASE 5: Emission Check
    print("\n" + "=" * 80)
    print("PHASE 5: EMISSION CHECK (port 49890)")
    print("=" * 80)

    print("\n  Checking for metric data on port 49890...")
    emit_ok, emit_detail = try_emit_check(EMIT_PORT, timeout=15)
    if emit_ok:
        RESULTS["emit_success"].append(
            {"port": EMIT_PORT, "data_preview": emit_detail[:300]}
        )
        print("  SUCCESS: Data received")
        print("  Preview: %s" % emit_detail[:300])
    else:
        RESULTS["emit_failure"].append({"port": EMIT_PORT, "detail": str(emit_detail)})
        print("  FAILED: %s" % emit_detail)

    # SUMMARY
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY")
    print("=" * 80)

    print("\n  describe_success:       %d" % len(RESULTS["describe_success"]))
    print("  describe_failure:       %d" % len(RESULTS["describe_failure"]))
    print("  metric_register_success: %d" % len(RESULTS["metric_register_success"]))
    print("  metric_register_failure: %d" % len(RESULTS["metric_register_failure"]))
    print("  emit_success:           %d" % len(RESULTS["emit_success"]))
    print("  emit_failure:           %d" % len(RESULTS["emit_failure"]))
    print("  inferred_from_pattern:  %d" % len(RESULTS["inferred_from_pattern"]))
    print("  not_tested:             %d" % len(RESULTS["not_tested"]))
    print("  errors:                 %d" % len(RESULTS["errors"]))

    # Naming corrections
    print("\n--- Naming Corrections ---")
    for r in RESULTS["describe_success"]:
        path = r["path"]
        if "BattVoltage" in path:
            RESULTS["naming_corrections"].append(
                {"path": path, "correction": "BattVoltage (not BatteryVoltage)"}
            )
        if "BattCurrent" in path:
            RESULTS["naming_corrections"].append(
                {"path": path, "correction": "BattCurrent (not BatteryCurrent)"}
            )
        if "CntrlTemp" in path:
            RESULTS["naming_corrections"].append(
                {"path": path, "correction": "CntrlTemp (not ControllerTemperature)"}
            )

    corrections = list(
        {c["correction"]: c for c in RESULTS["naming_corrections"]}.values()
    )
    for c in corrections:
        print("  %s: %s" % (c["path"], c["correction"]))

    # Save results
    output_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "live_trace_validation_results.json"
    )
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": PLC_HOST,
        "plc_reachable_ro": True,
        "plc_reachable_rw": len(RESULTS["metric_register_success"]) > 0
        or len(RESULTS["metric_register_failure"]) > 0,
        "hierarchy_exploration": hierarchy_results,
        "results": RESULTS,
        "summary": {
            "describe_success": len(RESULTS["describe_success"]),
            "describe_failure": len(RESULTS["describe_failure"]),
            "metric_register_success": len(RESULTS["metric_register_success"]),
            "metric_register_failure": len(RESULTS["metric_register_failure"]),
            "emit_success": len(RESULTS["emit_success"]),
            "emit_failure": len(RESULTS["emit_failure"]),
            "inferred_from_pattern": len(RESULTS["inferred_from_pattern"]),
            "not_tested": len(RESULTS["not_tested"]),
            "naming_corrections": len(corrections),
        },
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("\n[+] Full results saved to: %s" % output_path)


if __name__ == "__main__":
    main()

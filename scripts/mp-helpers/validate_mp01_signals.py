#!/usr/bin/env python3
import json
import socket
import sys
import time

PLC_HOST = "10.2.3.4"
PLC_PORT = 49870
TIMEOUT = 5.0
TERMINATOR = b"|$>"

SIGNALS = [
    ("hoist_sync_error_W1W2", ["Lift/iLiftABSync", "Lift/iLiftABSync/Value"]),
    ("hoist_sync_error_W3W4", ["Lift/iLiftCDSync", "Lift/iLiftCDSync/Value"]),
    ("hoist_position_W1", ["CANBusDrive/cWinchA/Position", "Lift/iLiftAPos/Value"]),
    ("hoist_position_W2", ["CANBusDrive/cWinchB/Position", "Lift/iLiftBPos/Value"]),
    ("hoist_position_W3", ["CANBusDrive/cWinchC/Position", "Lift/iLiftCPos/Value"]),
    ("hoist_position_W4", ["CANBusDrive/cWinchD/Position", "Lift/iLiftDPos/Value"]),
    ("hoist_dc_current_W1", ["CANBusDrive/cWinchA/Current"]),
    ("hoist_dc_current_W2", ["CANBusDrive/cWinchB/Current"]),
    ("hoist_dc_current_W3", ["CANBusDrive/cWinchC/Current"]),
    ("hoist_dc_current_W4", ["CANBusDrive/cWinchD/Current"]),
    ("hoist_dc_voltage_W1", ["CANBusDrive/cWinchA/BattVoltage"]),
    ("hoist_torque_W1", ["CANBusDrive/cWinchA/Torque"]),
    (
        "hoist_state",
        [
            "Lift/State",
            "Lift/Status",
            "Lift/Mode",
            "Lift/OperatingState",
            "Lift/RunState",
            "System/LiftState",
        ],
    ),
    (
        "hoist_load_kg",
        [
            "Lift/Load",
            "Lift/LoadKg",
            "Lift/ContainerMass",
            "Lift/Weight",
            "Spreader/Load",
            "Spreader/LoadKg",
            "System/Load",
        ],
    ),
    (
        "tilt_sensor_deg",
        [
            "System/TiltAngle",
            "System/Tilt",
            "System/TiltDeg",
            "System/Inclinometer",
            "Lift/TiltAngle",
            "Spreader/TiltAngle",
        ],
    ),
    ("hoist_temp_motor_W1", ["CANBusDrive/cWinchA/MotorTemp"]),
    ("hoist_temp_motor_W2", ["CANBusDrive/cWinchB/MotorTemp"]),
    ("hoist_temp_motor_W3", ["CANBusDrive/cWinchC/MotorTemp"]),
    ("hoist_temp_motor_W4", ["CANBusDrive/cWinchD/MotorTemp"]),
    (
        "hoist_fault_code",
        [
            "Lift/FaultCode",
            "Lift/Fault",
            "Lift/ErrorCode",
            "System/HoistFault",
            "System/FaultCode",
            "BMSAB/FaultCode",
            "BMS/FaultCode",
        ],
    ),
    ("bat_pack_current_signed", ["BMSAB/PackCurrent", "BMS/PackCurrent"]),
    ("bat_pack_voltage", ["BMSAB/PackVoltage", "BMS/PackVoltage"]),
    (
        "cycle_count",
        [
            "Lift/CycleCount",
            "Lift/Cycles",
            "System/CycleCount",
            "System/HoistCycles",
            "Lift/HoistCycleCount",
        ],
    ),
]


def recv_until(sock, terminator, timeout):
    sock.settimeout(timeout)
    buf = bytearray()
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            chunk = sock.recv(4096)
        except socket.timeout:
            break
        if not chunk:
            break
        buf.extend(chunk)
        idx = buf.find(terminator)
        if idx != -1:
            return buf[:idx].decode("utf-8", errors="replace").strip()
    raw = buf.decode("utf-8", errors="replace").strip()
    if raw.endswith("$>"):
        raw = raw[:-2].strip()
    return raw


def send_cmd(sock, cmd, timeout=TIMEOUT):
    sock.sendall((cmd + "\r\n").encode("ascii"))
    return recv_until(sock, TERMINATOR, timeout)


def try_describe(sock, path):
    try:
        resp = send_cmd(sock, "{} describe".format(path), timeout=TIMEOUT)
        if not resp or resp == "$>":
            return False, "(empty response)", None
        lower = resp.lower()
        if (
            "unknown" in lower
            or "error" in lower
            or "not found" in lower
            or "invalid" in lower
        ):
            return False, resp, None
        parsed = None
        try:
            start = resp.find("{")
            end = resp.rfind("}")
            if start == -1:
                start = resp.find("[")
                end = resp.rfind("]")
            if start != -1 and end != -1 and end > start:
                parsed = json.loads(resp[start : end + 1])
        except Exception:
            pass
        return True, resp, parsed
    except socket.timeout:
        return False, "(timeout)", None
    except Exception as e:
        return False, "(exception: {})".format(e), None


def try_children(sock, path):
    try:
        resp = send_cmd(sock, "{} describe -children".format(path), timeout=TIMEOUT)
        return resp
    except:
        return "(error)"


def main():
    print("=" * 80)
    print("MP-01 SIGNAL LIVE VALIDATION")
    print("Target: {}:{}".format(PLC_HOST, PLC_PORT))
    print("Time: {}".format(time.strftime("%Y-%m-%d %H:%M:%S")))
    print("=" * 80)

    print("\n[*] Connecting to PLC...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(TIMEOUT)
        sock.connect((PLC_HOST, PLC_PORT))
    except Exception as e:
        print("[ERROR] Connection failed: {}".format(e))
        sys.exit(1)

    greeting = recv_until(sock, TERMINATOR, TIMEOUT)
    print(
        "[+] Connected. Greeting: {}".format(greeting[:200] if greeting else "(empty)")
    )

    results = []

    for sig_name, paths in SIGNALS:
        print("\n" + "-" * 60)
        print("Testing: {}".format(sig_name))
        print("  Candidates: {}".format(paths))

        found = False
        best_path = None
        best_resp = None
        best_parsed = None

        for path in paths:
            print("  Trying: {}".format(path), end=" ... ")
            success, resp, parsed = try_describe(sock, path)
            if success:
                print("OK")
                found = True
                best_path = path
                best_resp = resp
                best_parsed = parsed
                snippet = resp[:150] if len(resp) > 150 else resp
                print("    Response: {}".format(snippet))
                if parsed:
                    print("    Parsed: {}".format(json.dumps(parsed, indent=2)[:200]))
            else:
                print("FAIL ({})".format(resp[:80] if resp else "no response"))

        if found:
            status = "present"
        else:
            status = "no present"

        results.append(
            {
                "signal": sig_name,
                "candidates": paths,
                "found": found,
                "best_path": best_path,
                "best_resp": best_resp,
                "best_parsed": best_parsed,
                "status": status,
            }
        )

    # Explore parent nodes
    print("\n" + "=" * 60)
    print("EXPLORING PARENT NODES FOR ADDITIONAL SIGNALS")
    print("=" * 60)

    explore_paths = ["Lift", "CANBusDrive", "BMSAB", "BMS", "Spreader", "System"]
    discovered = {}
    for ep in explore_paths:
        print("\n[*] Enumerating children of: {}".format(ep))
        resp = try_children(sock, ep)
        print("  Response: {}".format(resp[:300] if resp else "(empty)"))
        discovered[ep] = resp

    # Close
    print("\n[*] Closing session...")
    try:
        send_cmd(sock, "close", timeout=2.0)
    except:
        pass
    sock.close()

    # Summary table
    print("\n" + "=" * 80)
    print("VALIDATION SUMMARY TABLE")
    print("=" * 80)
    hdr = "{:<25} | {:<45} | {:<10} | {}".format(
        "Signal Name", "Candidate Path Tested", "Live Result", "Recommended Note"
    )
    print(hdr)
    print("-" * 80)

    for r in results:
        path = r["best_path"] if r["best_path"] else ", ".join(r["candidates"])
        if r["found"]:
            if r["best_parsed"]:
                val_summary = json.dumps(r["best_parsed"])[:60]
            elif r["best_resp"]:
                val_summary = r["best_resp"][:60]
            else:
                val_summary = "OK"
            note = "present"
        else:
            val_summary = "not found / no response"
            note = "no present"

        row = "{:<25} | {:<45} | {:<10} | {}".format(
            r["signal"], path, val_summary, note
        )
        print(row)

    print("-" * 80)
    present_count = sum(1 for r in results if r["found"])
    absent_count = sum(1 for r in results if not r["found"])
    print(
        "\nTotal: {} signals tested | {} present | {} no present".format(
            len(results), present_count, absent_count
        )
    )

    # Save results
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "target": "{}:{}".format(PLC_HOST, PLC_PORT),
        "results": results,
        "discovered_children": discovered,
    }

    out_path = (
        "C:\\\\local\\\\opencode\\\\codesys\\\\scripts\\\\mp01_validation_results.json"
    )
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    print("\n[+] Full results saved to: {}".format(out_path))


if __name__ == "__main__":
    main()

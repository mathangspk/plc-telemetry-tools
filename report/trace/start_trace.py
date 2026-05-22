#!/usr/bin/env python
"""start_trace.py — Register all signals from a trace JSON config onto the PLC.

Connects to the PLC's RW port (default 49870) and registers each signal
from the trace config using the metric register command.

Usage:
    python scripts/telemetry/start_trace.py CanBusDrive
    python scripts/telemetry/start_trace.py CanBusDrive --dry-run
    python scripts/telemetry/start_trace.py TraceSteer -H 10.2.3.99
"""

import argparse
import json
import os
import signal
import socket
import sys
import time


# Global flag for graceful interrupt handling
_interrupted = False


def _signal_handler(signum, frame):
    global _interrupted
    _interrupted = True
    print("\n[{}] received — stopping after current command.".format(
        "SIGINT" if signum == signal.SIGINT else "SIGTERM"
    ))


def graceful_close(sock):
    """Two-phase cleanup: send 'close' command, then shutdown + close socket."""
    try:
        sock.sendall(b"close\r\n")
        time.sleep(0.1)
    except Exception:
        pass  # Best-effort; PLC may have already closed
    try:
        sock.shutdown(socket.SHUT_WR)
    except Exception:
        pass
    try:
        sock.close()
    except Exception:
        pass


def wait_for_prompt(sock, timeout=5):
    """Read from socket until '$>' prompt is seen or timeout."""
    buf = b""
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            sock.settimeout(min(0.5, deadline - time.time()))
            chunk = sock.recv(4096)
            if not chunk:
                break
            buf += chunk
            if b"$>" in buf:
                return True
        except socket.timeout:
            continue
    return b"$>" in buf


def normalize_path(path):
    """Normalize any PLC path to a standard format (e.g. CANBusDrive/cTransA/Velocity)."""
    if path.startswith("PrimaryPLC."):
        path = path[len("PrimaryPLC."):]
    if path.startswith("System."):
        path = path[len("System."):]
    if path.startswith("System/"):
        path = path[len("System/"):]
    # Replace dots with slashes to ensure consistent formatting
    path = path.replace(".", "/")
    if path.startswith("system/") or path.startswith("System/"):
        path = path[7:]
    return path


def _extract_json_objects(text):
    """Extract JSON objects from a text string using brace matching."""
    objects = []
    text = text.replace('\x00', '').strip()
    if not text:
        return objects

    try:
        parsed = json.loads(text)
        objects.append(parsed)
        return objects
    except (json.JSONDecodeError, ValueError):
        pass

    depth = 0
    start = None
    for i, ch in enumerate(text):
        if ch == '{':
            if depth == 0:
                start = i
            depth += 1
        elif ch == '}':
            depth -= 1
            if depth == 0 and start is not None:
                candidate = text[start:i + 1]
                try:
                    parsed = json.loads(candidate)
                    objects.append(parsed)
                except (json.JSONDecodeError, ValueError):
                    pass
                start = None

    return objects


def verify_active_emission(host, expected_signals, listen_duration=3.0):
    """Checks if the registered signals are actively emitting data on port 49890."""
    print(">>> [VERIFY EMISSION] Verifying active telemetry emission on Emit port 49890...")
    emitted_paths = set()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(2.0)
    
    # Store expected paths for easy lookup
    expected_normalized = {normalize_path(sig["path"]): sig["name"] for sig in expected_signals}
    
    try:
        sock.connect((host, 49890))
        # Consume greeting socket immediately
        try:
            sock.recv(1024)
        except socket.timeout:
            pass
        
        all_data = bytearray()
        start_time = time.time()
        sock.settimeout(1.0)
        while time.time() - start_time < listen_duration:
            try:
                data = sock.recv(4096)
                if not data:
                    break
                all_data.extend(data)
            except socket.timeout:
                continue
            except Exception as e:
                print("  [ERROR] Recv error during emission check: {}".format(e))
                break
        sock.close()
        
        # Parse identities
        all_text = all_data.decode("utf-8", errors="replace")
        json_objects = _extract_json_objects(all_text)
        for data in json_objects:
            if isinstance(data, dict):
                members = data.get("members", [])
                if isinstance(members, list):
                    for m in members:
                        identity = m.get("identity", "")
                        if identity:
                            emitted_paths.add(normalize_path(identity))
    except Exception as e:
        print("  [ERROR] Connection to Emit port failed: {}".format(e))
        return False

    # Check which expected signals are actually emitting
    active_count = 0
    print("\nEmission Status:")
    for path, name in expected_normalized.items():
        if path in emitted_paths:
            print("  [ACTIVE]   {} ({})".format(name, path))
            active_count += 1
        else:
            print("  [SILENT]   {} ({})".format(name, path))
            
    print()
    if active_count == len(expected_signals):
        print(">>> [SUCCESS] All {} expected signals are actively emitting data!".format(active_count))
        return True
    elif active_count > 0:
        print(">>> [WARN] Partially active. Only {} of {} signals are emitting data.".format(active_count, len(expected_signals)))
        return False
    else:
        print(">>> [ERROR] No registered signals are emitting. Stream is silent.")
        return False


def main():
    global _interrupted

    parser = argparse.ArgumentParser(
        description="Register all signals from a trace JSON config onto the PLC."
    )
    parser.add_argument(
        "name",
        help="Trace name (e.g., CanBusDrive, TraceSteer)",
    )
    parser.add_argument(
        "--trace-dir",
        default="exports/trace-config/traces/",
        help="Directory containing trace JSON files",
    )
    parser.add_argument(
        "-H", "--host",
        default="10.2.3.4",
        help="PLC IP address (default: 10.2.3.4)",
    )
    parser.add_argument(
        "-P", "--port",
        type=int,
        default=49870,
        help="PLC RW port (default: 49870)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print what would be registered without connecting",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Per-command timeout in seconds (default: 5)",
    )

    args = parser.parse_args()

    # Load trace config
    trace_dir = args.trace_dir
    trace_file = os.path.join(trace_dir, "{}.json".format(args.name))
    
    # Smart fallback resolution
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    
    if not os.path.isfile(trace_file):
        # Fallback 1: Try relative to script's directory
        trace_file = os.path.join(script_dir, trace_dir, "{}.json".format(args.name))
        
    if not os.path.isfile(trace_file):
        # Fallback 2: If user passed report/trace/pass_active but is already inside report/trace
        normalized_dir = trace_dir.replace("report/trace/", "").replace("report\\trace\\", "")
        trace_file = os.path.join(script_dir, normalized_dir, "{}.json".format(args.name))
        
    if not os.path.isfile(trace_file):
        # Fallback 3: Just check if the last directory name exists inside the script folder
        basename_dir = os.path.basename(trace_dir.rstrip("/\\"))
        trace_file = os.path.join(script_dir, basename_dir, "{}.json".format(args.name))
        
    if not os.path.isfile(trace_file):
        # Fallback 4: Try relative to project root
        trace_file = os.path.join(project_root, trace_dir, "{}.json".format(args.name))

    if not os.path.isfile(trace_file):
        print("[ERROR] Trace config not found. Tried resolving paths: ")
        print("  - {}".format(os.path.join(os.getcwd(), trace_dir, "{}.json".format(args.name))))
        print("  - {}".format(os.path.join(script_dir, trace_dir, "{}.json".format(args.name))))
        sys.exit(1)

    with open(trace_file, "r") as f:
        config = json.load(f)

    trace_name = config.get("name", args.name)
    default_metric = "Metric250ms"
    signals = config.get("signals", [])
 
    # Print summary
    print("=" * 60)
    print("Trace: {}".format(trace_name))
    print("Signals: {}".format(len(signals)))
    print("=" * 60)
    print()
 
    if args.dry_run:
        print("[DRY RUN] Would register the following signals:")
        for i, sig in enumerate(signals, 1):
            sig_metric = sig.get("metric", default_metric)
            cmd = "{} register object={}".format(sig_metric, sig["path"])
            print("  {:>3}. [{}] {}  ->  {}".format(i, sig["name"], cmd, sig["path"]))
        print()
        print("[DRY RUN] Total: {} signals".format(len(signals)))
        return

    # Set up signal handlers
    if hasattr(signal, "SIGINT"):
        signal.signal(signal.SIGINT, _signal_handler)
    if hasattr(signal, "SIGTERM"):
        try:
            signal.signal(signal.SIGTERM, _signal_handler)
        except (ValueError, OSError):
            pass  # SIGTERM not supported on all platforms

    # Connect to PLC
    print("Connecting to {}:{} ...".format(args.host, args.port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(args.timeout)

    try:
        sock.connect((args.host, args.port))
    except socket.timeout:
        print("[ERROR] Connection timed out — PLC unreachable or wrong IP.")
        sys.exit(1)
    except socket.error as e:
        print("[ERROR] Connection failed: {}".format(e))
        sys.exit(1)

    print("Connected. Consuming greeting...")

    # Consume greeting
    if not wait_for_prompt(sock, timeout=args.timeout):
        print("[WARN] Did not receive prompt after connection (may still work).")

    print()

    # Register each signal
    registered = 0
    failed = 0

    for i, sig in enumerate(signals, 1):
        if _interrupted:
            print("\n[INTERRUPTED] Stopping at signal {}/{}.".format(i, len(signals)))
            break

        path = sig["path"]
        sig_metric = sig.get("metric", default_metric)
        cmd = "{} register object={}\r\n".format(sig_metric, path)

        try:
            sock.sendall(cmd.encode("ascii"))
            if wait_for_prompt(sock, timeout=args.timeout):
                print("  [{:>3}/{}] [OK]   {}".format(i, len(signals), sig["name"]))
                registered += 1
            else:
                print("  [{:>3}/{}] [FAIL] {} (timeout)".format(i, len(signals), sig["name"]))
                failed += 1
        except socket.timeout:
            print("  [{:>3}/{}] [FAIL] {} (timeout)".format(i, len(signals), sig["name"]))
            failed += 1
        except socket.error as e:
            print("  [{:>3}/{}] [FAIL] {} ({})".format(i, len(signals), sig["name"], e))
            failed += 1
            break

    # Summary
    print()
    print("=" * 60)
    print("Summary: {} registered, {} failed, {} total".format(
        registered, failed, len(signals)
    ))
    print("=" * 60)

    # Graceful cleanup
    print("\nClosing session...")
    graceful_close(sock)
    print("Session closed.")

    # Verify active emission on port 49890
    print()
    verify_active_emission(args.host, signals)


if __name__ == "__main__":
    main()

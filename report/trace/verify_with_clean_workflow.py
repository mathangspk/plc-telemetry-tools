#!/usr/bin/env python3
"""verify_with_clean_workflow.py — High-precision sequential trace verification with pre/post clear checks.

Workflow:
  1. Pre-Check: Verify if any metric is currently pushing data (Emit port 49890) or has members (Describe port 49880).
     If yes, execute 'clear' via RW port 49870 and re-verify silence.
  2. REGISTER: Register all signals from the trace JSON config.
  3. DESCRIBE: Verify registered membership using 'describe' query.
  4. EMIT: Listen to push stream to confirm active data emission.
  5. STOP/CLEAR: Run 'clear' command to stop telemetry stream.
  6. Post-Check: Re-verify that emission is silent and members are cleared. Clear again if necessary.
  7. Report: Generate independent markdown report and console output for this single trace.
"""

import argparse
import datetime
import json
import os
import socket
import sys
import time

# Force UTF-8 for Windows console
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
DEFAULT_HOST = "10.2.3.4"
PORT_RW = 49870
PORT_RO_DESCRIBE = 49870
PORT_RO_EMIT = 49890
TERMINATOR = b"|$>"
PROMPT = b"$>"
CONNECT_TIMEOUT = 5.0
CMD_TIMEOUT = 5.0
CLOSE_TIMEOUT = 2.0
EMIT_LISTEN_DURATION = 5.0  # 5 seconds is enough to capture a 250ms stream

# Paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(os.path.dirname(SCRIPT_DIR))
TRACE_DIR = os.path.join(PROJECT_ROOT, "exports", "trace-config", "traces")
RESULTS_DIR = os.path.join(SCRIPT_DIR, "test_results")

# ---------------------------------------------------------------------------
# Socket & Protocol Helpers
# ---------------------------------------------------------------------------
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


def recv_until_terminator(sock, timeout):
    """Read from sock until TERMINATOR (|$>) or standard ($>) is found or timeout elapses."""
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
        # Look for either the pipe terminator or the simple prompt
        idx = buf.find(TERMINATOR)
        if idx == -1:
            idx = buf.find(b"$>")
        if idx != -1:
            decoded = buf[:idx].decode("utf-8", errors="replace").replace('\x00', '').strip()
            return bytes(buf), decoded
    # Fallback
    raw = bytes(buf)
    decoded = raw.decode("utf-8", errors="replace").replace('\x00', '').strip()
    if decoded.endswith("$>"):
        decoded = decoded[:-2].strip()
    return raw, decoded


def wait_for_greeting(sock, timeout=5.0):
    """Consume greeting prompt after connecting."""
    return recv_until_terminator(sock, timeout)


def send_command(sock, cmd, timeout=CMD_TIMEOUT):
    """Send a command and return (raw_bytes, decoded_response)."""
    sock.sendall((cmd + "\r\n").encode("ascii"))
    return recv_until_terminator(sock, timeout)


def graceful_close(sock):
    """Send 'close' command, then shutdown + close socket."""
    try:
        sock.settimeout(CLOSE_TIMEOUT)
        sock.sendall(b"close\r\n")
        recv_until_terminator(sock, CLOSE_TIMEOUT)
    except Exception:
        pass
    try:
        sock.shutdown(socket.SHUT_WR)
    except OSError:
        pass
    try:
        sock.close()
    except OSError:
        pass


def connect_socket(host, port, label):
    """Connect a TCP socket."""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.settimeout(CONNECT_TIMEOUT)
        sock.connect((host, port))
        return sock
    except Exception as e:
        print(f"  [ERROR] Connection to {host}:{port} ({label}) failed: {e}")
        sock.close()
        return None


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
def _extract_identities_from_obj(obj, paths_set):
    """Recursively extract identity/path strings from a JSON object's members list."""
    if isinstance(obj, dict):
        members = obj.get("members", [])
        if isinstance(members, list):
            for m in members:
                if isinstance(m, dict):
                    identity = m.get("identity", "")
                    if identity:
                        paths_set.add(normalize_path(identity))

KNOWN_METRICS = ["Metric100ms", "Metric250ms", "Metric500ms", "Metric1s", "Metric5s", "Metric10s"]


# ---------------------------------------------------------------------------
# Checking and Cleaning Core Logic
# ---------------------------------------------------------------------------
def check_active_emission(host):
    """Checks if there is active telemetry emission on port 49890.
    
    Listens for 1.5 seconds. Returns a set of active metric names.
    """
    print(f"  Checking RO Emit port {PORT_RO_EMIT} for active data stream...")
    active_metrics = set()
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(1.5)
    try:
        sock.connect((host, PORT_RO_EMIT))
        # The RO Emit port immediately sends a socket greeting on connect. Consume it first.
        try:
            greeting = sock.recv(1024)
        except socket.timeout:
            pass
        
        # Now listen to see if any actual telemetry data frames follow
        sock.settimeout(1.5)
        data = sock.recv(4096)
        sock.close()
        if data:
            text = data.decode("utf-8", errors="replace")
            print(f"    [WARN] Active emission detected! Received {len(data)} additional bytes.")
            # Parse metric names from JSON frames
            json_objects = _extract_json_objects(text)
            for obj in json_objects:
                if isinstance(obj, dict):
                    identity = obj.get("identity", "")
                    if identity and "Metric" in identity:
                        # Extract e.g. "Metric5s" from "PrimaryPLC.System.Metric5s"
                        metric_name = identity.split(".")[-1]
                        active_metrics.add(metric_name)
    except socket.timeout:
        # A timeout here means absolutely no active telemetry stream is running (silent)
        pass
    except Exception as e:
        print(f"    [ERROR] Check emit failed: {e}")
    finally:
        try:
            sock.close()
        except OSError:
            pass
            
    if active_metrics:
        print(f"    [WARN] Active metrics found emitting data: {list(active_metrics)}")
    else:
        print("    [OK] No active data stream detected on Emit port (silent).")
    return active_metrics


def check_registered_members(host, target_metrics):
    """Checks specified metrics on describe port 49880 to find active members.
    
    Returns a set of active metric names that have registered members.
    """
    if isinstance(target_metrics, str):
        target_metrics = [target_metrics]
        
    print(f"  Checking RO Describe port {PORT_RO_DESCRIBE} for registered members...")
    active_metrics_with_members = set()
    
    for metric in target_metrics:
        sock = connect_socket(host, PORT_RO_DESCRIBE, f"Describe Check {metric}")
        if sock:
            wait_for_greeting(sock)
            try:
                raw_resp, resp_text = send_command(sock, f"{metric} describe", timeout=2.0)
                raw_str = raw_resp.decode("utf-8", errors="replace")
                json_objects = _extract_json_objects(raw_str)
                confirmed_paths = set()
                for obj in json_objects:
                    _extract_identities_from_obj(obj, confirmed_paths)
                if confirmed_paths:
                    print(f"    [WARN] Metric '{metric}' has {len(confirmed_paths)} active members.")
                    active_metrics_with_members.add(metric)
            except Exception:
                pass
            graceful_close(sock)
            
    if active_metrics_with_members:
        print(f"    [WARN] Metrics with active members in describe: {list(active_metrics_with_members)}")
    else:
        print("    [OK] No members registered in describe for checked metrics.")
    return active_metrics_with_members


def execute_metric_clear(host, metric="Metric250ms"):
    """Connects to RW port 49870 and executes clear on the metric."""
    print(f"  Executing '{metric} clear' command on RW port {PORT_RW}...")
    sock = connect_socket(host, PORT_RW, "Clear Request")
    if sock:
        wait_for_greeting(sock)
        try:
            raw_resp, text = send_command(sock, f"{metric} clear", timeout=3.0)
            print(f"    [OK] Clear response: {text}")
        except Exception as e:
            print(f"    [ERROR] Clear command failed: {e}")
        graceful_close(sock)
        # Small delay for PLC to apply state changes
        time.sleep(1.0)
    else:
        print("    [FATAL] Unable to connect to RW port to issue clear!")


def enforce_silence_workflow(host, target_metrics):
    """Ensures that the telemetry metrics are fully cleared and silent.
    
    Performs check, executes clear if needed, and re-checks.
    """
    if isinstance(target_metrics, str):
        target_metrics = [target_metrics]
    target_metrics = list(target_metrics)
        
    print(f"\n>>> [ENFORCE SILENCE] Verifying PLC state for metrics {target_metrics}...")
    
    # 1. Check emit and describe
    active_emitting = check_active_emission(host)
    active_described = check_registered_members(host, target_metrics)
    
    # Union of all active metrics
    all_active_metrics = active_emitting.union(active_described)
    
    if all_active_metrics:
        print(f">>> [ALERT] Active metrics detected: {list(all_active_metrics)}! Triggering reset clear...")
        for m in all_active_metrics:
            execute_metric_clear(host, m)
        # Always clear the target metrics too just to be safe
        for m in target_metrics:
            if m not in all_active_metrics:
                execute_metric_clear(host, m)
            
        # 2. Re-verify
        print("\nRe-verifying silence post-clear...")
        active_emitting_post = check_active_emission(host)
        active_described_post = check_registered_members(host, target_metrics)
        
        still_active = active_emitting_post.union(active_described_post)
        if still_active:
            print(f">>> [WARN] PLC remains active on metrics {list(still_active)} after clear command!")
            print(">>> [RETRY] Attempting one more clear command on still-active metrics...")
            for m in still_active:
                execute_metric_clear(host, m)
            
            # Final re-verify
            active_emitting_final = check_active_emission(host)
            active_described_final = check_registered_members(host, target_metrics)
            final_active = active_emitting_final.union(active_described_final)
            if final_active:
                print(f">>> [FATAL] PLC state could not be set to silent on metrics {list(final_active)}! Check PLC health.")
                return False
        
        print(">>> [SUCCESS] PLC telemetry successfully reset to silent state.")
    else:
        print(">>> [OK] PLC is already in a clean, silent state.")
    return True


# ---------------------------------------------------------------------------
# Core Workflow Test
# ---------------------------------------------------------------------------
def run_focused_test(host, trace_file, listen_duration=EMIT_LISTEN_DURATION):
    """Executes the workflow: verify silent -> register -> describe -> emit -> stop -> verify silent."""
    trace_name = os.path.splitext(os.path.basename(trace_file))[0]
    
    with open(trace_file, "r", encoding="utf-8") as f:
        trace_config = json.load(f)
        
    default_metric = "Metric250ms"
    signals = trace_config.get("signals", [])
    # Gather all unique metrics referenced in this trace
    metrics_in_trace = sorted(list(set(sig.get("metric", default_metric) for sig in signals)))
    if not metrics_in_trace:
        metrics_in_trace = [default_metric]
    
    print("\n" + "=" * 80)
    print(f"  SEQUENTIAL TEST: REGISTER -> DESCRIBE -> EMIT -> STOP")
    print(f"  Target Trace: {trace_name} ({len(signals)} expected signals)")
    print(f"  Target Metrics: {', '.join(metrics_in_trace)} | Listen Duration: {listen_duration}s")
    print("=" * 80)
    
    # 1. Pre-Check & Clear
    if not enforce_silence_workflow(host, metrics_in_trace):
        print("[ABORT] PLC state could not be set to silent. Aborting test.")
        return None
        
    # Store expected paths
    expected_signals = []
    for sig in signals:
        expected_signals.append({
            "name": sig["name"],
            "original_path": sig["path"],
            "normalized_path": normalize_path(sig["path"])
        })
        
    # 2. Step 1: REGISTER
    print(f"\nSTEP 1: Registering {len(signals)} signals on RW port {PORT_RW}...")
    registered_paths = set()
    rw_sock = connect_socket(host, PORT_RW, "Register")
    if rw_sock:
        wait_for_greeting(rw_sock)
        for i, sig in enumerate(signals, 1):
            path = sig["path"]
            # Preserve full path (including System/ prefix if present) to ensure direct leaves register correctly
            reg_path = path
            sig_metric = sig.get("metric", default_metric)
            cmd = f"{sig_metric} register object={reg_path}"
            try:
                send_command(rw_sock, cmd, timeout=CMD_TIMEOUT)
                registered_paths.add(normalize_path(path))
            except Exception as e:
                print(f"    [FAIL] Register {sig['name']}: {e}")
        graceful_close(rw_sock)
        print("  Registration phase complete.")
    else:
        print("  [FATAL] Unable to connect for registration.")
        return None
        
    time.sleep(0.5)
    
    # 3. Step 2: DESCRIBE
    print(f"\nSTEP 2: Querying describe on RO port {PORT_RO_DESCRIBE} to confirm membership...")
    confirmed_paths = set()
    for m in metrics_in_trace:
        ro_sock = connect_socket(host, PORT_RO_DESCRIBE, f"Describe {m}")
        if ro_sock:
            wait_for_greeting(ro_sock)
            cmd = f"{m} describe"
            try:
                raw_resp, resp_text = send_command(ro_sock, cmd, timeout=5.0)
                raw_str = raw_resp.decode("utf-8", errors="replace")
                json_objects = _extract_json_objects(raw_str)
                for obj in json_objects:
                    _extract_identities_from_obj(obj, confirmed_paths)
            except Exception as e:
                print(f"    [FAIL] Describe command failed for {m}: {e}")
            graceful_close(ro_sock)
        else:
            print(f"  [WARN] Unable to connect for describe verification of {m}.")
            
    print(f"  Describe verification finished. Confirmed {len(confirmed_paths)} active signals.")
    time.sleep(0.5)
    
    # 4. Step 3: EMIT
    print(f"\nSTEP 3: Listening on Emit stream port {PORT_RO_EMIT} ({listen_duration}s)...")
    emitted_paths = set()
    emit_sock = connect_socket(host, PORT_RO_EMIT, "Emit Stream")
    if emit_sock:
        emit_sock.settimeout(1.0)
        try:
            emit_sock.recv(4096)
        except socket.timeout:
            pass
            
        all_data = bytearray()
        start_time = time.monotonic()
        emit_sock.settimeout(2.0)
        while time.monotonic() - start_time < listen_duration:
            try:
                data = emit_sock.recv(4096)
                if not data:
                    break
                all_data.extend(data)
            except socket.timeout:
                continue
            except Exception as e:
                print(f"    [ERROR] Recv error during emission: {e}")
                break
        emit_sock.close()
        
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
        print(f"  Emit stream finished. Captured {len(emitted_paths)} unique active emission paths.")
    else:
        print("  [FATAL] Unable to connect for emit listening.")
        return None
        
    time.sleep(0.5)
    
    # 5. Step 4: STOP/CLEAR
    print(f"\nSTEP 4: Sending stop/clear command to RW port {PORT_RW}...")
    for m in metrics_in_trace:
        execute_metric_clear(host, m)
    
    # 6. Post-Check & Enforce Silence
    print("\nSTEP 5: Post-Test state verification (verifying silent PLC)...")
    if not enforce_silence_workflow(host, metrics_in_trace):
        print("  [WARN] Post-test cleanup did not result in absolute silence! Check PLC status.")
    else:
        print("  [OK] Post-test cleanup verified. PLC is completely silent.")
        
    # Compile Results
    active_signals = []
    silent_signals = []
    failed_signals = []
    
    for info in expected_signals:
        norm_path = info["normalized_path"]
        is_registered = norm_path in registered_paths
        is_described = norm_path in confirmed_paths
        is_emitted = norm_path in emitted_paths
        
        status_rec = {
            "name": info["name"],
            "path": info["original_path"],
            "normalized_path": norm_path,
            "registered": "OK" if is_registered else "FAIL",
            "described": "YES" if is_described else "NO",
            "emitted": "YES" if is_emitted else "NO"
        }
        
        if is_described and is_emitted:
            status_rec["status"] = "PASS_ACTIVE"
            active_signals.append(status_rec)
        elif is_described and not is_emitted:
            status_rec["status"] = "SILENT"
            silent_signals.append(status_rec)
        else:
            status_rec["status"] = "FAIL"
            failed_signals.append(status_rec)
            
    print("\n" + "=" * 80)
    print(f"  FOCUSED TEST REPORT: {trace_name}")
    print(f"  Status Summary: {len(active_signals)} Active | {len(silent_signals)} Silent | {len(failed_signals)} Failed")
    print("=" * 80)
    
    # Generate MD report
    report_file_md = os.path.join(RESULTS_DIR, f"{trace_name}_focused_report.md")
    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    with open(report_file_md, "w", encoding="utf-8") as f:
        f.write(f"# Telemetry Focused Report: {trace_name}\n\n")
        f.write(f"- **Tested At:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"- **PLC Host:** {host}\n")
        f.write(f"- **Metric Containers:** {', '.join(metrics_in_trace)}\n\n")
        
        f.write("## Summary Statistics\n\n")
        f.write("| Status | Count | Percentage |\n")
        f.write("| --- | ---: | ---: |\n")
        tot = len(signals)
        f.write(f"| **Active (PASS_ACTIVE)** | {len(active_signals)} | {len(active_signals)/tot*100:.1f}% |\n")
        f.write(f"| **Silent (SILENT)** | {len(silent_signals)} | {len(silent_signals)/tot*100:.1f}% |\n")
        f.write(f"| **Failed (FAIL)** | {len(failed_signals)} | {len(failed_signals)/tot*100:.1f}% |\n")
        f.write(f"| **Total Expected** | {tot} | 100.0% |\n\n")
        
        f.write("## 🟢 Verified Active Signals (PASS_ACTIVE)\n\n")
        if active_signals:
            f.write("| Signal Name | PLC Path | Registered | Described | Emitted |\n")
            f.write("| --- | --- | :---: | :---: | :---: |\n")
            for s in sorted(active_signals, key=lambda x: x["name"]):
                f.write(f"| `{s['name']}` | `{s['path']}` | {s['registered']} | {s['described']} | {s['emitted']} |\n")
        else:
            f.write("*No active signals verified.*\n")
        f.write("\n")
        
        f.write("## 🔴 Failed / Inactive Signals (FAIL)\n\n")
        if failed_signals:
            f.write("| Signal Name | PLC Path | Registered | Described | Emitted |\n")
            f.write("| --- | --- | :---: | :---: | :---: |\n")
            for s in sorted(failed_signals, key=lambda x: x["name"]):
                f.write(f"| `{s['name']}` | `{s['path']}` | {s['registered']} | {s['described']} | {s['emitted']} |\n")
        else:
            f.write("*No failed signals.*")
        f.write("\n")
        
    print(f"Beautiful Markdown report saved to: [Report](file:///{report_file_md.replace(chr(92), '/')})")
    return {
        "trace": trace_name,
        "active": active_signals,
        "silent": silent_signals,
        "failed": failed_signals
    }


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Focused sequential trace verification with pre/post clean workflow.")
    parser.add_argument("-t", "--trace", default="cTransTest", help="Name of the trace configuration file to test")
    parser.add_argument("-H", "--host", default=DEFAULT_HOST, help="PLC IP Address")
    parser.add_argument("-d", "--duration", type=float, default=EMIT_LISTEN_DURATION, help="Duration to listen to emit stream in seconds")
    parser.add_argument("--trace-dir", default=TRACE_DIR, help="Directory containing trace JSON files")
    args = parser.parse_args()
    
    trace_dir = args.trace_dir
    trace_file = os.path.join(trace_dir, f"{args.trace}.json")
    
    # Smart fallback resolution
    if not os.path.exists(trace_file):
        # Fallback 1: Try relative to script's directory (SCRIPT_DIR)
        trace_file = os.path.join(SCRIPT_DIR, trace_dir, f"{args.trace}.json")
        
    if not os.path.exists(trace_file):
        # Fallback 2: If user passed report/trace/pass_active but is already inside report/trace
        normalized_dir = trace_dir.replace("report/trace/", "").replace("report\\trace\\", "")
        trace_file = os.path.join(SCRIPT_DIR, normalized_dir, f"{args.trace}.json")
        
    if not os.path.exists(trace_file):
        # Fallback 3: Just check if the last directory name exists inside the script folder
        basename_dir = os.path.basename(trace_dir.rstrip("/\\"))
        trace_file = os.path.join(SCRIPT_DIR, basename_dir, f"{args.trace}.json")
        
    if not os.path.exists(trace_file):
        # Fallback 4: Try relative to project root
        trace_file = os.path.join(PROJECT_ROOT, trace_dir, f"{args.trace}.json")
        
    if not os.path.exists(trace_file):
        print(f"[ERROR] Trace config file not found. Tried resolving paths:")
        print(f"  - {os.path.join(os.getcwd(), trace_dir, f'{args.trace}.json')}")
        print(f"  - {os.path.join(SCRIPT_DIR, trace_dir, f'{args.trace}.json')}")
        sys.exit(1)
        
    run_focused_test(args.host, trace_file, args.duration)


if __name__ == "__main__":
    main()

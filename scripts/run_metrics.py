#!/usr/bin/env python3
"""
transA Metric Runner - Send metric registration/deregistration commands to a PLC.

Reads a JSON template (e.g. transA_start.json or transA_stop.json), opens a TCP
connection to the PLC, and sends each command in order.  Prints every command
sent and the response received.

Response-framing assumptions (documented for safety):
  - After connecting, the PLC sends a prompt ending with "$>".
  - Each command is sent as ASCII text terminated by "\\r\\n".
  - The PLC replies with optional JSON payload followed by a "|$>" terminator.
  - We read until "|$>" is seen or a timeout elapses.
  - Registration/deregistration commands are typically silent (just "$>" prompt).

Usage:
    python run_metrics.py scripts/transA_start.json
    python run_metrics.py scripts/transA_stop.json
    python run_metrics.py scripts/transA_start.json --host 10.2.3.4 --port 49870
    python run_metrics.py scripts/transA_start.json --dry-run
"""

import argparse
import json
import socket
import sys
import time


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT = 5.0          # seconds per send/receive cycle
DEFAULT_CONNECT_TIMEOUT = 5.0  # seconds for initial TCP connect
PROMPT = b"$>"
TERMINATOR = b"|$>"
LINE_END = b"\r\n"


def load_template(path: str) -> dict:
    """Load and return the JSON template."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def recv_until_terminator(sock: socket.socket, timeout: float) -> str:
    """
    Read from *sock* until TERMINATOR (|$>) is found or *timeout* elapses.

    Returns the accumulated response as a decoded string (terminator stripped).
    """
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
        idx = buf.find(TERMINATOR)
        if idx != -1:
            return buf[:idx].decode("utf-8", errors="replace").strip()
    # Fallback: return whatever we got (may just be the prompt)
    raw = buf.decode("utf-8", errors="replace").strip()
    # Strip trailing prompt if present
    if raw.endswith("$>"):
        raw = raw[:-2].strip()
    return raw


def wait_for_prompt(sock: socket.socket, timeout: float = 2.0) -> str:
    """
    Consume the initial greeting/prompt after connecting.

    Returns the text before the first "$>" prompt.
    """
    return recv_until_terminator(sock, timeout)


def send_command(sock: socket.socket, cmd: str, timeout: float) -> str:
    """Send a single command and return the response string."""
    sock.sendall((cmd + "\r\n").encode("ascii"))
    return recv_until_terminator(sock, timeout)


def run(template_path: str, host: str | None, port: int | None,
        timeout: float, dry_run: bool) -> None:
    """Main runner logic."""
    tpl = load_template(template_path)

    # Resolve host/port: CLI override > JSON target > hardcoded fallback
    target = tpl.get("target", {})
    resolved_host = host or target.get("host", "10.2.3.4")
    resolved_port = port or target.get("port_rw", 49870)

    commands = tpl.get("commands", [])
    if not commands:
        print("[WARN] No commands found in template.")
        return

    print(f"Template : {tpl.get('template', 'unknown')} v{tpl.get('version', '?')}")
    print(f"Host     : {resolved_host}:{resolved_port}")
    print(f"Commands : {len(commands)}")
    print("-" * 60)

    if dry_run:
        for i, entry in enumerate(commands, 1):
            print(f"  [{i}] {entry['command']}")
        print("\n(Dry run - no connection made.)")
        return

    # Connect
    print(f"Connecting to {resolved_host}:{resolved_port} ...")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(DEFAULT_CONNECT_TIMEOUT)
    try:
        sock.connect((resolved_host, resolved_port))
    except OSError as exc:
        print(f"[ERROR] Connection failed: {exc}", file=sys.stderr)
        sys.exit(1)

    # Consume initial prompt
    greeting = wait_for_prompt(sock, timeout=DEFAULT_CONNECT_TIMEOUT)
    if greeting:
        print(f"  Greeting: {greeting}")

    # Send commands
    ok = 0
    fail = 0
    for i, entry in enumerate(commands, 1):
        cmd = entry["command"]
        try:
            resp = send_command(sock, cmd, timeout)
            status = "OK" if resp == "" or resp == "$>" else "RESP"
            if status == "OK":
                ok += 1
            else:
                fail += 1
            print(f"  [{i:2d}] {status} | {cmd}")
            if resp and resp not in ("", "$>"):
                print(f"         -> {resp}")
        except OSError as exc:
            fail += 1
            print(f"  [{i:2d}] FAIL | {cmd}  ({exc})", file=sys.stderr)

    # Summary
    print("-" * 60)
    print(f"Done.  OK={ok}  non-silent={fail}  total={len(commands)}")

    sock.close()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Send metric commands from a JSON template to a PLC.")
    parser.add_argument("template", help="Path to the JSON template file")
    parser.add_argument("--host", default=None, help="Override PLC host")
    parser.add_argument("--port", type=int, default=None,
                        help="Override PLC port (default: port_rw from JSON)")
    parser.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT,
                        help=f"Per-command timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("--dry-run", action="store_true",
                        help="Print commands without connecting")
    args = parser.parse_args()

    run(args.template, args.host, args.port, args.timeout, args.dry_run)


if __name__ == "__main__":
    main()

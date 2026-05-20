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

Cleanup safety:
  - Before closing the TCP socket, the script sends a ``close`` command to the
    PLC so the ParseConnectionHandler can release its side of the session
    (SysSockClose).  This reduces the risk of stale sessions on ParseServerRW.
  - Signal handlers (SIGINT / SIGTERM) attempt the same graceful cleanup so
    that Ctrl+C or a termination signal does not leave the PLC session hanging.

Usage:
    # From project root:
    python scripts/run_metrics.py scripts/transA_start.json
    python scripts/run_metrics.py transA_start.json

    # From scripts/ directory:
    python run_metrics.py transA_start.json

    # With overrides:
    python scripts/run_metrics.py transA_start.json --host 10.2.3.4 --port 49870
    python scripts/run_metrics.py transA_start.json --dry-run
"""

import argparse
import json
import os
import signal
import socket
import sys
import time

# ---------------------------------------------------------------------------
# Python version check (needs 3.7+ for time.monotonic, 3.6+ for f-strings)
# ---------------------------------------------------------------------------
if sys.version_info < (3, 7):
    print(
        "[ERROR] Python 3.7+ is required. "
        "You are running Python {}.{}.".format(sys.version_info[0], sys.version_info[1]),
        file=sys.stderr,
    )
    sys.exit(1)


# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------
DEFAULT_TIMEOUT = 5.0          # seconds per send/receive cycle
DEFAULT_CONNECT_TIMEOUT = 5.0  # seconds for initial TCP connect
CLOSE_TIMEOUT = 2.0            # seconds for the session-close command
PROMPT = b"$>"
TERMINATOR = b"|$>"
LINE_END = b"\r\n"

# ---------------------------------------------------------------------------
# Global state for signal-safe cleanup
# ---------------------------------------------------------------------------
_shutdown_requested = False
_active_sock = None  # type: socket.socket | None


def _signal_handler(signum, frame):
    # type: (int, object) -> None
    """Handle SIGINT / SIGTERM by requesting graceful shutdown."""
    global _shutdown_requested
    sig_name = "SIGINT" if signum == signal.SIGINT else "SIGTERM"
    print("\n[{}] received — attempting graceful cleanup ...".format(sig_name))
    _shutdown_requested = True
    if _active_sock is not None:
        try:
            _active_sock.settimeout(CLOSE_TIMEOUT)
        except OSError:
            pass


def resolve_template_path(path):
    # type: (str) -> str
    """
    Resolve the JSON template path so it works from either the project root
    or the scripts/ directory.

    Resolution order:
      1. Exact path as given (works from any directory).
      2. Relative to the script's own directory (handles ``python run_metrics.py
         transA_start.json`` when cwd is project root).
      3. Prepend ``scripts/`` (handles ``python scripts/run_metrics.py
         transA_start.json`` from project root).
    """
    # 1. As-is
    if os.path.isfile(path):
        return path

    # 2. Relative to this script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    candidate = os.path.join(script_dir, path)
    if os.path.isfile(candidate):
        return candidate

    # 3. Prepend scripts/
    candidate = os.path.join("scripts", path)
    if os.path.isfile(candidate):
        return candidate

    # None found — return original so the caller produces a clear error
    return path


def load_template(path):
    # type: (str) -> dict
    """Load and return the JSON template."""
    with open(path, "r", encoding="utf-8") as fh:
        return json.load(fh)


def recv_until_terminator(sock, timeout):
    # type: (socket.socket, float) -> str
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


def wait_for_prompt(sock, timeout=2.0):
    # type: (socket.socket, float) -> str
    """
    Consume the initial greeting/prompt after connecting.

    Returns the text before the first "$>" prompt.
    """
    return recv_until_terminator(sock, timeout)


def send_command(sock, cmd, timeout):
    # type: (socket.socket, str, float) -> str
    """Send a single command and return the response string."""
    sock.sendall((cmd + "\r\n").encode("ascii"))
    return recv_until_terminator(sock, timeout)


def send_close_command(sock):
    # type: (socket.socket) -> None
    """
    Send the PLC ``close`` session command before tearing down the TCP socket.

    The ParseConnectionHandler on the PLC recognises ``close`` as a built-in
    command (cTokenClose) and calls SysSockClose on its client handle, which
    releases the server-side session resources.  This reduces the risk of
    stale sessions accumulating on ParseServerRW.

    Errors during this step are logged but never raised — the caller should
    always proceed to close the local socket regardless.
    """
    try:
        sock.settimeout(CLOSE_TIMEOUT)
        sock.sendall(b"close\r\n")
        # Consume whatever the PLC sends back (may be empty or a prompt).
        # We do not care about the content — the goal is to let the PLC
        # process the command before we pull the socket out from under it.
        recv_until_terminator(sock, CLOSE_TIMEOUT)
    except (socket.timeout, OSError) as exc:
        # Non-fatal: the PLC may already have closed its side, or the
        # network may be unreliable.  We still close our socket below.
        print("  [WARN] Session-close command failed ({}); closing socket anyway.".format(exc))


def graceful_close(sock):
    # type: (socket.socket) -> None
    """
    Perform a graceful TCP shutdown followed by socket close.

    1. Sends the PLC ``close`` command so the server can release its session.
    2. Calls ``shutdown(SHUT_WR)`` to signal end-of-stream to the peer.
    3. Calls ``close()`` to release the local socket descriptor.
    """
    try:
        send_close_command(sock)
    except Exception:
        pass  # Already logged inside send_close_command
    try:
        sock.shutdown(socket.SHUT_WR)
    except OSError:
        pass  # Peer may already have closed
    try:
        sock.close()
    except OSError:
        pass


def run(template_path, host, port, timeout, dry_run):
    # type: (str, str | None, int | None, float, bool) -> None
    """Main runner logic."""
    global _active_sock

    tpl = load_template(template_path)

    # Resolve host/port: CLI override > JSON target > hardcoded fallback
    target = tpl.get("target", {})
    resolved_host = host or target.get("host", "10.2.3.4")
    resolved_port = port or target.get("port_rw", 49870)

    commands = tpl.get("commands", [])
    if not commands:
        print("[WARN] No commands found in template.")
        return

    print("Template : {} v{}".format(
        tpl.get("template", "unknown"), tpl.get("version", "?")))
    print("Host     : {}:{}".format(resolved_host, resolved_port))
    print("Commands : {}".format(len(commands)))
    print("-" * 60)

    if dry_run:
        for i, entry in enumerate(commands, 1):
            print("  [{}] {}".format(i, entry["command"]))
        print("\n(Dry run - no connection made.)")
        return

    # Connect
    print("Connecting to {}:{} ...".format(resolved_host, resolved_port))
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    _active_sock = sock
    try:
        sock.settimeout(DEFAULT_CONNECT_TIMEOUT)
        sock.connect((resolved_host, resolved_port))
    except socket.timeout:
        print(
            "[ERROR] Connection timed out after {}s. "
            "Check that the PLC is powered on, reachable, and that port {} "
            "is open (not blocked by a firewall).".format(
                DEFAULT_CONNECT_TIMEOUT, resolved_port),
            file=sys.stderr,
        )
        sock.close()
        _active_sock = None
        sys.exit(1)
    except ConnectionRefusedError:
        print(
            "[ERROR] Connection refused by {}:{} — the PLC may be offline, "
            "the port may be wrong, or a firewall is blocking access. "
            "Hint: use --port 49870 for register/deregister (RW port), "
            "not 49880 (RO port).".format(resolved_host, resolved_port),
            file=sys.stderr,
        )
        sock.close()
        _active_sock = None
        sys.exit(1)
    except OSError as exc:
        print("[ERROR] Connection failed: {}".format(exc), file=sys.stderr)
        sock.close()
        _active_sock = None
        sys.exit(1)

    # Consume initial prompt
    try:
        greeting = wait_for_prompt(sock, timeout=DEFAULT_CONNECT_TIMEOUT)
    except OSError as exc:
        print(
            "[ERROR] Failed to read initial PLC greeting: {}. "
            "The connection may have been dropped.".format(exc),
            file=sys.stderr,
        )
        graceful_close(sock)
        _active_sock = None
        sys.exit(1)

    if greeting:
        print("  Greeting: {}".format(greeting))

    # Send commands
    ok = 0
    fail = 0
    interrupted = False
    try:
        for i, entry in enumerate(commands, 1):
            if _shutdown_requested:
                print("  [WARN] Shutdown requested — stopping after {} commands.".format(i - 1))
                interrupted = True
                break
            cmd = entry["command"]
            try:
                resp = send_command(sock, cmd, timeout)
                status = "OK" if resp == "" or resp == "$>" else "RESP"
                if status == "OK":
                    ok += 1
                else:
                    fail += 1
                print("  [{:2d}] {} | {}".format(i, status, cmd))
                if resp and resp not in ("", "$>"):
                    print("         -> {}".format(resp))
            except socket.timeout:
                fail += 1
                print(
                    "  [{:2d}] FAIL | {}  (command timed out after {}s — "
                    "PLC may be busy or port may be wrong)".format(
                        i, cmd, timeout),
                    file=sys.stderr,
                )
            except OSError as exc:
                fail += 1
                print("  [{:2d}] FAIL | {}  ({})".format(i, cmd, exc),
                      file=sys.stderr)
    finally:
        # Always perform graceful cleanup: send PLC close command, then
        # shutdown/close the local socket.  This runs even on Ctrl+C or
        # if a command loop exception occurs.
        graceful_close(sock)
        _active_sock = None

    # Summary
    print("-" * 60)
    summary = "Done.  OK={}  non-silent={}  total={}".format(ok, fail, len(commands))
    if interrupted:
        summary += "  (interrupted)"
    print(summary)


def main():
    # type: () -> None
    # Register signal handlers for graceful cleanup on Ctrl+C / SIGTERM
    signal.signal(signal.SIGINT, _signal_handler)
    signal.signal(signal.SIGTERM, _signal_handler)

    parser = argparse.ArgumentParser(
        description=(
            "Send metric commands from a JSON template to a PLC. "
            "The template path is resolved relative to the script directory, "
            "the current directory, or a 'scripts/' subdirectory."
        ),
        epilog=(
            "Examples:\n"
            "  python scripts/run_metrics.py transA_start.json\n"
            "  python scripts/run_metrics.py transA_start.json --dry-run\n"
            "  python scripts/run_metrics.py transA_start.json "
            "--host 10.2.3.4 --port 49870\n"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "template",
        help="Path to the JSON template file (e.g. transA_start.json)",
    )
    parser.add_argument(
        "--host", default=None,
        help="Override PLC host IP (default: from JSON template)",
    )
    parser.add_argument(
        "--port", type=int, default=None,
        help="Override PLC port (default: port_rw from JSON, usually 49870)",
    )
    parser.add_argument(
        "--timeout", type=float, default=DEFAULT_TIMEOUT,
        help="Per-command timeout in seconds (default: {})".format(DEFAULT_TIMEOUT),
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print commands that would be sent without connecting to the PLC",
    )
    args = parser.parse_args()

    # Resolve template path with fallbacks
    resolved = resolve_template_path(args.template)
    if not os.path.isfile(resolved):
        print(
            "[ERROR] Template file not found: {}".format(args.template),
            file=sys.stderr,
        )
        print(
            "  Searched: (1) as given, (2) relative to script dir, "
            "(3) scripts/ subdirectory.",
            file=sys.stderr,
        )
        sys.exit(1)

    run(resolved, args.host, args.port, args.timeout, args.dry_run)


if __name__ == "__main__":
    main()

# transA Metric Runner

Helper script + JSON templates for registering and deregistering telemetry metrics on the PLC via its TCP command port.

## Files

| File | Purpose |
|---|---|
| `run_metrics.py` | Python script that reads a JSON template, connects to the PLC, and sends each command in sequence. |
| `transA_start.json` | Metric **registration** template — run before a test to enable telemetry push. |
| `transA_stop.json` | Metric **deregistration** template — run after a test to tear down registrations. |

## Prerequisites

- **Python 3.7+** (uses only stdlib — no third-party packages).
- **Network access** to the PLC on the RW port (default `49870`).
- Required modules: `argparse`, `json`, `os`, `socket`, `signal`, `sys`, `time` (all stdlib).

## Quick Start

### From the project root

```bash
python scripts/run_metrics.py transA_start.json
python scripts/run_metrics.py transA_stop.json
```

### From the scripts/ directory

```bash
python run_metrics.py transA_start.json
python run_metrics.py transA_stop.json
```

### Dry-run (print commands without connecting)

```bash
python scripts/run_metrics.py transA_start.json --dry-run
```

### Override host, port, or timeout

```bash
python scripts/run_metrics.py transA_start.json --host 10.2.3.99 --port 49870 --timeout 10
```

Resolution order: CLI flag > JSON `target` field > hardcoded fallback (`10.2.3.4:49870`).

## Template Path Resolution

The script tries to find the JSON template in this order:

1. **As given** — works if you provide an absolute path or a path relative to your current directory.
2. **Relative to the script's own directory** — so `python scripts/run_metrics.py transA_start.json` from the project root finds `scripts/transA_start.json`.
3. **Under `scripts/`** — so `python run_metrics.py transA_start.json` from the project root also works.

## What to Expect

### Connection

After connecting, the PLC sends a greeting ending with the `$>` prompt. The script consumes this before sending commands.

### Registration / Deregistration responses

These commands are **silent** — the PLC replies with only the `$>` prompt (no JSON payload). The script marks these as `OK`.

### Commands with data responses

If a command returns a JSON payload, the script marks it as `RESP` and prints the payload.

### Response framing

- Each command is sent as ASCII text terminated by `\r\n`.
- The PLC replies with an optional JSON payload followed by the `|$>` terminator.
- The script reads until `|$>` is seen or the per-command timeout elapses.

### Summary line

After all commands finish:

```
Done.  OK=5  non-silent=0  total=5
```

## Graceful Session Cleanup

The script implements a **two-phase cleanup** to reduce the risk of stale sessions on the PLC's `ParseServerRW` (port 49870):

1. **PLC-side close command** — Before tearing down the TCP socket, the script sends the `close` command to the PLC. The `ParseConnectionHandler` recognises this as a built-in command (`cTokenClose`) and calls `SysSockClose` on its client handle, releasing server-side session resources.

2. **Graceful TCP shutdown** — After the close command, the script calls `shutdown(SHUT_WR)` to signal end-of-stream to the peer, then `close()` to release the local socket descriptor.

This cleanup runs automatically in all exit paths:

| Exit scenario | Cleanup behavior |
|---|---|
| Normal completion (all commands sent) | `close` command → `shutdown` → `close` |
| Command timeout or error | `close` command → `shutdown` → `close` |
| Ctrl+C (SIGINT) | Prints warning, sends `close` command → `shutdown` → `close` |
| SIGTERM | Same as SIGINT |
| Connection failure (before commands) | Immediate `close()` (no session to close) |

### Signal handling

Pressing **Ctrl+C** during command execution will:

1. Print a `[SIGINT] received` message.
2. Stop sending further commands after the current one.
3. Attempt the graceful cleanup sequence.
4. Print a summary line marked `(interrupted)`.

The same behavior applies to **SIGTERM** (e.g. from `kill` or a process manager).

## Important Syntax Findings

### Path separator: `/` (forward slash)

Object paths under `CANBusDrive` **must** use forward slashes:

```
CANBusDrive/cTransA/MotorTemp     ✅
CANBusDrive.cTransA.MotorTemp     ❌  (dot syntax fails for deep paths)
```

### `object=` keyword is mandatory

Both register and deregister require the `object=` prefix:

```
Metric1m register object=CANBusDrive/cTransA/MotorTemp     ✅
Metric1m register CANBusDrive/cTransA/MotorTemp            ❌  (returns duplicate_cmd error)
Metric1m deregister object=CANBusDrive/cTransA/MotorTemp   ✅
```

### Ports

| Port | Use |
|---|---|
| `49870` (RW) | Register / deregister commands |
| `49880` (RO) | `describe` / verification only |

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `[ERROR] Template file not found` | Wrong path or running from unexpected directory | Use `scripts/transA_start.json` from project root, or `transA_start.json` from `scripts/`. |
| `[ERROR] Connection timed out` | PLC unreachable, wrong IP, or firewall blocking | Verify PLC is reachable: `ping 10.2.3.4`; check firewall rules. |
| `[ERROR] Connection refused` | PLC offline, wrong port, or firewall | Use port `49870` (RW) for register/deregister, not `49880` (RO). |
| `duplicate_cmd` error | Missing `object=` keyword in command | Use `MetricXs register object=<path>`. |
| Command fails / no response | Dot-separated path instead of slash-separated | Use `/` not `.` in object paths. |
| Timeout on every command | Connected to RO port (49880) instead of RW port | Use port `49870` for register/deregister. |
| Path not found | Signal name mismatch or wrong hierarchy | Run `MetricXs describe CANBusDrive/cTransA` to enumerate available children. |
| `[WARN] Session-close command failed` | PLC already closed its side or network issue | Non-fatal — local socket is still closed. No action needed. |

## Caveats and Limitations

- **`close` command is best-effort.** If the PLC has already dropped the connection (e.g. due to a network fault or PLC-side timeout), the close command will fail silently. The local socket is still cleaned up.
- **No session-recovery retry.** If the connection drops mid-command, the script stops and cleans up. It does not attempt to reconnect. Re-run the script if needed.
- **PLC-side session limits.** The `ParseTCPServer` has a finite connection limit (`cConnectionsLimit`). If all slots are occupied by stale sessions from previous unclean disconnects, new connections may be refused. The graceful cleanup in this script reduces that risk but cannot fix sessions left by other tools.
- **Signal handling on Windows.** `SIGTERM` is not natively supported on Windows; only `SIGINT` (Ctrl+C) is reliably delivered. On Linux/macOS, both signals are handled.
- **No authentication.** The ParseServerRW port (49870) has no authentication. Anyone with network access can send commands. Restrict network access via firewall rules.

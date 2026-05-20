# transA Metric Runner

Helper script + JSON templates for registering and deregistering telemetry metrics on the PLC via its TCP command port.

## Files

| File | Purpose |
|---|---|
| `run_metrics.py` | Python script that reads a JSON template, connects to the PLC, and sends each command in sequence. |
| `transA_start.json` | Metric **registration** template — run before a test to enable telemetry push. |
| `transA_stop.json` | Metric **deregistration** template — run after a test to tear down registrations. |

## Prerequisites

- **Python 3.10+** (uses `str | None` union syntax).
- **Network access** to the PLC on the RW port (default `49870`).
- No third-party packages — only stdlib (`argparse`, `json`, `socket`, `sys`, `time`).

## Quick Start

### Register metrics (start telemetry)

```bash
python run_metrics.py transA_start.json
```

### Deregister metrics (stop telemetry)

```bash
python run_metrics.py transA_stop.json
```

### Dry-run (print commands without connecting)

```bash
python run_metrics.py transA_start.json --dry-run
```

### Override host, port, or timeout

```bash
python run_metrics.py transA_start.json --host 10.2.3.99 --port 49870 --timeout 10
```

Resolution order: CLI flag > JSON `target` field > hardcoded fallback (`10.2.3.4:49870`).

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
| `Connection failed` | Wrong IP, PLC offline, or firewall blocking port 49870 | Verify PLC is reachable: `ping 10.2.3.4`; check firewall rules. |
| `duplicate_cmd` error | Missing `object=` keyword in command | Use `MetricXs register object=<path>`. |
| Command fails / no response | Dot-separated path instead of slash-separated | Use `/` not `.` in object paths. |
| Timeout on every command | Connected to RO port (49880) instead of RW port | Use port `49870` for register/deregister. |
| Path not found | Signal name mismatch or wrong hierarchy | Run `MetricXs describe CANBusDrive/cTransA` to enumerate available children. |

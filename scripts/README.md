# Scripts

This directory contains two categories of scripts:

1. **PLC Telemetry Helpers** — interact with the live PLC via TCP.
2. **Dependency Graph Pipeline** — analyze the CODESYS XML export to build a dependency graph.

---

## PLC Telemetry Helpers

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

---

## Measuring Profile (MP) Signal Discovery & Validation Workflow

Scripts and process for discovering, validating, and packaging signals from the live PLC into reusable measuring-profile templates (MP-01..MP-06 and beyond).

### When to Use Each Script

| Script | Purpose | When to Run | Dependencies |
|---|---|---|---|
| `validate_mp01_signals.py` | **Step 1 — Inspect & validate.** Sends `describe` for each candidate runtime path against the live PLC (RW port 49870). Enumerates parent nodes with `describe -children`. Saves results to `mp01_validation_results.json`. | First pass on a new MP template or when the PLC project has changed. Hardcoded for MP-01 signals; use as a reference pattern for new templates. | Python 3.7+, PLC reachable on port 49870 |
| `capture_identity.py` | **Step 2 — Capture identity.** Connects to the RO port (49880) and captures the exact `identity` field and a sample value for each confirmed runtime path. Conservative (read-only). Saves to `identity_capture_results.json`. | After validation confirms which paths are present. Use to fill the `identity` field in the verified-signals JSON. | Python 3.7+, PLC reachable on port 49880 |
| `update_mp02_06.py` | **Step 3 — Update Excel workbooks.** Batch-updates MP-02..MP-06 `.xlsx` templates with validated signal names, descriptions, hardware sources, and notes. | After validation + identity capture are complete. Mapping data is hardcoded per template; edit the `MP02`..`MP06` lists before running. | Python 3.7+, `openpyxl`, templates in `templates/` |
| `process_mp.py` | **Step 4 — Orchestration stub.** Generates a `*-verified-signals.json` skeleton and packages outputs. Provides a checklist and template for future MP-N processing. | After all validation and workbook updates are done. Run to produce the final packaged artifacts. | Python 3.7+ |

### Step-by-Step Process for a New MP Template (e.g., MP-07)

#### Step 1 — Inspect the Template

Open the Excel workbook (e.g., `templates/MP-07.xlsx`) and review the existing signal rows. Each row has:
- **Signal Name** — the telemetry name used in reports
- **Description** — human-readable description
- **Hardware Source** — the PLC runtime path (e.g., `CANBusDrive/cTransA/Current`)
- **Note** — validation status (`present`, `no present`, `manual-only`, `not validated`)

#### Step 2 — Map Signals to Runtime/Export Candidates

For each signal row, identify one or more candidate runtime paths to test. Use these heuristics:
- CANOpen drive signals: `CANBusDrive/c<Device>/<SignalName>` (e.g., `CANBusDrive/cWinchA/MotorTemp`)
- System-level signals: `System/<Subsystem>/<SignalName>` (e.g., `System/BMSAB/Current`)
- Lift/hoist signals: `Lift/<SignalName>` or `System/iLift<Axis>Pos`
- Steering signals: `System/iSteer<Letter>Pos`

**Important:** Signal names on the PLC are often abbreviated (e.g., `BattVoltage` not `BatteryVoltage`, `CntrlTemp` not `ControllerTemperature`). Do not guess — always validate live.

#### Step 3 — Live Validate Signals Conservatively

Create a validation script modeled on `validate_mp01_signals.py`:

1. Define a `SIGNALS` list of `(template_name, [candidate_paths])` tuples.
2. Connect to the PLC on the **RW port (49870)**.
3. For each candidate path, send `<path> describe` and check for a valid response.
4. Record which paths are `present` vs `no present`.
5. Explore parent nodes with `<parent> describe -children` to discover additional signals.
6. Save results to a JSON file for reference.

**Conservative validation rules:**
- Only mark a signal as `present` if `describe` returns a non-error response.
- If multiple candidates succeed, prefer the path with the most specific/semantic match.
- If no candidate succeeds, mark as `no present` — do not fabricate a path.

#### Step 4 — Update Workbook Fields

After validation, update the Excel workbook columns:
- **Signal Name** — use the live-confirmed name (may differ from template placeholder).
- **Description** — refine based on what the live response reveals.
- **Hardware Source** — set to the confirmed runtime path, or `N/A` if not present.
- **Note** — one of: `present`, `no present`, `manual-only`, `not validated`.

Use `update_mp02_06.py` as a reference: it reads mapping tuples and writes to columns 1, 2, 4, and the Note column.

#### Step 5 — Capture Exact `identity`

Run a script modeled on `capture_identity.py` against the **RO port (49880)**:

1. For each confirmed runtime path, send `<path> describe`.
2. Parse the JSON response to extract the `identity` field (e.g., `PrimaryPLC.System.CANBusDrive/cWinchA/Current`).
3. Also capture a sample value for documentation.
4. Save results to `identity_capture_results.json`.

**Why RO port?** Identity capture is read-only and should not modify PLC state. The RO port (49880) enforces this.

#### Step 6 — Generate `*-verified-signals.json`

Create a verified-signals JSON file following the schema established by `MP-01-verified-signals.json`:

```json
{
  "_note": "Reusable baseline for MP-NN live-verified signals...",
  "profile": "MP-NN",
  "verified_at": "YYYY-MM-DD",
  "source_endpoint": {
    "rw": "10.2.3.4:49870",
    "ro": "10.2.3.4:49880"
  },
  "verification_policy": "live-confirmed only",
  "signals": [
    {
      "template_signal": "<original template row name>",
      "signal_name": "<live-confirmed name>",
      "runtime_path": "<confirmed PLC path>",
      "identity": "<exact identity from describe>",
      "sample_value": <value or null>,
      "status": "present",
      "evidence": "<brief note on how this was confirmed>"
    }
  ]
}
```

Only include signals with `status: "present"`. Signals marked `no present`, `manual-only`, or `not validated` are excluded from the verified registry.

#### Step 7 — Package Outputs

Copy the final artifacts to `export-src/measuring-profiles/`:
- `MP-NN.xlsx` — the updated workbook
- `MP-NN-verified-signals.json` — the verified signal registry

See `export-src/measuring-profiles/README.md` for the full packaging convention.

### Quick Reference: Port Usage

| Port | Purpose | Scripts That Use It |
|---|---|---|
| `49870` (RW) | Signal validation (`describe`), Metric5s register/deregister | `validate_mp01_signals.py`, `run_metrics.py` |
| `49880` (RO) | Identity capture, conservative read-only verification | `capture_identity.py` |

### Limitations Requiring Manual Judgment

- **Signal name abbreviations** — PLC signal names are often shortened. Live validation is the only reliable source.
- **Path separator** — Object hierarchy uses `/` (forward slash), not `.` (dot). Namespace prefix (`PrimaryPLC.`) uses dot and is optional.
- **Semantic matching** — When multiple candidate paths return valid responses, choosing the most semantically correct one requires human judgment.
- **Scaling and units** — The `describe` response may not include unit information. Scaling factors (e.g., `0.001 * NominalVoltage`) must be inferred from code review or domain knowledge.
- **`not validated` signals** — Signals with plausible paths that were not live-tested remain `not validated`. They should be tested before being promoted to `present`.
- **PLC project changes** — If the CODESYS project is updated, all verified signals should be re-validated. The `verified_at` date in the JSON file indicates when validation occurred.

---

## Dependency Graph Pipeline

Scripts that analyze the CODESYS PLCopenXML export to build a multi-phase dependency graph. Run these in order against an export directory (e.g., `exports/v1`).

### Full Pipeline

```bash
python scripts/index_xml.py exports/v1          # Phase 2: POU/DUT indexing
python scripts/build_xref.py exports/v1         # Phase 3: Cross-reference resolution
python scripts/analyze_graph.py exports/v1      # Phase 3.5: Transitive closure & cascade
python scripts/extract_impl_deps.py exports/v1  # Phase 4: Implementation-level deps
python scripts/unify_deps.py exports/v1         # Phase 4.5: Unified graph with provenance
python scripts/clean_graph.py exports/v1        # Phase 5: Filtering & confidence scoring
```

### Phase 2 — `index_xml.py`

Parses all XML files in `exports/v1/xml/` to produce a structured index of every POU, DUT, and library reference.

| Output | Description |
|---|---|
| `POU_INDEX.json` | Machine-readable index of all POUs, DUTs, libraries |
| `PROJECT_MAP.md` | Human-readable codebase structure map |

### Phase 2.5 — POU Interface Extraction

Built into `index_xml.py`. Extracts VAR_INPUT, VAR_OUTPUT, VAR, VAR_GLOBAL, and return type declarations from each POU interface.

### Phase 3 — `build_xref.py`

Resolves type names from POU interfaces against the known POU/DUT registry to build a dependency graph.

| Output | Description |
|---|---|
| `XREF.json` | Cross-reference data (uses, used_by, type resolution) |
| `DEPENDENCY_MAP.md` | Human-readable dependency and impact analysis |

### Phase 3.5 — `analyze_graph.py`

Computes transitive closures, impact cascades, centrality metrics, and notable dependency paths on the Phase 3 graph.

| Output | Description |
|---|---|
| `TRANSITIVE_CLOSURE.json` | Forward/reward transitive closure, centrality, paths |
| `CASCADE_ANALYSIS.md` | Human-readable cascade analysis with bridge/leaf/root classification |

### Phase 4 — `extract_impl_deps.py`

Scans ST (Structured Text) implementation bodies from the XML files to find behavioral dependencies: FB calls, method calls, property accesses, type casts, and general type references.

| Output | Description |
|---|---|
| `IMPL_DEPS.json` | Implementation-level dependency data |
| `IMPL_DEPENDENCY_MAP.md` | Structural vs behavioral dependency analysis |

### Phase 4.5 — `unify_deps.py`

Merges the interface-derived (Phase 3) and implementation-derived (Phase 4) graphs into a single graph with provenance tracking on every edge.

| Output | Description |
|---|---|
| `UNIFIED_DEPS.json` | Unified graph with provenance (interface / implementation / both) |
| `UNIFIED_DEPENDENCY_MAP.md` | Human-readable unified dependency map |

### Phase 5 — `clean_graph.py`

Filters false positives from the Phase 4.5 unified graph and assigns confidence scores to every surviving edge.

**Filtering rules** (edges removed if target matches):
- IEC 61131-3 keywords (IF, CASE, AND, OR, etc.)
- Standard type conversion functions (`*_TO_*`)
- Standard library FBs/functions (TON, MAX, MIN, ADR, etc.)
- Self-references (source == target)
- Local variable names (l*, r*, etc. not in known type registry)
- Common method/property names that are not project-defined types
- Unknown types (not in POU_INDEX.json registry)

**Confidence scoring**:
| Label | Score | Criteria |
|---|---|---|
| high | 0.95–1.00 | Provenance = "both" (interface + implementation) |
| medium | 0.70–0.94 | Provenance = "interface" (compiler-enforced) |
| low | 0.30–0.69 | Provenance = "implementation" (regex-inferred) |

| Output | Description |
|---|---|
| `CLEAN_DEPS.json` | Cleaned graph with confidence scores on every edge |
| `CLEAN_DEPENDENCY_MAP.md` | Filtering report with confidence distribution and impact analysis |

### Common Options

All pipeline scripts support `--no-index-update` to skip updating `INDEX.json` with artifact references.

### v1 Results Summary

| Phase | Edges | Nodes | Key Metric |
|---|---|---|---|
| Phase 3 | 534 | 432 | 235 resolved types, 0 unresolved |
| Phase 4 | 3,699 impl refs | 462 POUs | 122 impl-only types |
| Phase 4.5 | 4,209 | 1,805 | 24 edges confirmed by both sources |
| Phase 5 | **1,009** | **512** | **76% noise reduction**, 24 high-confidence edges |

For detailed documentation, see [docs/phase1-exports.md](../docs/phase1-exports.md).

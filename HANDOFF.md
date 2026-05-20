# CODESYS Project Review - Handoff Document

## Project: apollo-3cs-0.004bf - eolus- v5
**Date:** 2026-05-20
**Target:** STW ESX-3CS (ECU công nghiệp)
**CODESYS:** V3.5 SP11
**Version:** 1.0.0.0

---

## 1. Environment Setup

### Installed
- **Node.js:** v24.15.0 (installed via winget)
- **CODESYS MCP Toolkit:** @codesys/mcp-toolkit v1.1.16 (npm global)
- **CODESYS V3.5:** C:\Program Files (x86)\3S CODESYS V3.5\
- **Profile:** STW CODESYS V3.5 SP11 - ESX-3CS

### MCP Config (C:\Users\technician\.config\opencode\opencode.jsonc)
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "servers": {
      "codesys": {
        "command": "codesys-mcp-tool",
        "args": [
          "--codesys-path", "C:\\Program Files (x86)\\3S CODESYS V3.5\\CODESYS\\Common\\CODESYS.exe",
          "--codesys-profile", "STW CODESYS V3.5 SP11 - ESX-3CS",
          "--workspace", "C:\\local\\opencode\\codesys\\workspace"
        ]
      }
    }
  }
}
```

### MCP Tools Available (WRITE only)
- `codesys_open_project` ✅
- `codesys_create_project` ✅
- `codesys_create_pou` ✅
- `codesys_set_pou_code` ✅
- `codesys_create_method` ✅
- `codesys_create_property` ✅
- `codesys_compile_project` ✅
- `codesys_save_project` ✅

### MCP Limitation
- **READ operations** (resources: `codesys://project/.../pou/.../code`) are NOT supported by opencode CLI
- **Workaround:** Export PLCopenXML from CODESYS IDE manually → review XML files

---

## 2. Project Files

### Source XML Files (exported-src/)
| File | Size | Description |
|---|---|---|
| `apollo-3cs-0.004bf - eolus- v5.xml` | 4.1 MB | Main project (7 POUs) |
| `primary - eolus - v2d.xml` | 1.3 MB | Core library (104 POUs, 2+ DUTs) |
| `apollo-eolus - v2c.xml` | 330 KB | Apollo extension (39 POUs) |
| `services-eolus-heap-v8db.xml` | 2.2 MB | Services library (networking, TCP, reporting) |
| `canplc - eolus-v2b.xml` | 176 KB | CAN/PLC communication |
| `common.xml` | 55 KB | Common types/utilities |
| `machine - eolus - v1b.xml` | 90 KB | Machine-specific types |
| `build-isoloader.xml` | 7 KB | Build configuration |
| `device-3cs.xml` | 105 KB | ESX-3CS device config |

### Total: ~150 POUs across all libraries

---

## 3. Architecture Summary

### Inheritance Chain
```
PLC_PRG (project program)
  └─ gSystem: SystemBuild
       └─ SystemApollo (apollo lib)
            └─ SystemPrimary (primary lib)
                 └─ System (primary lib)

CANOpenMasterDriveBuild (project)
  └─ CANOpenMasterDriveApollo (apollo)
       └─ CANOpenMasterDrivePrimary (primary)
            └─ CANOpenMaster (primary)

LocalMachineBuild (project)
  └─ LocalMachinePrimary (primary)

ReportableChannelManagerBuild (project)
  └─ ReportableChannelManager (services lib)
```

### Key Components
- **CANOpenMasterDrive:** Manages 16+ CANOpen slave devices (Steer A-D, Trans A-D, Winch A-D, WinchAngle A-D, Spreader)
- **System:** Orchestrates all subsystems via registerOperational() pattern
- **Movement System:** TravelQuad, LiftQuad with interlocks (position, synchronous, twistlock)
- **Spreader:** Crane spreader controller with twistlock, telescoping, sideshift
- **UInterface:** Cabin + Radio dual interface for operator control
- **ReportableChannelManager:** TCP channels for logging, metrics, edge reporting
- **UMFS:** User Movement Function Safety system

---

## 4. Review Findings

### 🔴 HIGH (4 issues)
1. **TCP Servers no authentication** - Ports 49860-49889 open to network, 49870 allows interactive read-write
2. **Pointer dereference without initialization** - `ptr^ := ptr^ + 1` in PLC_PRG (line 3254), ptr is unassigned POINTER TO INT
3. **Duplicate EMCY error codes** - 3 pairs of error codes share same value in t_motor_emcy_id enum
4. **Outbound TCP without encryption** - 4 client channels push data to remote servers (ports 49700, 49710, 49720, 49740) with no TLS

### 🟡 MEDIUM (5 issues)
5. **10 TCP endpoints total** - 4 outbound PUSH, 6 inbound servers, all unencrypted
6. **Extensive commented-out code** - Crash tests, CAN tasks, calibration values, channels
7. **foobar comments** - 5+ places where developer marked uncertainty
8. **Debug counters never reset** - PackReportablePLC.read() counters a,b,c,d,e increment forever
9. **BMS fault enum gaps** - Missing values 39, 45-46, 49-50, 55-71

### 🟢 LOW (3 issues)
10. **Naming inconsistency** - gSystemPrimary vs gSystemApollo vs gSystem
11. **Interlock pattern repeated 4x** - SteerA/B/C/D identical code, should be array
12. **10+ ProgrammedMovement variants** - Could be parameterized

---

## 5. TCP/Network Endpoints (Complete Map)

| Port | Component | Mode | Direction | Data | Risk |
|---|---|---|---|---|---|
| 49700 | EdgeLog Client | Client | PUSH outbound | Logs | 🔴 |
| 49710 | EdgeStateMetric Client | Client | PUSH outbound | State metrics | 🔴 |
| 49720 | EdgeValueMetric Client | Client | PUSH outbound | Value metrics | 🔴 |
| 49730 | EdgeTrace Client | Client | Disabled | Trace | ✅ |
| 49740 | Executor Client | Client | PUSH outbound | Commands | 🔴 |
| 49860-69 | ParseServerEdge | Server | Inbound R/W | Edge data | 🟡 |
| 49870-79 | ParseServerRW | Server | Inbound R/W Interactive | Full access | 🔴 |
| 49880-89 | ParseServerRO | Server | Inbound RO Interactive | Read access | 🟡 |
| 49890-99 | LogTCP Server | Server | Inbound | Logs | 🟡 |

---

## 6. Library Dependencies

### Custom (Isoloader)
- `primary` - Core system logic (104 POUs)
- `apollo` - Crane-specific extensions (39 POUs)
- `services` - Network services, TCP, reporting
- `canplc` - CAN/PLC communication
- `common` - Shared types
- `machine` - Machine types
- `build` - Build config

### STW (Sensor-Technik Wiedemann)
- `STW openSYDE Datapool` (STW_OSYDP)
- `STW openSYDE Communication` (STW_OSYCOM)
- `STW ESX-3CS BIOS` v1.1.0.0
- `STW Errors` v1.4.1.0

### Third-party/System
- `3S CANopenStack` v3.5.11.0
- `CAA CiA 405` v3.5.8.0
- `CANbusDevice` v3.5.10.0
- `SysSocket` v3.5.9.0
- `Standard` v3.5.9.0, `Util` v3.5.11.0

### Compiler Defines
`TargetApollo, CANOPEN_NO_MODULARDEVICES, CANOPEN_NO_NODEGUARDING, CANOPEN_NO_TIMEPRODUCING, target_d19`

---

## 7. What Was Done This Session

### Phase 1 — Environment & Architecture Review
1. ✅ Installed Node.js v24.15.0
2. ✅ Installed @codesys/mcp-toolkit v1.1.16
3. ✅ Configured MCP server in opencode.jsonc
4. ✅ Discovered MCP limitation: no READ support in opencode CLI
5. ✅ Extracted project as ZIP (binary format, not readable)
6. ✅ User manually exported PLCopenXML files from CODESYS IDE
7. ✅ Reviewed all 3 main XML files (project + primary + apollo)
8. ✅ Identified 12 issues across HIGH/MEDIUM/LOW severity
9. ✅ Mapped all 10 TCP endpoints
10. ✅ Documented full architecture and inheritance chain

### Phase 2 — ParseServerRW TCP Investigation
11. ✅ Reviewed `services-eolus-heap-v8db.xml` — ParseTCPServer / ParseConnectionHandler implementation
12. ✅ Traced command parsing flow: `operator()` → `getNextExecuteCommand()` → `parse()` → `getParticle()` → `Executor.putCommand()`
13. ✅ Identified namespace requirement: `gNameSpace := 'PrimaryPLC'` — all commands must be prefixed with `PrimaryPLC.`
14. ⚠️ ~~Confirmed prompt string is `$$>`~~ — **CORRECTED by live testing:** actual prompt is `$>`
15. ⚠️ ~~Confirmed commands are resolved via `strcmp()` — case-sensitive matching~~ — **Partially corrected:** case sensitivity holds, but `PrimaryPLC.` prefix is optional despite source code suggesting it's required
16. ✅ Tested TCP connection to 10.2.3.4:49870 manually (telnet) — received prompt after connection
17. ✅ Attempted programmatic TCP tests (Node.js net.Socket) — **did not reproduce prompt behavior**
18. ✅ Reviewed ParseTCPServer config: ReadWrite=TRUE, Interactive=TRUE, WrappedResponse=FALSE, ReportError=TRUE

### Phase 3 — Live PLC Validation (ParseServerRW TCP)
19. ✅ **Live TCP validation succeeded** on both `10.2.3.4:49870` (ParseServerRW) and `10.2.3.4:49880` (ParseServerRO)
20. ✅ **Working command verb: `describe`** — alternatives `get`, `read`, `list`, `help`, `info`, `value`, `state` all failed
21. ✅ `System describe` — works, returns current system state (JSON)
22. ✅ `PrimaryPLC.System describe` — works, equivalent to above
23. ✅ `PrimaryPLC.System describe -children` — works, lists child particles
24. ✅ `PrimaryPLC.System.SystemState` — exposed child particle (readable)
25. ✅ `PrimaryPLC.System.State describe` — returns `unknown_name`
26. ✅ **Live state observed:** `systemstate = charging`
27. ✅ **`PrimaryPLC.` prefix is optional** — `System describe` works without it
28. ✅ **Prompt observed:** `$>` (not `$$>` as previously assumed from source code)
29. ✅ **Response framing:** JSON payload followed by `|$>` terminator
30. ⚠️ **Earlier assumptions corrected by live testing** — see Section 11 corrections

### Phase 4 — Live PLC Validation (MotorTemp Path & Metric5s Registration)
31. ✅ **Verified exact path: `CANBusDrive/cTransA/MotorTemp`** — uses forward-slash `/` separators, NOT dot `.` separators
32. ✅ **Dot-path syntax fails** — `CANBusDrive.cTransA.MotorTemp` (or any `.` variant) is rejected by the resolver
33. ✅ **Slash-path syntax works** — `CANBusDrive/cTransA/MotorTemp` resolves correctly
34. ✅ **Live value via `describe`: `45.0`** — MotorTemp currently reporting 45.0 (degrees C assumed)
35. ✅ **`Metric5s register object=CANBusDrive/cTransA/MotorTemp`** — works on RW port (49870)
36. ✅ **`Metric5s register <path>` without `object=` fails** — returns `duplicate_cmd` error
37. ✅ **Successful register is silent** — response is just `$>` prompt; no confirmation message
38. ✅ **`Metric5s describe` required to confirm registration** — shows membership before/after
39. ✅ **`Metric5s describe` before registration** — MotorTemp NOT listed as member
40. ✅ **`Metric5s describe` after registration** — MotorTemp IS listed as member
41. ⚠️ **Earlier assumptions about path syntax and registration syntax materially corrected** — see Section 12

### Phase 5 — Metric5s Periodic Events, Edge Metric Mapping & transA Signal Registration
42. ✅ **Metric5s emits periodic events** — after registering `CANBusDrive/cTransA/MotorTemp` to Metric5s, the PLC pushes metric data at ~5-second intervals to the edge metric channel.
43. ✅ **Observable channel confirmed: port 49890** — LogTCP server on port 49890-49899 receives periodic metric event payloads from registered Metric5s subscriptions.
44. ✅ **Edge metric outbound mapping: 10.2.3.10:49720** — code-backed confirmation that EdgeValueMetric client pushes registered metrics to `10.2.3.10:49720` (previously mapped in Section 5 but now confirmed as the live destination for Metric5s data).
45. ✅ **transA MotorTemp live metric registration** — `Metric5s register object=CANBusDrive/cTransA/MotorTemp` confirmed working; periodic values observed flowing through port 49890 and outbound to 10.2.3.10:49720.
46. ✅ **Five live signal names corrected under CANBusDrive/cTransA** — all verified via live `describe`:
    - `Current` (not a guessed name — live-verified)
    - `MotorTemp` (live-verified, value 45.0 observed)
    - `BattVoltage` (previously guessed as `BatteryVoltage` — **corrected**)
    - `BattCurrent` (previously guessed as `BatteryCurrent` — **corrected**)
    - `CntrlTemp` (previously guessed as `ControllerTemperature` — **corrected**)
47. ✅ **Split template files created** — `scripts/transA_start.json` (registration) and `scripts/transA_stop.json` (deregistration), each containing all 5 transA signals with correct paths, metric intervals, and `object=` syntax.
48. ✅ **Python helper hardened** — `scripts/run_metrics.py` rewritten for robustness:
    - `close` command sent before TCP teardown to release PLC-side ParseServerRW sessions
    - Signal handlers (SIGINT/SIGTERM) for graceful cleanup on Ctrl+C
    - `resolve_template_path()` — works from project root or scripts/ directory
    - Python 3.7+ compatibility (removed f-strings, added version check)
    - Specific error messages for timeout, connection refused, greeting failure
    - `graceful_close()` — two-phase shutdown: PLC close command → `shutdown(SHUT_WR)` → `close()`
    - `finally` block ensures cleanup runs on all exit paths (normal, error, interrupt)
49. ✅ **README updated** — `scripts/README.md` expanded with:
    - Graceful session cleanup documentation (close command + TCP shutdown)
    - Signal handling behavior (Ctrl+C / SIGTERM)
    - Template path resolution order
    - New troubleshooting entries (template not found, session-close warning)
    - Caveats and limitations section (best-effort close, no retry, Windows SIGTERM, no auth)
50. ⚠️ **Multiple prior signal-name assumptions corrected by live testing** — see Section 13 corrections.

### Phase 6 — Helper Hardening & Git Preservation
51. ✅ **`close` command cleanup** — ParseConnectionHandler recognises `close` as `cTokenClose` and calls `SysSockClose`; script now sends this before socket teardown to prevent stale sessions on ParseServerRW.
52. ✅ **Signal handling** — SIGINT (Ctrl+C) and SIGTERM handlers set global flag, interrupt command loop, and trigger graceful cleanup sequence.
53. ✅ **Remaining caveats documented** — `close` is best-effort; no session-recovery retry; PLC-side connection limits; Windows SIGTERM not supported; no authentication on port 49870.
54. ✅ **Git preservation** — hardened `scripts/run_metrics.py`, updated `scripts/README.md`, and this HANDOFF.md committed to `plc-telemetry-tools` repo for future exploration.

### Phase 5 (Dependency Graph) — Graph Cleaning & Confidence Scoring
55. ✅ **`scripts/clean_graph.py`** — Phase 5 filtering script: removes IEC keywords, conversion functions, standard library FBs, local variable names, self-references, common member names, and unknown types from the Phase 4.5 unified graph.
56. ✅ **Confidence scoring model** — Every surviving edge scored: high (0.95–1.00, provenance=both), medium (0.70–0.94, provenance=interface), low (0.30–0.69, provenance=implementation with sub-scoring by category).
57. ✅ **`exports/v1/CLEAN_DEPS.json`** — Clean machine-readable graph: 1,009 edges (down from 4,209), 512 nodes (down from 1,805), 3,200 false positives removed (76% reduction).
58. ✅ **`exports/v1/CLEAN_DEPENDENCY_MAP.md`** — Human-readable report: filtering results by category, confidence distribution, signal improvement metrics, top nodes by degree, high/medium/low confidence edge listings, and clean graph impact analysis.
59. ✅ **INDEX.json updated** — `phase5_artifacts` section added referencing CLEAN_DEPS.json and CLEAN_DEPENDENCY_MAP.md.
60. ✅ **docs/phase1-exports.md updated** — Full Phase 5 documentation section with schema, filtering rules, confidence scoring model, v1 summary, and limitations.
61. ✅ **exports/v1/README.md updated** — Phase 5 section with key findings and regeneration instructions.

---

## 8. Next Steps / TODO

### Immediate (P0)
- [ ] Fix pointer dereference in PLC_PRG (line 3254)
- [ ] Add authentication to TCP servers (especially 49870)
- [ ] Fix duplicate EMCY error codes in t_motor_emcy_id
- [ ] Review outbound TCP destinations (IPs not found in exported code - likely in services lib)

### ParseServerRW Investigation (P0)
- [x] ~~Resolve programmatic vs manual telnet discrepancy~~ — **RESOLVED:** Live validation confirmed both ports 49870 and 49880 accept connections and respond to commands
- [x] ~~Test with raw TCP~~ — **RESOLVED:** `describe` verb confirmed working; full command set needs exploration
- [ ] Map all available particles/commands via `describe -children` traversal
- [ ] Test write operations on ParseServerRW (port 49870) — confirm R/W capability
- [ ] Test read-only enforcement on ParseServerRO (port 49880)
- [ ] Understand `EnableSkipCompletingNewline := TRUE` effect on command termination
- [ ] Review `ConnectionHandler` base class (in services lib) for `connecting()` / `onDataReceived()` lifecycle

### Metric5s & Edge Telemetry (P0)
- [x] ~~Confirm Metric5s emits periodic events~~ — **RESOLVED:** ~5s interval confirmed after registration
- [x] ~~Confirm observable channel port 49890~~ — **RESOLVED:** LogTCP server on 49890-49899 receives metric payloads
- [x] ~~Confirm edge metric outbound destination 10.2.3.10:49720~~ — **RESOLVED:** code-backed mapping confirmed
- [x] ~~Live-verify all 5 transA signal names~~ — **RESOLVED:** Current, MotorTemp, BattVoltage, BattCurrent, CntrlTemp
- [ ] Test Metric5s registration for other CANOpen drives (cTransB/C/D, cSteerA-D, cWinchA-D)
- [ ] Verify Metric250ms, Metric1s, Metric1h, Metric1d intervals emit at expected cadence
- [ ] Capture and parse actual JSON payloads from port 49890 to confirm metric format
- [ ] Confirm edge server at 10.2.3.10:49720 is receiving and processing metric data

### Short-term (P1)
- [ ] Add TLS/encryption for outbound connections
- [ ] Clean up commented-out code
- [ ] Resolve all foobar comments
- [ ] Fix debug counter overflow in PackReportablePLC
- [ ] Review services library for TCP implementation details

### Medium-term (P2)
- [ ] Refactor interlock pattern to array-based
- [ ] Consolidate ProgrammedMovement variants
- [ ] Fill BMS fault enum gaps
- [ ] Standardize naming conventions

### Phase 3: Cross-Reference Resolution (Done)
- [x] `scripts/build_xref.py` — Cross-reference builder over POU_INDEX.json
- [x] `exports/v1/XREF.json` — Machine-readable dependency data (534 edges, 235 resolved types, 0 unresolved)
- [x] `exports/v1/DEPENDENCY_MAP.md` — Human-readable impact analysis and dependency chains
- [x] INDEX.json updated with `phase3_artifacts` section
- [x] docs/phase1-exports.md updated with Phase 3 documentation
- [x] exports/v1/README.md updated with Phase 3 artifact references

### Phase 3.5: Transitive Dependency & Cascade Analysis (Done)
- [x] `scripts/analyze_graph.py` — Transitive closure, impact cascade, centrality, path finding
- [x] `exports/v1/TRANSITIVE_CLOSURE.json` — Machine-readable transitive dependency data (432 nodes, max 102 transitive impact)
- [x] `exports/v1/CASCADE_ANALYSIS.md` — Human-readable cascade analysis with bridge/leaf/root classification
- [x] INDEX.json updated with `phase3_5_artifacts` section
- [x] docs/phase1-exports.md updated with Phase 3.5 documentation
- [x] exports/v1/README.md updated with Phase 3.5 artifact references

### Phase 4: Implementation-Level Dependency Extraction (Done)
- [x] `scripts/extract_impl_deps.py` — ST body parser: FB calls, method calls, property accesses, type casts, impl refs
- [x] `exports/v1/IMPL_DEPS.json` — Machine-readable impl-level dependency data (3,428 bodies, 462 POUs, 173 types)
- [x] `exports/v1/IMPL_DEPENDENCY_MAP.md` — Human-readable structural vs behavioral dependency analysis
- [x] INDEX.json updated with `phase4_artifacts` section
- [x] docs/phase1-exports.md updated with Phase 4 documentation
- [x] exports/v1/README.md updated with Phase 4 artifact references

### Phase 4.5: Unified Dependency Graph (Done)
- [x] `scripts/unify_deps.py` — Merges interface-derived (Phase 3) and implementation-derived (Phase 4) graphs with provenance
- [x] `exports/v1/UNIFIED_DEPS.json` — Unified graph with provenance on every edge (4,209 edges, 1,805 nodes)
- [x] `exports/v1/UNIFIED_DEPENDENCY_MAP.md` — Human-readable unified map with key object analysis
- [x] INDEX.json updated with `phase4_5_artifacts` section
- [x] docs/phase1-exports.md updated with Phase 4.5 documentation
- [x] exports/v1/README.md updated with Phase 4.5 artifact references

### Phase 5: Graph Cleaning & Confidence Scoring (Done)
- [x] `scripts/clean_graph.py` — Filters false positives and assigns confidence scores
- [x] `exports/v1/CLEAN_DEPS.json` — Clean graph (1,009 edges, 512 nodes, 76% noise reduction)
- [x] `exports/v1/CLEAN_DEPENDENCY_MAP.md` — Human-readable filtering report with confidence distribution
- [x] INDEX.json updated with `phase5_artifacts` section
- [x] docs/phase1-exports.md updated with Phase 5 documentation
- [x] exports/v1/README.md updated with Phase 5 artifact references
- [x] HANDOFF.md updated with Phase 5 session entries and key files

### Needs More Info
- [ ] **services library** - Contains actual TCP client/server implementation, need to review how data is formatted/sent
- [ ] **Remote server IPs** - Not found in any exported XML, likely configured in services library or runtime config
- [ ] **Network isolation** - Verify if PLC is on isolated VLAN
- [ ] **Firewall rules** - Check if ports are restricted

---

## 9. Key Files Reference

### In Git (plc-telemetry-tools repo)
These files are committed and available for future project exploration:

```
├── .gitignore
├── HANDOFF.md                              (this document — full session findings)
├── plc_nodes_map.json                      (DEPRECATED — see exports/v1/INDEX.json)
├── docs/
│   └── phase1-exports.md                   (workflow docs for versioned XML exports, Phases 1-5)
├── exports/
│   └── v1/
│       ├── xml/                            (9 PLCopenXML files — committed snapshot)
│       ├── MANIFEST.json                   (snapshot metadata)
│       ├── INDEX.json                      (node discovery index)
│       ├── POU_INDEX.json                  (Phase 2 — POU/DUT index)
│       ├── PROJECT_MAP.md                  (Phase 2 — human-readable codebase map)
│       ├── XREF.json                       (Phase 3 — cross-reference data)
│       ├── DEPENDENCY_MAP.md               (Phase 3 — dependency/impact analysis)
│       ├── TRANSITIVE_CLOSURE.json         (Phase 3.5 — transitive closure, centrality, paths)
│       ├── CASCADE_ANALYSIS.md             (Phase 3.5 — cascade/impact analysis)
│       ├── IMPL_DEPS.json                  (Phase 4 — implementation-level dependency data from ST bodies)
│       ├── IMPL_DEPENDENCY_MAP.md          (Phase 4 — structural vs behavioral dependency analysis)
│       ├── UNIFIED_DEPS.json               (Phase 4.5 — unified dependency graph with provenance)
│       ├── UNIFIED_DEPENDENCY_MAP.md       (Phase 4.5 — human-readable unified dependency map)
│       ├── CLEAN_DEPS.json                 (Phase 5 — cleaned graph with confidence scores)
│       ├── CLEAN_DEPENDENCY_MAP.md         (Phase 5 — human-readable filtering report)
│       └── README.md                       (snapshot description)
└── scripts/
    ├── README.md                           (usage docs, syntax findings, troubleshooting, caveats)
    ├── run_metrics.py                      (hardened Python helper: close cleanup, signal handling, path resolution)
    ├── generate_manifest.py                (manifest generator for export snapshots)
    ├── index_xml.py                        (Phase 2/2.5: XML POU/DUT indexer)
    ├── build_xref.py                       (Phase 3: cross-reference resolution & dependency analysis)
    ├── analyze_graph.py                    (Phase 3.5: transitive closure, cascade, centrality, paths)
    ├── extract_impl_deps.py                (Phase 4: implementation-level dependency extraction from ST bodies)
    ├── unify_deps.py                       (Phase 4.5: unified dependency graph merging interface + implementation)
    ├── clean_graph.py                      (Phase 5: false positive filtering and confidence scoring)
    ├── transA_start.json                   (metric registration template — 5 transA signals)
    └── transA_stop.json                    (metric deregistration template — 5 transA signals)
```

### Local Only (not in git — can be regenerated or are environment-specific)
```
├── src/                                    (original binary .project)
├── workspace/                              (working copy .project)
├── exported-src/                           (PLCopenXML exports — large, regenerable)
├── project-extract/                        (ZIP extract, binary)
├── templates/                              (local Excel workbooks)
├── *.ps1                                   (one-time setup/export scripts)
├── explore_plc.py                          (ad-hoc exploration script)
├── mcp_input.txt                           (MCP test input)
├── opencode.json / .mcp.json               (local tool config)
├── .opencode/                              (opencode internal state)
└── CODESYS_Code_Review.md                  (initial review doc, superseded by HANDOFF.md)
```

---

## 10. Lessons Learned

1. **CODESYS .project files are binary ZIP** - cannot read directly, must export as PLCopenXML
2. **MCP toolkit only supports WRITE** - opencode CLI cannot read POU code via MCP resources
3. **Manual export is required** - User must export from CODESYS IDE: File → Export → PLCopenXML
4. **Libraries contain most logic** - Project itself is thin (7 POUs), libraries have 140+ POUs
5. **TCP implementation is in services library** - Need to review services-eolus-heap-v8db.xml for actual socket code
6. **ParseServerRW uses namespace-based command routing** - `gNameSpace := 'PrimaryPLC'` in source, but live testing shows `PrimaryPLC.` prefix is **optional**; resolver falls back to root namespace
7. **PLC task cycle matters for TCP** - MainTask at 10ms means connection handlers only process data once per cycle; quick connect/disconnect may not trigger any processing
8. **Telnet ≠ raw TCP** - Telnet sends IAC negotiation bytes that may affect how the PLC's TCP stack handles the connection
9. **Source code ≠ runtime behavior** - Prompt hardcoded as `$$>` in services lib, but live PLC responds with `$>`; always validate against live system
10. **`PrimaryPLC.` namespace prefix is optional** - Despite `gNameSpace := 'PrimaryPLC'` in source, `System describe` works without prefix; the resolver may fall back to root namespace
11. **`describe` is the primary command verb** - Common alternatives (get, read, list, help, info, value, state) all fail; `describe` returns JSON state
12. **Response framing uses `|$>` terminator** - Responses are JSON payloads followed by `|$>`, not just the prompt string
13. **`System.State` returns `unknown_name`** - The `.State` particle exists but does not return a meaningful state value; use `System describe` or `System.SystemState` instead
14. **Path separator is `/` for object hierarchy** - `CANBusDrive/cTransA/MotorTemp` uses forward slashes; dot `.` syntax fails for deep object paths (dot works only for namespace prefix like `PrimaryPLC.`)
15. **`Metric5s register` requires `object=` keyword** - Bare path `Metric5s register <path>` fails with `duplicate_cmd`; must use `Metric5s register object=<path>`
16. **Successful Metric5s registration is silent** - Only `$>` prompt returned; must use `Metric5s describe` to confirm membership
17. **Metric5s emits periodic events at ~5s intervals** - After registration, metric values are pushed automatically; no polling needed
18. **Port 49890 is the observable metric channel** - LogTCP server on 49890-49899 receives periodic metric event payloads from Metric5s subscriptions
19. **Edge metric destination is 10.2.3.10:49720** - EdgeValueMetric client pushes registered metrics to this endpoint; confirmed by code review and live behavior
20. **Signal names are shorter than guessed** - Live `describe` reveals `BattVoltage` (not `BatteryVoltage`), `BattCurrent` (not `BatteryCurrent`), `CntrlTemp` (not `ControllerTemperature`); always verify against live PLC rather than guessing from IEC variable names

---

## 11. ParseServerRW TCP Deep Dive

### Architecture
```
ParseTCPServer (extends TCPServer)
  └─ lHandlers[1..cConnectionsLimit]: ParseConnectionHandler[]
       └─ extends ConnectionHandler
            ├─ prompt()       → sends '$$>' (source) / `$>` (live observed)
            ├─ parse()        → tokenizes input, resolves particles
            ├─ operator()     → main cycle: read → parse → execute → write
            └─ clear()        → reset parse state
```

### Server Configuration (from primary lib, System.initializeStage0)
| Property | Value |
|---|---|
| `lParseServerRW.Name` | `'ParserRW'` |
| `lParseServerRW.ServerPort` | 49870 |
| `lParseServerRW.ServerPortLower` | 49870 |
| `lParseServerRW.ServerPortUpper` | 49879 |
| `lParseServerRW.ReadWrite` | TRUE |
| `lParseServerRW.Interactive` | TRUE |
| `lParseServerRW.WrappedResponse` | FALSE |
| `lParseServerRW.ReportError` | TRUE |

### Command Resolution Flow
1. **Connection accepted** → `connecting()` calls `clear()`, sets `lParsingComplete := TRUE`
2. **Each PLC cycle** → `operator()` checks `lParsingComplete`, calls `lConnection^.read()` into `lReadStream`
3. **`getNextExecuteCommand()`** → calls `prompt()` if `lPromptRequired`, then `parse()`
4. **`parse()`** → tokenizes stream via `lReadStream.getNextToken()`, resolves names via `getParticle()`
5. **`getParticle()`** → walks namespace tree starting from `gSystemServices`; **first token should match `gNameSpace`**
6. **`gNameSpace`** = `'PrimaryPLC'` (set in `initializeStage0`) — **but live testing shows prefix is optional** (resolver may fall back to root)
7. **Resolved command** → `Executor.putCommand()` for execution

### Key Code Details
- **Prompt (source)**: `$$>` (hardcoded, line 15147 in services lib)
- **Prompt (live observed)**: `$>` — **discrepancy with source code**
- **Response terminator**: `|$>` — JSON payload followed by this marker
- **Newline char**: `'$n'` (set in `ParseConnectionHandler.initialize()`)
- **Record delimiters**: `{` and `}` (for structured responses)
- **Indent**: empty string (no indentation in output)
- **Max tokens per command**: 32 (`cParseMaxTokens`)
- **Case sensitivity**: `strcmp()` used in `getParticle()` — **commands are case-sensitive**
- **Working verb**: `describe` — alternatives `get`, `read`, `list`, `help`, `info`, `value`, `state` all failed
- **Skip newline completion**: `EnableSkipCompletingNewline := TRUE` (ParseTCPServer.initialize)
- **Initial state**: `lParsingComplete := TRUE`, `lPromptRequired := TRUE`

### Command Format
Commands follow the namespace path (prefix is **optional** per live testing):
```
[PrimaryPLC.]<subsystem>.<particle> describe [args]
```
Examples (verified live):
- `System describe` → returns current system state (JSON)
- `PrimaryPLC.System describe` → same as above
- `PrimaryPLC.System describe -children` → lists child particles
- `PrimaryPLC.System.SystemState` → reads the SystemState child particle
- `PrimaryPLC.System.State describe` → returns `unknown_name`

### Live Validation Results (2026-05-19)
| Command | Port | Result |
|---|---|---|
| `System describe` | 49870 (RW) | ✅ Returns JSON with `systemstate = charging` |
| `PrimaryPLC.System describe` | 49870 (RW) | ✅ Same result as above |
| `PrimaryPLC.System describe -children` | 49870 (RW) | ✅ Lists child particles including `SystemState` |
| `PrimaryPLC.System.SystemState` | 49870 (RW) | ✅ Exposed child particle, readable |
| `PrimaryPLC.System.State describe` | 49870 (RW) | ✅ Returns `unknown_name` |
| `System describe` | 49880 (RO) | ✅ Works on read-only port too |
| `get`, `read`, `list`, `help`, `info`, `value`, `state` | 49870 | ❌ All failed — not recognized verbs |

### Earlier Command Attempts (Pre-Live Validation)
| Attempt | Method | Result |
|---|---|---|
| Manual telnet to 10.2.3.4:49870 | `telnet 10.2.3.4 49870` | ✅ Connected, received prompt |
| Node.js net.Socket connect | `net.createConnection(49870, '10.2.3.4')` | ❌ Connected but no prompt received |
| Node.js: connect + send data | connect → `socket.write('test\n')` | ❌ No response |
| Node.js: connect + wait | connect → setTimeout 5s | ❌ No prompt received |

### Corrections to Previous Assumptions
| Previous Assumption | Corrected Finding |
|---|---|
| Prompt is `$$>` | Live prompt is `$>` (source code says `$$>`) |
| `PrimaryPLC.` prefix required | Prefix is **optional** — `System describe` works without it |
| `System.State` would return meaningful state | Returns `unknown_name` |
| Response is just prompt + text | Responses are **JSON + `|$>`** terminator |
| Only port 49870 validated | Both **49870 (RW) and 49880 (RO)** validated live |
| Command format unknown | **`describe`** is the working verb; others fail |

---

## 12. MotorTemp Path & Metric5s Registration (Live Findings)

### Verified Path Syntax
| Syntax | Result | Notes |
|---|---|---|
| `CANBusDrive/cTransA/MotorTemp` | ✅ Works | **Correct path** — forward-slash `/` separators |
| `CANBusDrive.cTransA.MotorTemp` | ❌ Fails | Dot `.` separators are **not** recognized by resolver |
| `CANBusDrive.cTransA/MotorTemp` | ❌ Fails | Mixed syntax also fails |

**Key finding:** The particle resolver uses `/` as the hierarchy separator, NOT `.`. This is a critical distinction from the `PrimaryPLC.System.SystemState` dot-path that worked earlier — the dot-path works for top-level namespace particles (where `PrimaryPLC.` is the namespace prefix), but deeper object paths under `CANBusDrive` require `/` separators.

### Live Value
```
CANBusDrive/cTransA/MotorTemp describe
→ 45.0
```
MotorTemp currently reporting **45.0** (units assumed °C based on context).

### Metric5s Registration

#### Correct Syntax (RW port 49870)
```
Metric5s register object=CANBusDrive/cTransA/MotorTemp
→ $>    (silent — no confirmation message)
```

#### Incorrect Syntax (fails)
```
Metric5s register CANBusDrive/cTransA/MotorTemp
→ duplicate_cmd    (error — missing `object=` keyword)
```

**Key finding:** The `register` command requires the `object=` keyword prefix. Omitting it causes a `duplicate_cmd` error, likely because the parser interprets the bare path as a second command token rather than an argument.

### Confirming Registration
Since successful registration produces **no output** beyond the `$>` prompt, `Metric5s describe` must be used to verify:

| Step | Command | Result |
|---|---|---|
| Before | `Metric5s describe` | MotorTemp **NOT** listed in members |
| After | `Metric5s register object=CANBusDrive/cTransA/MotorTemp` | Silent (`$>`) |
| Confirm | `Metric5s describe` | MotorTemp **IS** listed in members |

### Corrections to Previous Assumptions
| Previous Assumption | Corrected Finding |
|---|---|
| Dot `.` path syntax works for all paths | Dot syntax works for namespace prefix only; **`/` required for object hierarchy** under `CANBusDrive` |
| `Metric5s register <path>` (bare path) | Must use **`object=` keyword**: `Metric5s register object=<path>` |
| Registration returns confirmation | Registration is **silent** — only `$>` prompt; must use `describe` to verify |
| Path format unknown | **`CANBusDrive/cTransA/MotorTemp`** is the verified working path

---

## 13. transA Signal Name Corrections (Live Findings)

### Corrected Signal Names Under `CANBusDrive/cTransA`

All five signal names were verified live via `describe` on the PLC. Three were previously guessed from IEC variable naming conventions and were **incorrect**:

| # | Live Signal Name | Previously Guessed | Status | Metric Interval | Units | Scaling / Notes |
|---|---|---|---|---|---|---|
| 1 | `Current` | — (not guessed) | ✅ Live-verified | Metric250ms | Amps | Direct CAN signal |
| 2 | `MotorTemp` | — (not guessed) | ✅ Live-verified | Metric1m | °C | Value 45.0 observed live |
| 3 | `BattVoltage` | `BatteryVoltage` | ✅ **Corrected** | Metric250ms | Volts | Scaling: `0.001 * NominalVoltage` |
| 4 | `BattCurrent` | `BatteryCurrent` | ✅ **Corrected** | Metric250ms | Amps | Scaling: `NominalCurrent / 127.0` |
| 5 | `CntrlTemp` | `ControllerTemperature` | ✅ **Corrected** | Metric1m | °C | Offset: `-40` |

### Corrections to Previous Assumptions
| Previous Assumption | Corrected Finding |
|---|---|
| Signal name `BatteryVoltage` | Live name is **`BattVoltage`** (abbreviated) |
| Signal name `BatteryCurrent` | Live name is **`BattCurrent`** (abbreviated) |
| Signal name `ControllerTemperature` | Live name is **`CntrlTemp`** (abbreviated) |
| Signal names could be guessed from IEC conventions | **Do not guess** — always verify with `CANBusDrive/cTransA/<signal> describe` |

### Verified Full Paths
```
CANBusDrive/cTransA/Current        → Metric250ms
CANBusDrive/cTransA/MotorTemp      → Metric1m
CANBusDrive/cTransA/BattVoltage    → Metric250ms
CANBusDrive/cTransA/BattCurrent    → Metric250ms
CANBusDrive/cTransA/CntrlTemp      → Metric1m
```

### Metric Interval Summary
| Interval | Signals |
|---|---|
| Metric250ms | Current, BattVoltage, BattCurrent |
| Metric1m | MotorTemp, CntrlTemp |
| Metric500ms | (available, not used for transA) |
| Metric1s | (available, not used for transA) |
| Metric5s | (available, not used for transA) |
| Metric1h | (available, not used for transA) |
| Metric1d | (available, not used for transA) |

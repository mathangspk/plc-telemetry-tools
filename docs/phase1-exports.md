# Phase 1: Versioned XML Exports + Discovery Index

## Purpose

Establish a repeatable, versioned snapshot workflow for CODESYS PLC XML exports and PLC node discovery findings. This enables:

- **Traceability** — Each export is identified by a version tag (`v1`, `v2`, ...) with metadata.
- **Reviewability** — XML files are committed to git so they can be diffed and reviewed in PRs.
- **Discoverability** — A structured `INDEX.json` captures the PLC particle hierarchy, TCP endpoints, and live-verified signals.
- **Reproducibility** — A manifest generator script and documented workflow make it easy to create new snapshots.

## Directory Structure

```
exports/
  v1/
    xml/                  # PLCopenXML files (committed to git)
    MANIFEST.json         # Snapshot metadata (auto-generated + manual edits)
    INDEX.json            # Node discovery index (seeded from exploration)
    README.md             # Human-readable description of this snapshot
  v2/                     # Future snapshots follow the same structure
    xml/
    MANIFEST.json
    INDEX.json
    README.md
```

## Export ID Convention

- IDs are sequential: `v1`, `v2`, `v3`, ...
- Each ID corresponds to a subdirectory under `exports/`.
- IDs are **not** tied to git tags or project version numbers — they track export snapshots independently.

## Creating a New Export Snapshot

### Step 1: Export XML from CODESYS IDE

1. Open the `.project` file in CODESYS IDE.
2. For each library and the main project:
   - **File → Export → PLCopenXML**
   - Save to a temporary location.
3. Alternatively, use the export script in `exported-src/export_plcopenxml.py` (requires CODESYS scripting environment).

### Step 2: Create the Export Directory

```bash
mkdir -p exports/v<N>/xml
```

Replace `<N>` with the next sequential number.

### Step 3: Copy XML Files

Copy all exported `.xml` files into `exports/v<N>/xml/`.

### Step 4: Generate MANIFEST.json

```bash
python scripts/generate_manifest.py exports/v<N> \
  --project-name "apollo-3cs-0.004bf - eolus- v5" \
  --project-version "1.0.0.0"
```

Review and edit the generated `MANIFEST.json` to add:
- `compiler_defines` (if known)
- `total_pou_count_approx` (if known)
- Any additional notes

### Step 5: Create/Update INDEX.json

Run live PLC discovery queries (`describe`, `describe -children`) against the PLC and populate `INDEX.json` with:
- Root node identity and state
- Operational and non-operational children
- Live-verified signal names
- TCP endpoint map

For Phase 1, `INDEX.json` is seeded from the existing `plc_nodes_map.json`. Future exports should update this from live queries.

### Step 6: Write README.md

Create a `README.md` in the export directory describing:
- What this snapshot contains
- How it was created
- Known gaps or limitations
- How to regenerate

### Step 7: Commit

```bash
git add exports/v<N>/
git commit -m "Add export v<N>: <brief description>"
```

## MANIFEST.json Schema

| Field | Type | Description |
|---|---|---|
| `export_id` | string | Version tag (e.g., `"v1"`) |
| `created` | string | ISO 8601 timestamp |
| `project` | object | Project name, version, target, CODESYS version, profile |
| `source` | object | Binary project path, export method, script reference |
| `xml_files` | array | List of XML files with filename, role, description, size_kb |
| `total_xml_files` | integer | Count of XML files |
| `total_xml_size_kb` | number | Total size in KB |
| `total_pou_count_approx` | integer | Approximate POU count (optional) |
| `compiler_defines` | array | Compiler define strings (optional) |
| `notes` | array | Free-form notes |

## INDEX.json Schema

| Field | Type | Description |
|---|---|---|
| `export_id` | string | Must match MANIFEST.json export_id |
| `generated` | string | ISO 8601 timestamp |
| `root_node` | object | Identity, type, subsystem of the root PLC node |
| `state_at_export` | object | PLC state at time of export |
| `op_children` | array | Operational child particles |
| `nop_children` | array | Non-operational child particles |
| `live_verified_signals` | object | Signals verified via live PLC queries |
| `tcp_endpoints` | array | TCP endpoint map |

## Deprecation: plc_nodes_map.json

`plc_nodes_map.json` at the project root is **deprecated** as of export `v1`. Its content has been migrated into `exports/v1/INDEX.json`.

- **Phase 1:** File is retained for backward compatibility with a deprecation header.
- **Phase 2:** File will be deleted after all consumers have migrated to `exports/*/INDEX.json`.

## Future Work (Phase 2+)

- [x] POU-level indexing (enumerate all POUs, DUTs, library refs per XML file) — **done in Phase 2**
- [x] POU interface/variable extraction (VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR, VAR_GLOBAL, return types) — **done in Phase 2.5**
- [ ] Automated XML export via CODESYS scripting (no manual IDE steps)
- [ ] Diff tooling to compare XML between export versions
- [ ] Delete `plc_nodes_map.json`
- [ ] CI validation that MANIFEST.json matches actual XML files in the directory

---

# Phase 2: XML POU Indexing & PROJECT_MAP

## Purpose

Phase 2 adds automated parsing of the PLCopenXML export files to produce a structured index of all POUs, DUTs, and library references. This enables exploring the codebase structure without manually opening raw XML files in an editor or the CODESYS IDE.

## Generated Artifacts

Running the Phase 2 indexer on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `POU_INDEX.json` | Structured JSON index of every POU, DUT, and library reference across all XML files. |
| `PROJECT_MAP.md` | Human-readable markdown map of the codebase structure, organized by file. |

The indexer also updates:

| File | Update |
|---|---|
| `MANIFEST.json` | Adds `total_pou_count` and `total_dut_count` fields derived from XML parsing. |
| `INDEX.json` | Adds `phase2_artifacts` section referencing the new generated files. |

## POU_INDEX.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `summary.total_files` | integer | Number of XML files indexed |
| `summary.total_pous` | integer | Total POU count across all files |
| `summary.total_duts` | integer | Total DUT count across all files |
| `summary.total_libraries` | integer | Count of unique library references |
| `summary.pou_types` | object | POU type breakdown (e.g., `functionBlock`, `function`) |
| `summary.dut_base_types` | object | DUT base type breakdown |
| `unique_libraries` | array | Sorted list of all unique library names |
| `files[]` | array | Per-file detail (see below) |

### Per-file entry (`files[]`)

| Field | Type | Description |
|---|---|---|
| `filename` | string | XML filename |
| `name` | string | Content header name |
| `version` | string | Content header version |
| `organization` | string | Content header organization |
| `pou_count` | integer | Number of POUs in this file |
| `dut_count` | integer | Number of DUTs in this file |
| `library_count` | integer | Number of library references |
| `pous[]` | array | List of POUs with `name`, `pou_type`, optional `methods`/`properties`, and optional `interface` (Phase 2.5) |
| `duts[]` | array | List of DUTs with `name`, `base_type` |
| `libraries[]` | array | List of library refs with `name`, `namespace`, `system_library`, `link_all` |

## Running the Indexer

### From the project root

```bash
python scripts/index_xml.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-manifest-update` | Skip updating MANIFEST.json with POU/DUT counts. |
| `--no-index-update` | Skip updating INDEX.json with Phase 2 artifact references. |

### Re-indexing after a new export

After creating a new export (e.g., `v2`), run:

```bash
python scripts/index_xml.py exports/v2
```

This will generate `POU_INDEX.json` and `PROJECT_MAP.md` in the export directory and update the manifest/index files.

## v1 Index Summary

| Metric | Value |
|---|---|
| XML files | 9 |
| Total POUs | 495 |
| Total DUTs | 146 |
| Unique library references | 44 |
| POU types | functionBlock=431, function=64 |
| POUs with interface info | 412 |
| Total interface variables | 1780 |

---

# Phase 2.5: POU Interface & Variable Extraction

## Purpose

Phase 2.5 extends the Phase 2 XML indexer to extract POU interface information — the
`VAR_INPUT`, `VAR_OUTPUT`, `VAR_IN_OUT`, `VAR`, `VAR_GLOBAL`, and function return type
declarations that define what each POU exposes and depends on.

This enables answering questions like:
- "What does this FB expose?" — check `VAR_OUTPUT` and `VAR_INPUT` in `POU_INDEX.json`.
- "Which POU uses this type?" — search the `type` field across all interface variables.
- "What inputs/outputs does this parser/server have?" — look up the POU by name and read its interface.

## What Changed

### POU_INDEX.json

Each POU entry now includes an optional `interface` object when the POU has declared
interface variables. The interface object uses IEC 61131-3 category keys:

| Key | IEC Section | Description |
|---|---|---|
| `VAR_INPUT` | `VAR_INPUT` | Input parameters (passed by value) |
| `VAR_OUTPUT` | `VAR_OUTPUT` | Output parameters (written by the POU) |
| `VAR_IN_OUT` | `VAR_IN_OUT` | Bidirectional parameters (passed by reference) |
| `VAR` | `VAR` | Local/instance variables |
| `VAR_GLOBAL` | `VAR_GLOBAL` | Global variables accessible by the POU |
| `VAR_TEMP` | `VAR_TEMP` | Temporary variables (not retained) |
| `VAR_EXTERNAL` | `VAR_EXTERNAL` | External variable references |
| `returnType` | (Function only) | Return type string for Function POUs |

Each variable entry within a category contains:

| Field | Type | Description |
|---|---|---|
| `name` | string | Variable name |
| `type` | string | Human-readable type (e.g., `BOOL`, `ControllerMotor`, `ARRAY [1..8] OF t_metric_ptr`) |
| `initial_value` | string (optional) | Initial value if declared (e.g., `FALSE`, `0`) |

### Summary additions

The `summary` object now includes:

| Field | Type | Description |
|---|---|---|
| `pous_with_interface` | integer | Count of POUs that have at least one interface variable |
| `total_interface_variables` | integer | Total count of interface variables across all POUs |
| `interface_variable_categories` | object | Breakdown by category (e.g., `{"VAR_INPUT": 252, "VAR": 1518}`) |

### PROJECT_MAP.md

The POU table now includes an **Interface** column showing a compact summary:
- `VAR_INPUT=3, VAR=5` — 3 input vars, 5 local vars
- `VAR_INPUT=2, VAR_OUTPUT=1` — 2 inputs, 1 output
- `-> BOOL` — function return type
- `—` — no interface variables declared

A new **Interface Variable Categories** summary table is added to the top-level summary.

## Running the Indexer

No changes to the command-line interface. Run as before:

```bash
python scripts/index_xml.py exports/v1
```

## v1 Interface Summary

| Category | Variables |
|---|---|
| VAR | 1518 |
| VAR_INPUT | 252 |
| VAR_GLOBAL | 6 |
| VAR_OUTPUT | 4 |

## Limitations (updated)

1. **No method/property body parsing** — The indexer enumerates method and property names but does not parse their implementation code.
2. **No method/property interface parsing** — Method and property interface sections (their own VAR_INPUT/VAR_OUTPUT/etc.) are not extracted. Only the top-level POU interface is captured.
3. **No cross-reference resolution in Phase 2/2.5** — Library references are listed but not resolved to their defining XML files. Type names in variables are strings, not resolved references. **Resolved in Phase 3.**
4. **No program-type POUs** — The current export contains only `functionBlock` and `function` POUs; `program` types would be captured if present.
5. **Namespace-prefixed library names** — Libraries with `#` prefix (e.g., `#Standard`) indicate unresolved placeholder references in the CODESYS project.
6. **VAR_IN_OUT and VAR_TEMP not present in v1 exports** — These categories are supported by the parser but did not appear in the v1 export set.

---

# Phase 3: Cross-Reference Resolution & Dependency Analysis

## Purpose

Phase 3 builds a dependency/cross-reference layer on top of the `POU_INDEX.json` produced by Phase 2/2.5. It resolves type names from POU interface variables and DUT base types against known POU/DUT definitions within the same export, producing machine-readable and human-readable dependency artifacts.

This enables answering questions like:
- **Which POUs depend on this DUT/type?** — Check `used_by` in `XREF.json`.
- **If I change this FB or type, what other objects are likely affected?** — See the Impact Analysis section in `DEPENDENCY_MAP.md`.
- **What is the dependency chain around parser/server/system objects?** — See Dependency Chains for Key Objects in `DEPENDENCY_MAP.md`.

## Generated Artifacts

Running the Phase 3 builder on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `XREF.json` | Machine-readable cross-reference data with `uses`, `used_by`, type resolution table, and unresolved references. |
| `DEPENDENCY_MAP.md` | Human-readable dependency and impact analysis map. |

The builder also updates:

| File | Update |
|---|---|
| `INDEX.json` | Adds `phase3_artifacts` section referencing the new generated files. |

## XREF.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `summary` | object | Counts (see below) |
| `uses` | object | Per-object dependency map (key: `POU:Name` or `DUT:Name`) |
| `used_by` | object | Reverse map: type name → list of objects that reference it |
| `type_resolution` | array | Table of all referenced types with resolution status |
| `unresolved` | array | List of type names that could not be resolved |

### Summary fields

| Field | Type | Description |
|---|---|---|
| `total_known_types` | integer | Count of all known POU + DUT names in the export |
| `total_pous` | integer | Total POU count (from POU_INDEX.json) |
| `total_duts` | integer | Total DUT count (from POU_INDEX.json) |
| `total_resolved_references` | integer | Count of unique type names that resolved to a known POU/DUT |
| `total_unresolved_references` | integer | Count of unique type names that did NOT resolve |
| `total_dependency_edges` | integer | Total number of (object → type) dependency edges |
| `objects_with_dependencies` | integer | Count of objects that have at least one dependency |

### Per-object entry (`uses[POU:Name]` or `uses[DUT:Name]`)

| Field | Type | Description |
|---|---|---|
| `file` | string | XML filename where the object is defined |
| `kind` | string | `"POU"` or `"DUT"` |
| `pou_type` | string (POU only) | `"functionBlock"` or `"function"` |
| `base_type` | string (DUT only) | DUT base type string |
| `types` | object | Map of type name → list of `[category, variable_name]` references |

### Type resolution entry (`type_resolution[]`)

| Field | Type | Description |
|---|---|---|
| `type` | string | The referenced type name |
| `resolved` | boolean | Whether the type was found in the known type registry |
| `defined_in` | string (if resolved) | XML filename where the type is defined |
| `kind` | string (if resolved) | `"POU"` or `"DUT"` |
| `used_by_count` | integer | Number of objects that reference this type |

## Running the Builder

### From the project root

```bash
python scripts/build_xref.py exports/v1
```

### Prerequisites

Phase 3 requires `POU_INDEX.json` to exist in the export directory. Run the Phase 2 indexer first:

```bash
python scripts/index_xml.py exports/v1
python scripts/build_xref.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-index-update` | Skip updating INDEX.json with Phase 3 artifact references. |

## Resolution Strategy

The resolver uses a **conservative, two-step** approach:

1. **Type extraction** — Complex type strings (arrays, pointers, references) are unwrapped to find the base type name. For example:
   - `ARRAY [1..8] OF t_metric_ptr` → `t_metric_ptr`
   - `POINTER TO Packer` → `Packer`
   - `REFERENCE TO t_long_string` → `t_long_string`

2. **Registry lookup** — The base type name is looked up in a registry of all known POU names and DUT names from the export. IEC 61131-3 primitives (BOOL, INT, STRING, TIME, etc.) are excluded from resolution.

### What is NOT resolved

- **IEC primitives** — BOOL, INT, REAL, STRING, TIME, etc. are built-in and never resolved.
- **External library types** — Types from CODESYS system libraries (e.g., `TON`, `SysSockHandle`) that are not defined in the exported XML files will appear as unresolved if they are not in the POU/DUT registry.
- **Struct members** — DUTs with `struct` base types list member count but not individual member types, so struct-internal dependencies are not captured.
- **Enum values** — Enum DUTs are not resolved to their constituent values.

## v1 Cross-Reference Summary

| Metric | Value |
|---|---|
| Known types (POUs + DUTs) | 633 |
| Resolved type references | 235 |
| Unresolved type references | 0 |
| Total dependency edges | 534 |
| Objects with dependencies | 316 |

### Top 5 Most-Used Types (Highest Fan-In)

| Type | Kind | Used By |
|---|---|---|
| `t_percentage` | DUT | 81 objects |
| `t_time` | DUT | 22 objects |
| `t_medium_string` | DUT | 19 objects |
| `t_timer` | DUT | 13 objects |
| `ValueObjectPercentage` | POU | 10 objects |

## Limitations

1. **Interface-only resolution** — Only POU interface variables (VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR, VAR_GLOBAL) and DUT base types are analyzed. Implementation code (method bodies, property implementations) is not parsed, so dependencies created via local variable declarations inside method bodies are not captured.
2. **No transitive dependency chains in Phase 3** — The resolver captures direct (1-hop) dependencies only. Transitive chains (A → B → C) are computed in **Phase 3.5**.
3. **No implementation-level analysis** — Dependencies that exist only in implementation code (e.g., a local variable of type `X` declared inside a method body) are not captured.
4. **Single-export scope** — Cross-references are resolved only against types defined within the same export snapshot. Types from external CODESYS libraries are not resolved.

---

# Phase 3.5: Transitive Dependency & Cascade Analysis

## Purpose

Phase 3.5 builds on the Phase 3 cross-reference graph (`XREF.json`) to compute
transitive dependency closures, impact cascades, shortest dependency paths, and
graph centrality metrics. This enables answering questions that require multi-hop
graph traversal:

- **If I change type X, what is the full cascade of affected objects?** — See
  impact cascade (reverse transitive closure) in `TRANSITIVE_CLOSURE.json` or
  the Highest-Impact Types section in `CASCADE_ANALYSIS.md`.
- **What dependency path connects A to B?** — See Notable Dependency Paths in
  `CASCADE_ANALYSIS.md` or query `transitive_closure` in `TRANSITIVE_CLOSURE.json`.
- **Which objects are the most central in the graph?** — See Centrality Rankings
  in `CASCADE_ANALYSIS.md` or the `centrality` array in `TRANSITIVE_CLOSURE.json`.

## Generated Artifacts

Running the Phase 3.5 analyzer on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `TRANSITIVE_CLOSURE.json` | Machine-readable transitive dependency data including forward closure, reverse impact cascade, centrality metrics, bridge/leaf/root classification, and notable dependency paths. |
| `CASCADE_ANALYSIS.md` | Human-readable cascade/impact analysis with ranked tables, full cascade detail for top impact types, and dependency path visualization. |

The analyzer also updates:

| File | Update |
|---|---|
| `INDEX.json` | Adds `phase3_5_artifacts` section referencing the new generated files. |

## TRANSITIVE_CLOSURE.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `summary` | object | Graph-level counts (see below) |
| `transitive_closure` | object | Forward closure: node → sorted list of all transitively-depended-on types |
| `impact_cascade` | object | Reverse closure: node → sorted list of all transitively-affected objects |
| `top_impact_types` | array | Top 30 types ranked by transitive impact count |
| `top_dependency_objects` | array | Top 30 objects ranked by transitive dependency count |
| `centrality` | array | All nodes with in-degree, out-degree, total degree, transitive impact, transitive deps |
| `notable_nodes` | object | Categorized bridge nodes, leaf nodes, and root nodes |
| `notable_paths` | array | Shortest paths from Build objects to their transitive dependencies |

### Summary fields

| Field | Type | Description |
|---|---|---|
| `total_nodes` | integer | Total unique nodes in the dependency graph |
| `total_direct_edges` | integer | Total direct (1-hop) dependency edges |
| `nodes_with_transitive_deps` | integer | Nodes that transitively depend on at least one other node |
| `nodes_with_transitive_impact` | integer | Nodes that transitively affect at least one other node |
| `max_transitive_dep_depth` | integer | Maximum transitive dependency count for any single node |
| `max_transitive_impact_count` | integer | Maximum transitive impact count for any single node |

### Centrality entry (`centrality[]`)

| Field | Type | Description |
|---|---|---|
| `node` | string | POU or DUT name |
| `in_degree` | integer | Number of objects that directly use this node (fan-in) |
| `out_degree` | integer | Number of types this node directly uses (fan-out) |
| `total_degree` | integer | in_degree + out_degree |
| `transitive_impact` | integer | Count of objects transitively affected if this node changes |
| `transitive_deps` | integer | Count of types this node transitively depends on |

### Notable nodes (`notable_nodes`)

| Key | Description |
|---|---|
| `bridges` | Nodes with both fan-in ≥ 2 and fan-out ≥ 2 (coupling points) |
| `leaves` | Nodes with fan-in > 0 but fan-out == 0 (terminal/foundation types) |
| `roots` | Nodes with fan-out > 0 but fan-in == 0 (top-level consumers) |

### Notable paths (`notable_paths[]`)

| Field | Type | Description |
|---|---|---|
| `source` | string | Starting node (typically a Build object) |
| `target` | string | Ending node (a transitive dependency) |
| `hops` | integer | Number of edges in the shortest path |
| `path` | array | Ordered list of node names from source to target |

## Running the Analyzer

### From the project root

```bash
python scripts/analyze_graph.py exports/v1
```

### Prerequisites

Phase 3.5 requires `XREF.json` to exist in the export directory. Run the full
pipeline in order:

```bash
python scripts/index_xml.py exports/v1
python scripts/build_xref.py exports/v1
python scripts/analyze_graph.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-index-update` | Skip updating INDEX.json with Phase 3.5 artifact references. |

## Analysis Approach

### Transitive Closure (Forward)

For each node N in the graph, a breadth-first search (BFS) follows all forward
(`uses`) edges to discover every node reachable from N. The result is the set of
all types that N transitively depends on, at any depth.

### Impact Cascade (Reverse)

For each node N, a BFS follows all reverse (`used_by`) edges to discover every
node that transitively depends on N. This represents the full blast radius of a
change to N.

### Shortest Paths

BFS from a source node to a target node finds the minimum-hop dependency chain
connecting them. Paths are computed for Build objects to their key transitive
dependencies.

### Centrality

- **In-degree (fan-in):** How many objects directly reference this node.
- **Out-degree (fan-out):** How many types this object directly references.
- **Total degree:** Sum of in-degree and out-degree.
- **Transitive impact:** Size of the reverse transitive closure.
- **Transitive dependencies:** Size of the forward transitive closure.

### Node Classification

- **Bridge nodes:** Have both significant fan-in and fan-out. These are
  architectural coupling points — changes propagate in both directions.
- **Leaf nodes:** Used by others but depend on nothing (within the project graph).
  These are foundation types (often DUTs like `t_percentage`).
- **Root nodes:** Depend on others but are not used by anything else. These are
  typically top-level composition wrappers (e.g., `*Build` objects).

## v1 Transitive Analysis Summary

| Metric | Value |
|---|---|
| Total graph nodes | 432 |
| Total direct edges | 534 |
| Nodes with transitive deps | 316 |
| Nodes with transitive impact | 235 |
| Max transitive dep count | 51 |
| Max transitive impact count | 102 |

### Top 5 Highest-Impact Types

| Type | Direct Users | Transitive Impact |
|---|---|---|
| `t_percentage` | 81 | 102 |
| `t_medium_string` | 19 | 33 |
| `t_time` | 21 | 33 |
| `t_ms_time` | 5 | 26 |
| `ValueObjectPercentage` | 10 | 20 |

### Top 5 Most-Dependent Objects

| Object | Direct Deps | Transitive Deps |
|---|---|---|
| `SystemBuild` | 8 | 51 |
| `PackChannelUInterface` | 9 | 34 |
| `SystemApollo` | 12 | 33 |
| `UInterfaceDualRadioCabin` | 2 | 26 |
| `UInterfaceDualRadio` | 1 | 25 |

### Key Bridge Nodes

| Node | Fan-In | Fan-Out |
|---|---|---|
| `Movement` | 5 | 8 |
| `ControllerRotaryEncoderRange` | 4 | 5 |
| `ControllerMotor` | 4 | 3 |
| `Particle` | 2 | 5 |
| `UInterfaceCabinApollo` | 2 | 5 |

## Limitations

1. **Interface-only scope inherited from Phase 3** — Transitive analysis is only
   as complete as the underlying `uses` graph, which is built from POU interface
   variables and DUT base types. Implementation-level dependencies are not captured.
2. **No weighted edges** — All dependency edges are treated equally. A variable
   of type X counts the same whether it is a single VAR_INPUT or ten VAR locals.
3. **No cycle detection reporting** — The BFS-based traversal handles cycles
   correctly (no infinite loops), but cycles are not explicitly reported.
4. **Single-export scope** — Analysis is limited to types defined within the same
   export snapshot. External library types are not resolved.
5. **Path queries are limited** — Notable paths are pre-computed for Build objects
   only. Arbitrary A→B path queries require manual use of the `shortest_path`
   function or inspection of `transitive_closure` data.

---

# Phase 4: Implementation-Level Dependency Extraction

## Purpose

Phase 4 extends the dependency analysis beyond interface declarations (Phase 3)
into **ST (Structured Text) implementation bodies** — method bodies, property
accessors, and POU bodies. This captures **behavioral** dependencies: how code
actually *uses* other objects at runtime, not just what types it declares.

This enables answering questions like:
- **What code-level objects does this FB/function actually use?** — See per-POU
  implementation detail in `IMPL_DEPENDENCY_MAP.md` or `IMPL_DEPS.json`.
- **Which dependencies are structural vs behavioral?** — Compare Phase 3
  (`XREF.json`, `DEPENDENCY_MAP.md`) with Phase 4 (`IMPL_DEPS.json`,
  `IMPL_DEPENDENCY_MAP.md`). The "Structural vs Behavioral Dependencies" table
  in `IMPL_DEPENDENCY_MAP.md` provides a direct comparison.
- **If I change this parser/helper/type, what implementation-level impact might
  exist?** — See the Implementation Impact Analysis section in
  `IMPL_DEPENDENCY_MAP.md` and the `impl_used_by` map in `IMPL_DEPS.json`.
- **Which types are used in code but never declared in interfaces?** — See the
  "Types Referenced ONLY in Implementation" section.

## Generated Artifacts

Running the Phase 4 extractor on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `IMPL_DEPS.json` | Machine-readable implementation-level dependency data with per-POU FB calls, method calls, property accesses, type casts, and general implementation references. |
| `IMPL_DEPENDENCY_MAP.md` | Human-readable implementation dependency analysis with structural vs behavioral comparison, impl-only types, per-POU detail, and impact analysis. |

The extractor also updates:

| File | Update |
|---|---|
| `INDEX.json` | Adds `phase4_artifacts` section referencing the new generated files. |

## IMPL_DEPS.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `summary` | object | Counts (see below) |
| `impl_deps` | object | Per-POU implementation dependency data (key: `POU:Name`) |
| `impl_used_by` | object | Reverse map: type name → list of POUs that reference it in implementation |
| `top_impl_referenced_types` | array | Top 50 types ranked by implementation reference count |
| `impl_only_types` | array | Types referenced in implementation but NOT in any interface |

### Summary fields

| Field | Type | Description |
|---|---|---|
| `total_xml_files_scanned` | integer | Number of XML files scanned for ST bodies |
| `total_bodies_analyzed` | integer | Total ST code bodies analyzed (POU bodies + methods + property accessors) |
| `total_pous_with_impl_deps` | integer | POUs that have at least one implementation-level reference |
| `total_fb_calls_found` | integer | Total unique FB/function calls found across all bodies |
| `total_method_calls_found` | integer | Total unique method call targets found |
| `total_property_accesses_found` | integer | Total unique property access targets found |
| `total_type_casts_found` | integer | Total unique type cast/conversion references found |
| `total_impl_refs_found` | integer | Total unique general implementation references found |
| `total_impl_referenced_types` | integer | Count of unique types referenced in implementation |
| `impl_only_types_count` | integer | Count of types referenced ONLY in implementation (not in any interface) |

### Per-POU entry (`impl_deps[POU:Name]`)

| Field | Type | Description |
|---|---|---|
| `file` | string | XML filename where the POU is defined |
| `kind` | string | Always `"POU"` |
| `pou_type` | string | `"functionBlock"` or `"function"` |
| `total_bodies` | integer | Number of ST bodies analyzed for this POU |
| `fb_calls` | array | Sorted list of FB/function names called in implementation |
| `method_calls` | array | Sorted list of object names that have methods called on them |
| `property_accesses` | array | Sorted list of object names that have properties accessed |
| `type_casts` | array | Sorted list of type names used in casts/conversions |
| `impl_refs` | array | Sorted list of all known type names referenced in implementation |
| `body_details` | array | Per-body breakdown with context and references |

### Body detail entry (`body_details[]`)

| Field | Type | Description |
|---|---|---|
| `context` | string | Body context (e.g., `"POU:body"`, `"Method:operator"`, `"Property:Active:GetAccessor"`) |
| `fb_calls` | array | FB/function calls in this body |
| `method_calls` | array | Method call targets in this body |
| `property_accesses` | array | Property access targets in this body |
| `type_casts` | array | Type casts in this body |
| `impl_refs` | array | All known type references in this body |

## Running the Extractor

### From the project root

```bash
python scripts/extract_impl_deps.py exports/v1
```

### Prerequisites

Phase 4 requires `POU_INDEX.json` to exist in the export directory. It also
benefits from `XREF.json` (to distinguish interface-only vs impl-only types).
Run the full pipeline in order:

```bash
python scripts/index_xml.py exports/v1
python scripts/build_xref.py exports/v1
python scripts/analyze_graph.py exports/v1
python scripts/extract_impl_deps.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-index-update` | Skip updating INDEX.json with Phase 4 artifact references. |

## Extraction Approach

### ST Code Extraction

The extractor parses each XML file and extracts ST code from:
1. **POU bodies** — `<body><ST><xhtml>...</xhtml></ST></body>`
2. **Method bodies** — Within `<data name="...method">` elements
3. **Property accessors** — Within `<SetAccessor>` and `<GetAccessor>` elements

HTML entities (`&lt;`, `&gt;`, `&amp;`, etc.) are decoded before analysis.

### Pattern-Based Reference Extraction

Five categories of references are extracted using regex pattern matching:

| Category | Pattern | Example |
|---|---|---|
| FB/function calls | `identifier(` | `lTimer(IN:=TRUE, PT:=T#100ms)` → `TON` |
| Method calls | `identifier.identifier(` | `lHandler.initialize()` → `lHandler` |
| Property accesses | `identifier.identifier` (no `(`) | `x := obj.Value` → `obj` |
| Type casts | `TypeName(expression)` | `INT_TO_UINT(lng)` → `INT_TO_UINT` |
| Impl refs | Any known type name as word | `SystemState` appearing anywhere |

### Filtering

- **IEC primitives** (BOOL, INT, STRING, etc.) are excluded.
- **Standard library FBs** (TON, CTU, R_TRIG, etc.) are excluded from project
  dependency graphs but tracked in the raw analysis.
- **IEC keywords** (IF, FOR, WHILE, etc.) are excluded.
- Only references that match known POU/DUT names from `POU_INDEX.json` are
  included in the final output.

### Structural vs Behavioral Distinction

Phase 4 cross-references its findings against Phase 3's `XREF.json` to identify:
- **Interface-derived dependencies** — Types declared in VAR_INPUT, VAR_OUTPUT,
  VAR, etc. (captured by Phase 3).
- **Implementation-derived dependencies** — Types found in ST code bodies that
  are NOT declared in any interface. These are listed in `impl_only_types`.

## v1 Implementation Dependency Summary

| Metric | Value |
|---|---|
| XML files scanned | 9 |
| ST bodies analyzed | 3,428 |
| POUs with impl-level deps | 462 |
| FB/function calls found | 1,129 |
| Method calls found | 921 |
| Property accesses found | 1,552 |
| Type casts found | 937 |
| Implementation refs found | 636 |
| Types referenced in impl | 173 |
| Types referenced ONLY in impl | 122 |

### Top 10 Most-Referenced Types in Implementation

| Type | Kind | Impl References |
|---|---|---|
| `SystemState` | POU | 38 |
| `TypeHandlerEnum` | POU | 28 |
| `t_enum_option_definition` | DUT | 28 |
| `UInterface` | POU | 23 |
| `strcmp` | POU | 23 |
| `Active` | POU | 20 |
| `CANOpenMasterDriveApollo` | POU | 17 |
| `Spreader` | POU | 16 |
| `System` | POU | 13 |
| `BMS` | POU | 13 |

### Top 10 Types Referenced ONLY in Implementation

| Type | Kind | Used By (Impl) |
|---|---|---|
| `SystemState` | POU | 38 |
| `TypeHandlerEnum` | POU | 28 |
| `strcmp` | POU | 23 |
| `Active` | POU | 20 |
| `BMS` | POU | 13 |
| `Cycle` | POU | 13 |
| `System` | POU | 13 |
| `OperatingMode` | POU | 12 |
| `PLC` | POU | 10 |
| `UMFS` | POU | 10 |

## Limitations

1. **Regex-based extraction** — References are found via pattern matching, not
   a full ST parser. This means:
   - False positives are possible (e.g., a type name appearing in a comment or
     string literal may be counted as a reference).
   - False negatives are possible (e.g., indirect references through dynamic
     dispatch or reflection-like patterns may be missed).
   - The extraction is **conservative**: it only reports references that match
     known POU/DUT names.
2. **No data-flow analysis** — The extractor identifies *which* types are
   referenced, but not *how* they are used (read vs write, conditional vs
   unconditional, etc.).
3. **No call-graph resolution** — Method calls are recorded as object references,
   but the specific method name is not resolved to its defining type.
4. **Single-export scope** — Analysis is limited to types defined within the same
   export snapshot. External library types (CODESYS system libraries) are not
   resolved.
5. **No weighting** — All references are treated equally regardless of frequency
   within a body or across bodies.
6. **HTML entity decoding** — ST code is extracted from XHTML-wrapped XML
   content. While common entities are decoded, unusual encodings may not be
   handled correctly.

---

# Phase 4.5: Unified Dependency Graph

## Purpose

Phase 4.5 merges the **interface-derived** dependency graph (Phase 3 / `XREF.json`)
and the **implementation-derived** dependency graph (Phase 4 / `IMPL_DEPS.json`)
into a single machine-readable graph with **provenance tracking** on every edge.

This enables answering questions that require both structural and behavioral context:
- **Show me all dependencies of object X, classified by source.** — See per-object
  entries in `UNIFIED_DEPS.json` or the Key Object Analysis section in
  `UNIFIED_DEPENDENCY_MAP.md`.
- **Which impacts come only from implementation and not declarations?** — See the
  Implementation-Only Impact section in `UNIFIED_DEPENDENCY_MAP.md` or the
  `impl_only_types` array in `UNIFIED_DEPS.json`.
- **What is the full dependency picture around parser/server/system objects?** —
  See the Key Object Analysis section in `UNIFIED_DEPENDENCY_MAP.md`, which
  provides a unified view with provenance-classified edges for each key object.
- **Which edges are confirmed by both interface and implementation?** — See the
  `provenance_summary.both` array in `UNIFIED_DEPS.json`.

## Generated Artifacts

Running the Phase 4.5 unifier on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `UNIFIED_DEPS.json` | Machine-readable unified dependency graph with provenance on every edge, combined transitive analysis, impl-only/interface-only type classification, and per-object unified views. |
| `UNIFIED_DEPENDENCY_MAP.md` | Human-readable unified dependency map with structural vs behavioral comparison, impl-only type discovery, key object analysis (parser/server/system/etc.), and combined impact rankings. |

The unifier also updates:

| File | Update |
|---|---|
| `INDEX.json` | Adds `phase4_5_artifacts` section referencing the new generated files. |

## UNIFIED_DEPS.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `summary` | object | Graph-level counts (see below) |
| `edges` | array | All unified edges with provenance (see below) |
| `provenance_summary` | object | Edges grouped by provenance bucket |
| `impl_only_types` | array | Types referenced ONLY in implementation |
| `interface_only_types` | array | Types referenced ONLY in interface |
| `combined_centrality` | array | Top 50 nodes ranked by combined degree |
| `key_objects` | object | Detailed analysis of parser/server/system/etc. objects |
| `per_object` | object | Per-object unified dependency views |

### Summary fields

| Field | Type | Description |
|---|---|---|
| `total_nodes` | integer | Total unique nodes in the unified graph |
| `total_unified_edges` | integer | Total edges after merging (deduplicated by source+target) |
| `interface_only_edges` | integer | Edges found only in interface declarations |
| `implementation_only_edges` | integer | Edges found only in implementation bodies |
| `edges_in_both` | integer | Edges confirmed by both sources |
| `total_interface_edges` | integer | Total interface edges (interface_only + both) |
| `total_implementation_edges` | integer | Total implementation edges (impl_only + both) |
| `impl_only_type_count` | integer | Types referenced only in implementation |
| `interface_only_type_count` | integer | Types referenced only in interface |
| `nodes_with_transitive_deps` | integer | Nodes that transitively depend on at least one other |
| `nodes_with_transitive_impact` | integer | Nodes that transitively affect at least one other |
| `max_transitive_dep_count` | integer | Maximum transitive dependency count for any node |
| `max_transitive_impact_count` | integer | Maximum transitive impact count for any node |

### Edge entry (`edges[]`)

| Field | Type | Description |
|---|---|---|
| `source` | string | Source object name (POU or DUT) |
| `target` | string | Target type name |
| `provenance` | string | `"interface"`, `"implementation"`, or `"both"` |
| `source_kind` | string | `"POU"` or `"DUT"` |
| `source_file` | string | XML filename where source is defined |
| `interface_categories` | array | Interface context (e.g., `["VAR", "lBMSA"]`) — empty if impl-only |
| `implementation_categories` | array | Implementation categories (e.g., `["fb_call", "impl_ref"]`) — empty if interface-only |

### Provenance model

Every edge in the unified graph carries a `provenance` field:

| Provenance | Meaning |
|---|---|
| `interface` | The dependency exists only in interface declarations (VAR_INPUT, VAR_OUTPUT, VAR, etc.) |
| `implementation` | The dependency exists only in ST implementation bodies (FB calls, method calls, property accesses, type casts, impl refs) |
| `both` | The same (source, target) pair appears in both interface and implementation — the dependency is structurally declared AND behaviorally used |

### Combined centrality entry (`combined_centrality[]`)

| Field | Type | Description |
|---|---|---|
| `node` | string | Node name |
| `kind` | string | `"POU"` or `"DUT"` |
| `interface_fan_in` | integer | Objects that declare this type in their interface |
| `impl_fan_in` | integer | Objects that reference this type in implementation |
| `interface_fan_out` | integer | Types this object declares in its interface |
| `impl_fan_out` | integer | Types this object references in implementation |
| `total_fan_in` | integer | Combined fan-in (unique sources across both graphs) |
| `total_fan_out` | integer | Combined fan-out (unique targets across both graphs) |
| `total_degree` | integer | total_fan_in + total_fan_out |
| `transitive_impact` | integer | Objects transitively affected in the unified graph |
| `transitive_deps` | integer | Types transitively depended on in the unified graph |

### Key object entry (`key_objects[Name]`)

| Field | Type | Description |
|---|---|---|
| `kind` | string | `"POU"` or `"DUT"` |
| `defined_in` | string | XML filename |
| `interface_dep_count` | integer | Direct interface dependencies |
| `impl_dep_count` | integer | Direct implementation dependencies |
| `interface_used_by_count` | integer | Interface fan-in |
| `impl_used_by_count` | integer | Implementation fan-in |
| `direct_deps` | array | Per-edge detail with provenance and categories |
| `transitive_dep_count` | integer | Transitive dependency count |
| `used_by` | array | Direct users with provenance |
| `transitive_impact_count` | integer | Transitive impact count |

## Running the Unifier

### From the project root

```bash
python scripts/unify_deps.py exports/v1
```

### Prerequisites

Phase 4.5 requires `XREF.json` (Phase 3), `IMPL_DEPS.json` (Phase 4), and
`POU_INDEX.json` (Phase 2) to exist in the export directory. Run the full
pipeline in order:

```bash
python scripts/index_xml.py exports/v1
python scripts/build_xref.py exports/v1
python scripts/extract_impl_deps.py exports/v1
python scripts/unify_deps.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-index-update` | Skip updating INDEX.json with Phase 4.5 artifact references. |

## v1 Unified Graph Summary

| Metric | Value |
|---|---|
| Total graph nodes | 1,805 |
| Total unified edges | 4,209 |
| Interface-only edges | 510 |
| Implementation-only edges | 3,675 |
| Edges in both sources | 24 |
| Types referenced ONLY in impl | 1,341 |
| Types referenced ONLY in interface | 184 |
| Max transitive impact | 273 |
| Max transitive deps | 922 |

### Top 10 Combined Centrality (by total degree)

| Rank | Node | Kind | IF Fan-In | Impl Fan-In | Total Degree | Trans. Impact |
|---|---|---|---|---|---|---|
| 1 | `gCodeErrorHandler` | — | 0 | 0 | 123 | 251 |
| 2 | `IF` | — | 0 | 0 | 117 | 273 |
| 3 | `ControllerMotor` | POU | 4 | 6 | 96 | 42 |
| 4 | `__ISVALIDREF` | — | 0 | 0 | 90 | 237 |
| 5 | `SystemState` | POU | 0 | 37 | 82 | 156 |
| 6 | `t_percentage` | DUT | 81 | 0 | 81 | 134 |
| 7 | `ADR` | — | 0 | 0 | 72 | 205 |
| 8 | `PLC` | POU | 0 | 10 | 64 | 156 |
| 9 | `matchOption` | — | 0 | 0 | 59 | 214 |
| 10 | `SteerMovement` | POU | 1 | 0 | 58 | 1 |

### Key Observations from v1

1. **Implementation dominates the graph** — 3,675 of 4,209 edges (87%) come only
   from implementation scanning. Interface-only analysis captures just 12% of the
   total dependency picture.
2. **24 edges confirmed by both sources** — These are the most reliable
   dependencies: structurally declared AND behaviorally used.
3. **1,341 types referenced only in implementation** — Many of these are local
   variable names, IEC keywords matched as identifiers, or conversion functions.
   The impl-only list includes both genuine project types and regex false positives.
4. **SystemState, PLC, System, Cycle** — These core system objects have significant
   implementation fan-in (37, 10, 13, 13 respectively) but minimal or zero interface
   fan-in, meaning their impact is almost entirely behavioral.
5. **t_percentage remains the top interface fan-in** — 81 objects declare it as a
   variable type, confirming its role as the most widely-used project DUT.

## Limitations

1. **Inherited from Phase 3** — Interface-derived edges are limited to POU/DUT
   interface variables. Struct member types, enum values, and external library
   types are not resolved.
2. **Inherited from Phase 4** — Implementation-derived edges use regex pattern
   matching, which can produce false positives (type names in comments/strings)
   and false negatives (indirect references).
3. **No edge weighting** — All edges are treated equally regardless of reference
   frequency or semantic importance.
4. **Local variable names as targets** — Implementation scanning may capture local
   variable names (e.g., `lMovement`, `lSpreader`) as dependency targets. These
   are not project-defined types but appear as impl-only edges.
5. **IEC keyword false positives** — Some IEC keywords (e.g., `IF`, `CASE`, `MAX`,
   `MIN`) match known type names or appear in ST code patterns and are captured
   as impl-only edges. These are not genuine dependencies.
6. **Single-export scope** — Analysis is limited to types defined within the same
   export snapshot. External CODESYS library types are not resolved.
 7. **Transitive analysis is unweighted** — BFS traversal treats all edges equally,
    so a single impl_ref edge has the same transitive reach as an interface-declared
    variable edge.

---

# Phase 5: Graph Cleaning & Confidence Scoring

## Purpose

Phase 5 applies a **practical cleaning and scoring layer** over the Phase 4.5
unified dependency graph. It removes known false positives that arise from
regex-based implementation scanning and assigns confidence scores to every
surviving edge based on provenance and evidence strength.

This enables answering questions with calibrated trust:
- **What are the most reliable dependencies in the graph?** — See high-confidence
  edges (provenance = "both") in `CLEAN_DEPENDENCY_MAP.md`.
- **How much noise was in the unified graph?** — See the Filtering Results table
  showing 3,200 edges removed (76% reduction).
- **Which types are the most impactful in the cleaned graph?** — See the Top Nodes
  by Degree and Clean Graph Impact Analysis sections.
- **Should I trust this dependency?** — Check the confidence score: high (0.95+),
  medium (0.70–0.94), or low (0.30–0.69).

## Generated Artifacts

Running the Phase 5 cleaner on an export directory (e.g., `exports/v1`) produces:

| Artifact | Description |
|---|---|
| `CLEAN_DEPS.json` | Machine-readable cleaned dependency graph with false positives removed and confidence scores on every edge. |
| `CLEAN_DEPENDENCY_MAP.md` | Human-readable report summarizing filtering results, confidence distribution, signal improvement metrics, and the cleaned dependency picture. |

The cleaner also updates:

| File | Update |
|---|---|
| `INDEX.json` | Adds `phase5_artifacts` section referencing the new generated files. |

## CLEAN_DEPS.json Schema

| Field | Type | Description |
|---|---|---|
| `generated` | string | ISO 8601 timestamp |
| `description` | string | Human-readable description |
| `source` | string | Source artifact (UNIFIED_DEPS.json) |
| `summary` | object | Graph-level counts and filter statistics (see below) |
| `confidence_summary` | object | Confidence distribution with descriptions |
| `top_nodes_by_degree` | array | Top 50 nodes ranked by degree in the clean graph |
| `edges` | array | All clean edges with confidence scores (see below) |

### Summary fields

| Field | Type | Description |
|---|---|---|
| `total_nodes` | integer | Total unique nodes in the clean graph |
| `total_edges` | integer | Total edges after filtering |
| `edges_by_provenance` | object | Edge counts grouped by provenance |
| `edges_by_confidence` | object | Edge counts grouped by confidence label |
| `filter_stats` | object | Filtering statistics (see below) |

### Filter statistics (`filter_stats`)

| Field | Type | Description |
|---|---|---|
| `total_input_edges` | integer | Edges in the input (Phase 4.5) graph |
| `total_clean_edges` | integer | Edges surviving after filtering |
| `total_filtered` | integer | Edges removed as false positives |
| `filter_reasons` | object | Breakdown of removed edges by filter category |

### Edge entry (`edges[]`)

| Field | Type | Description |
|---|---|---|
| `source` | string | Source object name (POU or DUT) |
| `target` | string | Target type name |
| `provenance` | string | `"interface"`, `"implementation"`, or `"both"` |
| `confidence` | number | Confidence score (0.0–1.0) |
| `confidence_label` | string | `"high"`, `"medium"`, or `"low"` |
| `source_kind` | string | `"POU"` or `"DUT"` |
| `source_file` | string | XML filename where source is defined |
| `interface_categories` | array | Interface context (e.g., `["VAR", "lBMSA"]`) |
| `implementation_categories` | array | Implementation categories (e.g., `["fb_call", "impl_ref"]`) |

## Running the Cleaner

### From the project root

```bash
python scripts/clean_graph.py exports/v1
```

### Prerequisites

Phase 5 requires `UNIFIED_DEPS.json` (Phase 4.5) and `POU_INDEX.json` (Phase 2)
to exist in the export directory. Run the full pipeline in order:

```bash
python scripts/index_xml.py exports/v1
python scripts/build_xref.py exports/v1
python scripts/extract_impl_deps.py exports/v1
python scripts/unify_deps.py exports/v1
python scripts/clean_graph.py exports/v1
```

### Options

| Flag | Description |
|---|---|
| `--no-index-update` | Skip updating INDEX.json with Phase 5 artifact references. |

## Filtering Rules

Edges are removed if the **target** matches any of these criteria:

| Filter | Description | Example Targets Removed |
|---|---|---|
| `self_reference` | Source equals target | `Active` → `Active` |
| `iec_keyword` | IEC 61131-3 language keyword | `IF`, `CASE`, `AND`, `OR`, `FOR` |
| `conversion_function` | Standard type conversion (`*_TO_*`) | `INT_TO_REAL`, `BOOL_TO_STRING` |
| `standard_library` | Standard library FB/function | `TON`, `MAX`, `MIN`, `ADR`, `strcmp` |
| `local_variable_name` | Matches local var naming (l*, r*, etc.) and not in type registry | `lMovement`, `rValue`, `tTimer` |
| `common_member_name` | Common method/property name, not a project type | `trigger`, `reset`, `configure` |
| `unknown_type` | Not found in POU_INDEX.json registry | Any name not in known POU/DUT list |

## Confidence Scoring Model

Every surviving edge receives a confidence score based on provenance and
evidence strength:

| Label | Score Range | Criteria |
|---|---|---|
| **high** | 0.95–1.00 | Provenance = "both" (confirmed by interface AND implementation) |
| **medium** | 0.70–0.94 | Provenance = "interface" (compiler-enforced declaration) |
| **low** | 0.30–0.69 | Provenance = "implementation" (regex-inferred) |

Within the **low** tier, sub-scoring applies based on implementation category:

| Sub-score | Categories | Rationale |
|---|---|---|
| 0.65 | fb_call + impl_ref | Strong behavioral signal |
| 0.60 | fb_call alone | FB invocation is a clear dependency |
| 0.55 | method_call + property_access | Object usage pattern |
| 0.50 | method_call alone | Method invocation on an object |
| 0.40 | property_access alone | Could be any member access |
| 0.35 | impl_ref alone | General reference, weak signal |
| 0.30 | type_cast alone | Weakest signal |

## v1 Clean Graph Summary

| Metric | Value |
|---|---|
| Clean graph nodes | 512 |
| Clean graph edges | 1,009 |
| Edges filtered | 3,200 (76.0%) |
| High confidence | 24 |
| Medium confidence | 510 |
| Low confidence | 475 |

### Top Filter Categories

| Reason | Edges Removed |
|---|---|
| local_variable_name | 1,070 |
| unknown_type | 1,028 |
| common_member_name | 424 |
| conversion_function | 226 |
| standard_library | 216 |
| iec_keyword | 126 |
| self_reference | 110 |

### Top 10 Nodes by Degree (Clean Graph)

| Rank | Node | Total Degree | Fan-In | Fan-Out |
|---|---|---|---|---|
| 1 | `t_percentage` | 81 | 81 | 0 |
| 2 | `SystemState` | 39 | 36 | 3 |
| 3 | `UInterface` | 29 | 24 | 5 |
| 4 | `TypeHandlerEnum` | 28 | 28 | 0 |
| 5 | `t_enum_option_definition` | 28 | 28 | 0 |
| 6 | `CANOpenMasterDriveApollo` | 22 | 17 | 5 |
| 7 | `Active` | 21 | 18 | 3 |
| 8 | `System` | 21 | 12 | 9 |
| 9 | `t_time` | 21 | 21 | 0 |
| 10 | `Spreader` | 19 | 15 | 4 |

## Limitations

1. **Conservative filtering** — The filter lists are manually curated and may
   not cover all false positive patterns. New patterns discovered in future
   exports should be added to the filter lists.
2. **Local variable heuristic** — The `l*`, `r*`, etc. prefix heuristic may
   incorrectly filter genuine project types that follow IEC naming conventions.
   The known type registry check mitigates this but is not perfect.
3. **No semantic analysis** — Filtering is based on name matching, not semantic
   understanding of the ST code. Some genuine dependencies may be removed if
   their names match filter patterns.
4. **Confidence scores are heuristic** — The scoring model is designed to be
   useful and conservative, not mathematically rigorous. Scores should be
   treated as relative indicators, not absolute probabilities.
5. **Single-export scope** — Analysis is limited to types defined within the
   same export snapshot. External CODESYS library types are not resolved.
6. **Filter lists are project-specific** — The IEC keyword, conversion function,
   and standard library lists are based on IEC 61131-3 and common CODESYS
   libraries. They may need adjustment for projects using different library sets.

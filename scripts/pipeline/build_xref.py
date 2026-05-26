"""
build_xref.py — Phase 3: Cross-reference resolution over POU_INDEX.json.

Reads an existing POU_INDEX.json (produced by scripts/index_xml.py) and builds
a dependency/cross-reference layer that resolves type names from POU interfaces
and DUT base types against known POU/DUT definitions within the same export.

Produces:
  - XREF.json          — Machine-readable cross-reference data (uses, used_by,
                         type resolution table, unresolved references)
  - DEPENDENCY_MAP.md  — Human-readable dependency/impact map

Usage:
    python scripts/build_xref.py exports/v1

This script is designed to run AFTER index_xml.py. It does NOT parse XML files
directly; it consumes the POU_INDEX.json artifact.
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone

# IEC 61131-3 primitive / built-in types that should never be resolved
# against project-defined POUs or DUTs.
PRIMITIVE_TYPES = frozenset(
    [
        # Boolean
        "BOOL",
        # Integer
        "SINT",
        "USINT",
        "INT",
        "UINT",
        "DINT",
        "UDINT",
        "LINT",
        "ULINT",
        # Floating point
        "REAL",
        "LREAL",
        # Time
        "TIME",
        "LTIME",
        "DATE",
        "LDATE",
        "TIME_OF_DAY",
        "TOD",
        "LTOD",
        "DATE_AND_TIME",
        "DT",
        "LDATE_AND_TIME",
        "LDT",
        # String
        "STRING",
        "WSTRING",
        "CHAR",
        "WCHAR",
        # Byte
        "BYTE",
        "WORD",
        "DWORD",
        "LWORD",
        # Special
        "ANY",
        "ANY_DERIVED",
        "ANY_ELEMENTARY",
        "ANY_MAGNITUDE",
        "ANY_NUM",
        "ANY_REAL",
        "ANY_INT",
        "ANY_BIT",
        "ANY_STRING",
        "ANY_DATE",
        "VOID",
    ]
)


def is_primitive(type_name):
    """Check if a type name is an IEC primitive / built-in."""
    return type_name.upper() in PRIMITIVE_TYPES


def extract_base_type_name(type_string):
    """Extract the core type name from a complex type string.

    Handles:
      - Simple names: 'ControllerBMS' -> 'ControllerBMS'
      - Arrays: 'ARRAY [1..8] OF t_metric_ptr' -> 't_metric_ptr'
      - Pointers: 'POINTER TO Packer' -> 'Packer'
      - References: 'REFERENCE TO t_long_string' -> 't_long_string'
      - Strings: 'STRING(80)' -> None (primitive)
      - Primitives: 'BOOL' -> None

    Returns the base type name string, or None if the type is primitive
    or cannot be meaningfully resolved.
    """
    if not type_string:
        return None

    t = type_string.strip()

    # Primitive check first
    if is_primitive(t):
        return None

    # STRING(n) / WSTRING(n)
    if re.match(r"^(STRING|WSTRING)(\(\d+\))?$", t, re.IGNORECASE):
        return None

    # POINTER TO <type>
    m = re.match(r"^POINTER\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return extract_base_type_name(m.group(1).strip())

    # REFERENCE TO <type>
    m = re.match(r"^REFERENCE\s+TO\s+(.+)$", t, re.IGNORECASE)
    if m:
        return extract_base_type_name(m.group(1).strip())

    # ARRAY [...] OF <type>
    m = re.match(r"^ARRAY\s+\[.+\]\s+OF\s+(.+)$", t, re.IGNORECASE)
    if m:
        return extract_base_type_name(m.group(1).strip())

    # Simple derived type name (not a primitive)
    if not is_primitive(t):
        return t

    return None


def extract_dut_base_type_name(base_type_string):
    """Extract resolvable type names from a DUT base_type string.

    DUT base_type strings in POU_INDEX.json look like:
      - 'derived' (generic — not resolvable)
      - 'enum (N values)' (not resolvable)
      - 'struct (N members)' (not resolvable from summary)
      - 'array [1..8] of t_metric_ptr' -> 't_metric_ptr'
      - 'pointer to Packer' -> 'Packer'
      - 'ControllerBMS' -> 'ControllerBMS'
      - 'STRING(80)' -> None (primitive)

    Returns a list of resolvable type name strings (may be empty).
    """
    if not base_type_string:
        return []

    bt = base_type_string.strip()

    # Non-resolvable summaries
    if bt.startswith("enum ") or bt.startswith("struct ") or bt == "derived":
        return []

    # Try to extract a base type name
    base = extract_base_type_name(bt)
    if base and not is_primitive(base):
        return [base]

    return []


def build_type_registry(pou_index):
    """Build a registry of all known type names from POUs and DUTs.

    Returns:
      - known_types: set of all known type names (POU names + DUT names)
      - type_to_file: dict mapping type name -> filename where it's defined
      - type_to_kind: dict mapping type name -> 'POU' or 'DUT'
      - type_to_pou_type: dict mapping POU name -> pou_type (functionBlock/function)
      - type_to_dut_base: dict mapping DUT name -> base_type string
    """
    known_types = set()
    type_to_file = {}
    type_to_kind = {}
    type_to_pou_type = {}
    type_to_dut_base = {}

    for file_entry in pou_index["files"]:
        filename = file_entry["filename"]

        for pou in file_entry.get("pous", []):
            name = pou["name"]
            known_types.add(name)
            type_to_file[name] = filename
            type_to_kind[name] = "POU"
            type_to_pou_type[name] = pou.get("pou_type", "unknown")

        for dut in file_entry.get("duts", []):
            name = dut["name"]
            known_types.add(name)
            type_to_file[name] = filename
            type_to_kind[name] = "DUT"
            type_to_dut_base[name] = dut.get("base_type", "unknown")

    return known_types, type_to_file, type_to_kind, type_to_pou_type, type_to_dut_base


def resolve_pou_uses(pou, known_types):
    """Resolve which known types a POU uses via its interface variables.

    Returns a dict: { type_name: [ (category, var_name), ... ] }
    """
    uses = defaultdict(list)
    interface = pou.get("interface")
    if not interface:
        return dict(uses)

    for category, vars_list in interface.items():
        if category == "returnType":
            # Function return type
            base = extract_base_type_name(vars_list)
            if base and base in known_types:
                uses[base].append(("returnType", "(return)"))
            continue

        for var in vars_list:
            var_type = var.get("type", "")
            base = extract_base_type_name(var_type)
            if base and base in known_types:
                uses[base].append((category, var["name"]))

    return dict(uses)


def resolve_dut_uses(dut, known_types):
    """Resolve which known types a DUT uses via its base_type.

    Returns a dict: { type_name: [ ("base_type", dut_name) ] }
    """
    uses = defaultdict(list)
    base_type = dut.get("base_type", "")
    resolved = extract_dut_base_type_name(base_type)
    for t in resolved:
        if t in known_types:
            uses[t].append(("base_type", dut["name"]))
    return dict(uses)


def build_xref(pou_index):
    """Build the full cross-reference data structure.

    Returns a dict with:
      - generated: timestamp
      - summary: counts
      - uses: per-POU/DUT -> list of types it uses
      - used_by: per-type -> list of POUs/DUTs that use it
      - type_resolution: table of all referenced types with resolution status
      - unresolved: list of type names that could not be resolved
    """
    known_types, type_to_file, type_to_kind, type_to_pou_type, type_to_dut_base = (
        build_type_registry(pou_index)
    )

    # Forward map: object -> types it uses
    uses_map = {}  # key: "POU:Name" or "DUT:Name"
    # Reverse map: type -> objects that use it
    used_by_map = defaultdict(list)
    # All referenced types (resolved + unresolved)
    all_referenced = set()
    unresolved_types = set()

    for file_entry in pou_index["files"]:
        filename = file_entry["filename"]

        for pou in file_entry.get("pous", []):
            key = "POU:%s" % pou["name"]
            pou_uses = resolve_pou_uses(pou, known_types)
            if pou_uses:
                uses_map[key] = {
                    "file": filename,
                    "kind": "POU",
                    "pou_type": pou.get("pou_type", "unknown"),
                    "types": {},
                }
                for type_name, refs in pou_uses.items():
                    uses_map[key]["types"][type_name] = refs
                    used_by_map[type_name].append(
                        {"object": key, "file": filename, "refs": refs}
                    )
                    all_referenced.add(type_name)

        for dut in file_entry.get("duts", []):
            key = "DUT:%s" % dut["name"]
            dut_uses = resolve_dut_uses(dut, known_types)
            if dut_uses:
                uses_map[key] = {
                    "file": filename,
                    "kind": "DUT",
                    "base_type": dut.get("base_type", "unknown"),
                    "types": {},
                }
                for type_name, refs in dut_uses.items():
                    uses_map[key]["types"][type_name] = refs
                    used_by_map[type_name].append(
                        {"object": key, "file": filename, "refs": refs}
                    )
                    all_referenced.add(type_name)

    # Build type resolution table
    type_resolution = []
    for type_name in sorted(all_referenced):
        is_resolved = type_name in known_types
        entry = {
            "type": type_name,
            "resolved": is_resolved,
        }
        if is_resolved:
            entry["defined_in"] = type_to_file.get(type_name, "unknown")
            entry["kind"] = type_to_kind.get(type_name, "unknown")
            if entry["kind"] == "POU":
                entry["pou_type"] = type_to_pou_type.get(type_name, "unknown")
            else:
                entry["base_type"] = type_to_dut_base.get(type_name, "unknown")
        else:
            unresolved_types.add(type_name)
        entry["used_by_count"] = len(used_by_map.get(type_name, []))
        type_resolution.append(entry)

    # Build used_by map (sorted, deduplicated)
    used_by_output = {}
    for type_name in sorted(used_by_map.keys()):
        users = used_by_map[type_name]
        # Deduplicate by object key
        seen = set()
        unique_users = []
        for u in users:
            if u["object"] not in seen:
                seen.add(u["object"])
                unique_users.append(u)
        used_by_output[type_name] = unique_users

    # Summary
    total_uses_edges = sum(len(entry["types"]) for entry in uses_map.values())

    xref = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": "Cross-reference data generated by scripts/build_xref.py from POU_INDEX.json.",
        "summary": {
            "total_known_types": len(known_types),
            "total_pous": pou_index["summary"]["total_pous"],
            "total_duts": pou_index["summary"]["total_duts"],
            "total_resolved_references": len(all_referenced) - len(unresolved_types),
            "total_unresolved_references": len(unresolved_types),
            "total_dependency_edges": total_uses_edges,
            "objects_with_dependencies": len(uses_map),
        },
        "uses": uses_map,
        "used_by": used_by_output,
        "type_resolution": type_resolution,
        "unresolved": sorted(unresolved_types),
    }

    return xref


def build_dependency_map(xref, pou_index):
    """Generate a human-readable DEPENDENCY_MAP.md from cross-reference data.

    Organized into sections:
      1. Summary
      2. Most-used types (highest fan-in)
      3. Most-dependent objects (highest fan-out)
      4. Unresolved references
      5. Per-object dependency detail
      6. Impact analysis: what breaks if you change X
    """
    lines = []
    lines.append("# DEPENDENCY_MAP — CODESYS PLC Cross-Reference & Impact Analysis")
    lines.append("")
    lines.append("> Auto-generated by `scripts/build_xref.py`. Do not edit manually.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = xref["summary"]
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| Known types (POUs + DUTs) | %d |" % s["total_known_types"])
    lines.append("| Total POUs | %d |" % s["total_pous"])
    lines.append("| Total DUTs | %d |" % s["total_duts"])
    lines.append("| Resolved type references | %d |" % s["total_resolved_references"])
    lines.append(
        "| Unresolved type references | %d |" % s["total_unresolved_references"]
    )
    lines.append("| Total dependency edges | %d |" % s["total_dependency_edges"])
    lines.append("| Objects with dependencies | %d |" % s["objects_with_dependencies"])
    lines.append("")

    # Most-used types (fan-in)
    lines.append("## Most-Used Types (Highest Fan-In)")
    lines.append("")
    lines.append("These types are referenced by the most other objects. Changing them")
    lines.append("has the broadest impact.")
    lines.append("")
    lines.append("| Type | Kind | Defined In | Used By Count |")
    lines.append("|---|---|---|---|")

    # Sort by used_by count descending
    sorted_types = sorted(
        xref["type_resolution"], key=lambda t: (-t["used_by_count"], t["type"])
    )
    for entry in sorted_types:
        if entry["used_by_count"] == 0:
            continue
        kind = entry.get("kind", "external")
        defined_in = entry.get("defined_in", "(external)")
        lines.append(
            "| `%s` | %s | %s | %d |"
            % (entry["type"], kind, defined_in, entry["used_by_count"])
        )
    lines.append("")

    # Most-dependent objects (fan-out)
    lines.append("## Most-Dependent Objects (Highest Fan-Out)")
    lines.append("")
    lines.append("These objects depend on the most other types. They are the most")
    lines.append("sensitive to upstream changes.")
    lines.append("")
    lines.append("| Object | Kind | File | Dependencies |")
    lines.append("|---|---|---|---|")

    sorted_objects = sorted(
        xref["uses"].items(), key=lambda kv: (-len(kv[1]["types"]), kv[0])
    )
    for key, entry in sorted_objects:
        name = key.split(":", 1)[1]
        kind = entry["kind"]
        filename = entry["file"]
        dep_count = len(entry["types"])
        lines.append("| `%s` | %s | %s | %d |" % (name, kind, filename, dep_count))
    lines.append("")

    # Unresolved references
    if xref["unresolved"]:
        lines.append("## Unresolved Type References")
        lines.append("")
        lines.append("These type names appear in POU interfaces or DUT base types but")
        lines.append("could not be resolved to a known POU or DUT within this export.")
        lines.append("They may be external library types, compiler built-ins, or types")
        lines.append("defined in XML files not included in this snapshot.")
        lines.append("")
        lines.append("| Type | Referenced By Count |")
        lines.append("|---|---|")
        for type_name in xref["unresolved"]:
            count = len(xref["used_by"].get(type_name, []))
            lines.append("| `%s` | %d |" % (type_name, count))
        lines.append("")

    # Per-object dependency detail
    lines.append("## Dependency Detail by Object")
    lines.append("")

    # Group by file
    files = pou_index["files"]
    for file_entry in files:
        filename = file_entry["filename"]
        file_objects = {k: v for k, v in xref["uses"].items() if v["file"] == filename}
        if not file_objects:
            continue

        lines.append("### %s" % filename)
        lines.append("")

        # POUs
        pou_objects = {k: v for k, v in file_objects.items() if v["kind"] == "POU"}
        if pou_objects:
            lines.append("#### POUs")
            lines.append("")
            lines.append("| POU | Type | Depends On |")
            lines.append("|---|---|---|")
            for key in sorted(pou_objects.keys()):
                entry = pou_objects[key]
                name = key.split(":", 1)[1]
                pou_type = entry.get("pou_type", "")
                deps = ", ".join("`%s`" % t for t in sorted(entry["types"].keys()))
                lines.append("| `%s` | %s | %s |" % (name, pou_type, deps))
            lines.append("")

        # DUTs
        dut_objects = {k: v for k, v in file_objects.items() if v["kind"] == "DUT"}
        if dut_objects:
            lines.append("#### DUTs")
            lines.append("")
            lines.append("| DUT | Base Type | Depends On |")
            lines.append("|---|---|---|")
            for key in sorted(dut_objects.keys()):
                entry = dut_objects[key]
                name = key.split(":", 1)[1]
                base = entry.get("base_type", "")
                deps = ", ".join("`%s`" % t for t in sorted(entry["types"].keys()))
                lines.append("| `%s` | %s | %s |" % (name, base, deps))
            lines.append("")

        lines.append("---")
        lines.append("")

    # Impact analysis section
    lines.append("## Impact Analysis")
    lines.append("")
    lines.append(
        'Use this section to answer: *"If I change X, what else is affected?"*'
    )
    lines.append("")
    lines.append("### High-Impact Types (used by 5+ objects)")
    lines.append("")

    high_impact = [e for e in sorted_types if e["used_by_count"] >= 5]
    if high_impact:
        for entry in high_impact:
            type_name = entry["type"]
            users = xref["used_by"].get(type_name, [])
            lines.append(
                "#### `%s` (%s, used by %d objects)"
                % (type_name, entry.get("kind", "external"), entry["used_by_count"])
            )
            lines.append("")
            lines.append("Defined in: `%s`" % entry.get("defined_in", "(external)"))
            lines.append("")
            lines.append("Objects that depend on this type:")
            lines.append("")
            for u in sorted(users, key=lambda x: x["object"]):
                obj_name = u["object"].split(":", 1)[1]
                ref_details = ", ".join("%s.%s" % (cat, var) for cat, var in u["refs"])
                lines.append("- `%s` (via %s)" % (obj_name, ref_details))
            lines.append("")
    else:
        lines.append("No types are used by 5 or more objects in this export.")
        lines.append("")

    # Dependency chains for key objects
    lines.append("### Dependency Chains for Key Objects")
    lines.append("")
    lines.append("Shows the direct dependency chain for objects whose names suggest")
    lines.append("core system roles (parser, server, system, etc.).")
    lines.append("")

    key_patterns = [
        "system",
        "parser",
        "server",
        "master",
        "manager",
        "handler",
        "connection",
        "channel",
        "reportable",
        "particle",
        "executor",
    ]
    key_objects = []
    for key in sorted(xref["uses"].keys()):
        name_lower = key.split(":", 1)[1].lower()
        if any(p in name_lower for p in key_patterns):
            key_objects.append(key)

    if key_objects:
        for key in key_objects:
            entry = xref["uses"][key]
            name = key.split(":", 1)[1]
            kind = entry["kind"]
            deps = sorted(entry["types"].keys())
            if deps:
                lines.append("#### `%s` (%s)" % (name, kind))
                lines.append("")
                lines.append("Direct dependencies:")
                for dep in deps:
                    dep_info = ""
                    for tr in xref["type_resolution"]:
                        if tr["type"] == dep:
                            dep_info = " (%s in %s)" % (
                                tr.get("kind", "?"),
                                tr.get("defined_in", "?"),
                            )
                            break
                    lines.append("- `%s`%s" % (dep, dep_info))
                lines.append("")
    else:
        lines.append("No key objects with dependencies found.")
        lines.append("")

    return "\n".join(lines)


def update_index_with_xref(index_path):
    """Update INDEX.json to reference Phase 3 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    idx["phase3_artifacts"] = {
        "XREF.json": "Machine-readable cross-reference data (uses, used_by, type resolution, unresolved references).",
        "DEPENDENCY_MAP.md": "Human-readable dependency and impact analysis map.",
        "generated_by": "scripts/build_xref.py",
        "description": "Phase 3: Cross-reference resolution over POU/DUT index.",
    }

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Build cross-reference data from POU_INDEX.json (Phase 3)."
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 3 artifact references.",
    )
    args = parser.parse_args()

    export_dir = os.path.normpath(args.export_dir)

    if not os.path.isdir(export_dir):
        print("ERROR: Export directory not found: %s" % export_dir, file=sys.stderr)
        sys.exit(1)

    pou_index_path = os.path.join(export_dir, "POU_INDEX.json")
    if not os.path.isfile(pou_index_path):
        print("ERROR: POU_INDEX.json not found in %s" % export_dir, file=sys.stderr)
        print(
            "Run scripts/index_xml.py first to generate POU_INDEX.json.",
            file=sys.stderr,
        )
        sys.exit(1)

    print("Loading POU_INDEX.json from %s ..." % pou_index_path)
    with open(pou_index_path, "r", encoding="utf-8") as f:
        pou_index = json.load(f)

    print("Building cross-reference data ...")
    xref = build_xref(pou_index)

    # Write XREF.json
    xref_path = os.path.join(export_dir, "XREF.json")
    with open(xref_path, "w", encoding="utf-8") as f:
        json.dump(xref, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Cross-reference data written to: %s" % xref_path)

    # Build and write DEPENDENCY_MAP.md
    dep_map = build_dependency_map(xref, pou_index)
    dep_map_path = os.path.join(export_dir, "DEPENDENCY_MAP.md")
    with open(dep_map_path, "w", encoding="utf-8") as f:
        f.write(dep_map)
    print("Dependency map written to: %s" % dep_map_path)

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_xref(index_path)
        print("INDEX.json updated with Phase 3 artifact references.")

    # Print summary
    s = xref["summary"]
    print("\nPhase 3 Summary:")
    print("  Known types (POUs + DUTs): %d" % s["total_known_types"])
    print("  Resolved type references: %d" % s["total_resolved_references"])
    print("  Unresolved type references: %d" % s["total_unresolved_references"])
    print("  Total dependency edges: %d" % s["total_dependency_edges"])
    print("  Objects with dependencies: %d" % s["objects_with_dependencies"])

    if xref["unresolved"]:
        print("\n  Top unresolved types (by reference count):")
        unresolved_with_counts = [
            (t, len(xref["used_by"].get(t, []))) for t in xref["unresolved"]
        ]
        unresolved_with_counts.sort(key=lambda x: -x[1])
        for t, count in unresolved_with_counts[:10]:
            print("    %-40s  referenced by %d object(s)" % (t, count))


if __name__ == "__main__":
    main()

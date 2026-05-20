"""
unify_deps.py — Phase 4.5: Unified Dependency Graph.

Merges the interface-derived dependency graph (Phase 3 / XREF.json) and the
implementation-derived dependency graph (Phase 4 / IMPL_DEPS.json) into a
single machine-readable graph with provenance on every edge.

Produces:
  - UNIFIED_DEPS.json              — Machine-readable unified dependency graph
                                     with provenance, edge classification, and
                                     combined transitive analysis.
  - UNIFIED_DEPENDENCY_MAP.md      — Human-readable unified dependency map
                                     with structural vs behavioral distinction,
                                     impl-only discovery, and key-object views.

Usage:
    python scripts/unify_deps.py exports/v1

This script is designed to run AFTER both build_xref.py (Phase 3) and
extract_impl_deps.py (Phase 4). It consumes XREF.json and IMPL_DEPS.json.

Provenance model:
  Every edge in the unified graph carries a "provenance" field:
    - "interface"      — Derived from VAR_INPUT/VAR_OUTPUT/VAR/etc. declarations
    - "implementation" — Derived from ST code body scanning (FB calls, method
                         calls, property accesses, type casts, impl refs)
    - "both"           — The same dependency appears in both sources

Edge categories (for implementation-derived edges):
  - "fb_call"         — FB/function invocation in ST code
  - "method_call"     — Method invocation on an object
  - "property_access" — Property read/write on an object
  - "type_cast"       — Type conversion / cast
  - "impl_ref"        — General reference to a known type in ST code
  - "var_decl"        — Interface variable declaration (VAR_INPUT, VAR, etc.)
"""

import argparse
import json
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# Data loading
# ---------------------------------------------------------------------------

def load_json(path):
    """Load a JSON file, returning None if not found."""
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Edge extraction from Phase 3 (interface-derived)
# ---------------------------------------------------------------------------

def extract_interface_edges(xref):
    """Extract interface-derived edges from XREF.json.

    Returns a list of edge dicts:
      {
        "source": str,       # POU or DUT name (bare, no prefix)
        "target": str,       # Type name (POU or DUT)
        "provenance": "interface",
        "source_kind": "POU" | "DUT",
        "source_file": str,
        "categories": [ ("VAR_INPUT", "varName"), ... ],
      }
    """
    edges = []
    uses = xref.get("uses", {})

    for obj_key, obj_data in uses.items():
        source_name = obj_key.split(":", 1)[1]
        source_kind = obj_data.get("kind", "unknown")
        source_file = obj_data.get("file", "unknown")

        for type_name, refs in obj_data.get("types", {}).items():
            edges.append({
                "source": source_name,
                "target": type_name,
                "provenance": "interface",
                "source_kind": source_kind,
                "source_file": source_file,
                "categories": refs,  # e.g. [["VAR", "lBMSA"], ...]
            })

    return edges


# ---------------------------------------------------------------------------
# Edge extraction from Phase 4 (implementation-derived)
# ---------------------------------------------------------------------------

def extract_implementation_edges(impl_data):
    """Extract implementation-derived edges from IMPL_DEPS.json.

    Returns a list of edge dicts:
      {
        "source": str,       # POU name (bare, no prefix)
        "target": str,       # Type name referenced in implementation
        "provenance": "implementation",
        "source_kind": "POU",
        "source_file": str,
        "categories": [ "fb_call", "method_call", ... ],
      }
    """
    edges = []
    impl_deps = impl_data.get("impl_deps", {})

    for obj_key, obj_data in impl_deps.items():
        source_name = obj_key.split(":", 1)[1]
        source_file = obj_data.get("file", "unknown")

        # Collect all unique targets with their categories
        target_categories = defaultdict(list)

        for ref in obj_data.get("fb_calls", []):
            target_categories[ref].append("fb_call")
        for ref in obj_data.get("method_calls", []):
            target_categories[ref].append("method_call")
        for ref in obj_data.get("property_accesses", []):
            target_categories[ref].append("property_access")
        for ref in obj_data.get("type_casts", []):
            target_categories[ref].append("type_cast")
        for ref in obj_data.get("impl_refs", []):
            target_categories[ref].append("impl_ref")

        for target, cats in target_categories.items():
            edges.append({
                "source": source_name,
                "target": target,
                "provenance": "implementation",
                "source_kind": "POU",
                "source_file": source_file,
                "categories": sorted(set(cats)),
            })

    return edges


# ---------------------------------------------------------------------------
# Edge unification
# ---------------------------------------------------------------------------

def unify_edges(interface_edges, implementation_edges):
    """Merge interface and implementation edges into a unified graph.

    Edges with the same (source, target) pair are merged:
      - provenance becomes "both"
      - categories are combined from both sources
      - interface categories are tagged with their VAR_* context
      - implementation categories retain their behavioral classification

    Returns:
      - unified_edges: list of merged edge dicts
      - edge_index: dict (source, target) -> edge dict for fast lookup
    """
    edge_index = {}

    # Index interface edges
    for edge in interface_edges:
        key = (edge["source"], edge["target"])
        edge_index[key] = {
            "source": edge["source"],
            "target": edge["target"],
            "provenance": "interface",
            "source_kind": edge["source_kind"],
            "source_file": edge["source_file"],
            "interface_categories": edge["categories"],
            "implementation_categories": [],
        }

    # Merge implementation edges
    for edge in implementation_edges:
        key = (edge["source"], edge["target"])
        if key in edge_index:
            # Edge exists in both — merge
            existing = edge_index[key]
            existing["provenance"] = "both"
            existing["implementation_categories"] = edge["categories"]
        else:
            # Implementation-only edge
            edge_index[key] = {
                "source": edge["source"],
                "target": edge["target"],
                "provenance": "implementation",
                "source_kind": edge["source_kind"],
                "source_file": edge["source_file"],
                "interface_categories": [],
                "implementation_categories": edge["categories"],
            }

    unified_edges = sorted(edge_index.values(), key=lambda e: (e["source"], e["target"]))
    return unified_edges, edge_index


# ---------------------------------------------------------------------------
# Node registry and classification
# ---------------------------------------------------------------------------

def build_node_registry(xref, impl_data, pou_index):
    """Build a registry of all nodes with their metadata.

    Returns dict: node_name -> {
      "kind": "POU" | "DUT",
      "pou_type": str (if POU),
      "base_type": str (if DUT),
      "defined_in": str (filename),
      "has_interface": bool,
      "has_implementation": bool,
      "interface_dep_count": int,
      "impl_dep_count": int,
      "interface_used_by_count": int,
      "impl_used_by_count": int,
    }
    """
    registry = {}

    # From POU_INDEX.json — all known types
    for file_entry in pou_index.get("files", []):
        filename = file_entry["filename"]
        for pou in file_entry.get("pous", []):
            name = pou["name"]
            registry[name] = {
                "kind": "POU",
                "pou_type": pou.get("pou_type", "unknown"),
                "base_type": None,
                "defined_in": filename,
                "has_interface": pou.get("interface") is not None,
                "has_implementation": False,
                "interface_dep_count": 0,
                "impl_dep_count": 0,
                "interface_used_by_count": 0,
                "impl_used_by_count": 0,
            }
        for dut in file_entry.get("duts", []):
            name = dut["name"]
            registry[name] = {
                "kind": "DUT",
                "pou_type": None,
                "base_type": dut.get("base_type", "unknown"),
                "defined_in": filename,
                "has_interface": False,
                "has_implementation": False,
                "interface_dep_count": 0,
                "impl_dep_count": 0,
                "interface_used_by_count": 0,
                "impl_used_by_count": 0,
            }

    # Mark POUs that have implementation bodies
    for obj_key in impl_data.get("impl_deps", {}):
        name = obj_key.split(":", 1)[1]
        if name in registry:
            registry[name]["has_implementation"] = True

    # Count interface dependencies (fan-out)
    for obj_key, obj_data in xref.get("uses", {}).items():
        name = obj_key.split(":", 1)[1]
        if name in registry:
            registry[name]["interface_dep_count"] = len(obj_data.get("types", {}))

    # Count implementation dependencies (fan-out)
    for obj_key, obj_data in impl_data.get("impl_deps", {}).items():
        name = obj_key.split(":", 1)[1]
        if name in registry:
            all_impl_refs = (
                set(obj_data.get("fb_calls", []))
                | set(obj_data.get("method_calls", []))
                | set(obj_data.get("property_accesses", []))
                | set(obj_data.get("type_casts", []))
                | set(obj_data.get("impl_refs", []))
            )
            registry[name]["impl_dep_count"] = len(all_impl_refs)

    # Count interface used-by (fan-in)
    for type_name, users in xref.get("used_by", {}).items():
        if type_name in registry:
            registry[type_name]["interface_used_by_count"] = len(users)

    # Count implementation used-by (fan-in)
    for type_name, users in impl_data.get("impl_used_by", {}).items():
        if type_name in registry:
            registry[type_name]["impl_used_by_count"] = len(users)

    return registry


# ---------------------------------------------------------------------------
# Adjacency lists for graph traversal
# ---------------------------------------------------------------------------

def build_adjacency_lists(unified_edges):
    """Build forward and reverse adjacency lists from unified edges.

    Returns (forward, reverse, all_nodes):
      - forward: node -> set of nodes it depends on
      - reverse: node -> set of nodes that depend on it
      - all_nodes: set of all node names
    """
    forward = defaultdict(set)
    reverse = defaultdict(set)
    all_nodes = set()

    for edge in unified_edges:
        src = edge["source"]
        tgt = edge["target"]
        all_nodes.add(src)
        all_nodes.add(tgt)
        forward[src].add(tgt)
        reverse[tgt].add(src)

    return forward, reverse, all_nodes


# ---------------------------------------------------------------------------
# Transitive analysis on unified graph
# ---------------------------------------------------------------------------

from collections import deque


def compute_transitive_closure(forward, all_nodes):
    """Compute forward transitive closure via BFS."""
    closure = {}
    for node in all_nodes:
        visited = set()
        queue = deque(forward.get(node, set()))
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in forward.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        closure[node] = visited
    return closure


def compute_impact_cascade(reverse, all_nodes):
    """Compute reverse transitive closure (impact cascade) via BFS."""
    cascade = {}
    for node in all_nodes:
        visited = set()
        queue = deque(reverse.get(node, set()))
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            for neighbor in reverse.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        cascade[node] = visited
    return cascade


# ---------------------------------------------------------------------------
# Edge provenance queries
# ---------------------------------------------------------------------------

def classify_edges_by_provenance(unified_edges):
    """Classify edges into provenance buckets.

    Returns:
      - interface_only: edges only in interface
      - impl_only: edges only in implementation
      - both: edges in both sources
    """
    interface_only = []
    impl_only = []
    both = []

    for edge in unified_edges:
        if edge["provenance"] == "interface":
            interface_only.append(edge)
        elif edge["provenance"] == "implementation":
            impl_only.append(edge)
        else:
            both.append(edge)

    return interface_only, impl_only, both


def find_impl_only_targets(unified_edges, xref):
    """Find types that are referenced ONLY in implementation, not in interface.

    Returns a sorted list of type names.
    """
    interface_targets = set()
    for obj_data in xref.get("uses", {}).values():
        for type_name in obj_data.get("types", {}):
            interface_targets.add(type_name)

    impl_targets = set()
    for edge in unified_edges:
        if edge["provenance"] in ("implementation", "both"):
            impl_targets.add(edge["target"])

    return sorted(impl_targets - interface_targets)


def find_interface_only_targets(unified_edges, impl_data):
    """Find types that are referenced ONLY in interface, not in implementation.

    Returns a sorted list of type names.
    """
    impl_targets = set()
    for obj_data in impl_data.get("impl_deps", {}).values():
        all_refs = (
            set(obj_data.get("fb_calls", []))
            | set(obj_data.get("method_calls", []))
            | set(obj_data.get("property_accesses", []))
            | set(obj_data.get("type_casts", []))
            | set(obj_data.get("impl_refs", []))
        )
        impl_targets |= all_refs

    interface_targets = set()
    for edge in unified_edges:
        if edge["provenance"] in ("interface", "both"):
            interface_targets.add(edge["target"])

    return sorted(interface_targets - impl_targets)


# ---------------------------------------------------------------------------
# Per-object unified dependency view
# ---------------------------------------------------------------------------

def get_object_dependencies(obj_name, edge_index, forward, closure, cascade):
    """Get a complete dependency view for a single object.

    Returns a dict with:
      - direct_deps: list of {target, provenance, categories}
      - transitive_deps: sorted list of all transitively-depended-on types
      - used_by: list of {source, provenance}
      - transitive_impact: sorted list of all transitively-affected objects
    """
    direct_deps = []
    # Forward edges from this object
    for tgt in sorted(forward.get(obj_name, set())):
        key = (obj_name, tgt)
        if key in edge_index:
            edge = edge_index[key]
            direct_deps.append({
                "target": tgt,
                "provenance": edge["provenance"],
                "interface_categories": edge["interface_categories"],
                "implementation_categories": edge["implementation_categories"],
            })

    # Reverse edges (who uses this object)
    used_by = []
    for src in sorted(cascade.get(obj_name, set())):
        # Find direct edges pointing to obj_name
        key = (src, obj_name)
        if key in edge_index:
            edge = edge_index[key]
            used_by.append({
                "source": src,
                "provenance": edge["provenance"],
            })

    return {
        "direct_deps": direct_deps,
        "transitive_deps": sorted(closure.get(obj_name, set())),
        "used_by": used_by,
        "transitive_impact": sorted(cascade.get(obj_name, set())),
    }


# ---------------------------------------------------------------------------
# Key object analysis
# ---------------------------------------------------------------------------

def analyze_key_objects(edge_index, forward, reverse, closure, cascade, registry):
    """Analyze key objects (parser, server, system, etc.) in the unified graph.

    Returns a dict of key object analyses.
    """
    key_patterns = [
        "system", "parser", "server", "master", "manager", "handler",
        "connection", "channel", "reportable", "particle", "executor",
        "build", "cycle", "plc", "state", "mode",
    ]

    results = {}
    for name in sorted(registry.keys()):
        name_lower = name.lower()
        if any(p in name_lower for p in key_patterns):
            obj_view = get_object_dependencies(
                name, edge_index, forward, closure, cascade
            )
            if obj_view["direct_deps"] or obj_view["used_by"]:
                results[name] = {
                    "kind": registry[name]["kind"],
                    "defined_in": registry[name]["defined_in"],
                    "interface_dep_count": registry[name]["interface_dep_count"],
                    "impl_dep_count": registry[name]["impl_dep_count"],
                    "interface_used_by_count": registry[name]["interface_used_by_count"],
                    "impl_used_by_count": registry[name]["impl_used_by_count"],
                    "direct_deps": obj_view["direct_deps"],
                    "transitive_dep_count": len(obj_view["transitive_deps"]),
                    "used_by": obj_view["used_by"],
                    "transitive_impact_count": len(obj_view["transitive_impact"]),
                }

    return results


# ---------------------------------------------------------------------------
# Build the unified output
# ---------------------------------------------------------------------------

def build_unified_output(xref, impl_data, pou_index, unified_edges, edge_index,
                         forward, reverse, all_nodes, closure, cascade,
                         node_registry):
    """Assemble the full UNIFIED_DEPS.json structure."""

    interface_only, impl_only, both_edges = classify_edges_by_provenance(unified_edges)
    impl_only_targets = find_impl_only_targets(unified_edges, xref)
    interface_only_targets = find_interface_only_targets(unified_edges, impl_data)

    # Key object analysis
    key_objects = analyze_key_objects(
        edge_index, forward, reverse, closure, cascade, node_registry
    )

    # Top nodes by combined degree
    combined_degree = []
    for node in all_nodes:
        in_deg = len(reverse.get(node, set()))
        out_deg = len(forward.get(node, set()))
        reg = node_registry.get(node, {})
        combined_degree.append({
            "node": node,
            "kind": reg.get("kind", "unknown"),
            "interface_fan_in": reg.get("interface_used_by_count", 0),
            "impl_fan_in": reg.get("impl_used_by_count", 0),
            "interface_fan_out": reg.get("interface_dep_count", 0),
            "impl_fan_out": reg.get("impl_dep_count", 0),
            "total_fan_in": in_deg,
            "total_fan_out": out_deg,
            "total_degree": in_deg + out_deg,
            "transitive_impact": len(cascade.get(node, set())),
            "transitive_deps": len(closure.get(node, set())),
        })
    combined_degree.sort(key=lambda x: (-x["total_degree"], x["node"]))

    # Summary
    summary = {
        "total_nodes": len(all_nodes),
        "total_unified_edges": len(unified_edges),
        "interface_only_edges": len(interface_only),
        "implementation_only_edges": len(impl_only),
        "edges_in_both": len(both_edges),
        "total_interface_edges": len(interface_only) + len(both_edges),
        "total_implementation_edges": len(impl_only) + len(both_edges),
        "impl_only_type_count": len(impl_only_targets),
        "interface_only_type_count": len(interface_only_targets),
        "nodes_with_transitive_deps": len([
            n for n in all_nodes if closure.get(n)
        ]),
        "nodes_with_transitive_impact": len([
            n for n in all_nodes if cascade.get(n)
        ]),
        "max_transitive_dep_count": max(
            (len(closure[n]) for n in all_nodes), default=0
        ),
        "max_transitive_impact_count": max(
            (len(cascade[n]) for n in all_nodes), default=0
        ),
    }

    # Build per-object unified view for objects with dependencies
    per_object = {}
    for edge in unified_edges:
        src = edge["source"]
        if src not in per_object:
            per_object[src] = get_object_dependencies(
                src, edge_index, forward, closure, cascade
            )

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": (
            "Unified dependency graph generated by scripts/unify_deps.py. "
            "Merges interface-derived (Phase 3) and implementation-derived "
            "(Phase 4) dependency graphs with provenance tracking on every edge."
        ),
        "summary": summary,
        "edges": [
            {
                "source": e["source"],
                "target": e["target"],
                "provenance": e["provenance"],
                "source_kind": e["source_kind"],
                "source_file": e["source_file"],
                "interface_categories": e["interface_categories"],
                "implementation_categories": e["implementation_categories"],
            }
            for e in unified_edges
        ],
        "provenance_summary": {
            "interface_only": [
                {"source": e["source"], "target": e["target"]}
                for e in interface_only
            ],
            "implementation_only": [
                {"source": e["source"], "target": e["target"]}
                for e in impl_only
            ],
            "both": [
                {"source": e["source"], "target": e["target"]}
                for e in both_edges
            ],
        },
        "impl_only_types": impl_only_targets,
        "interface_only_types": interface_only_targets,
        "combined_centrality": combined_degree[:50],
        "key_objects": key_objects,
        "per_object": {
            k: {
                "direct_deps": v["direct_deps"],
                "transitive_deps": v["transitive_deps"],
                "used_by": v["used_by"],
                "transitive_impact": v["transitive_impact"],
            }
            for k, v in per_object.items()
        },
    }


# ---------------------------------------------------------------------------
# Human-readable UNIFIED_DEPENDENCY_MAP.md
# ---------------------------------------------------------------------------

def build_unified_dependency_map(output, node_registry):
    """Generate a human-readable UNIFIED_DEPENDENCY_MAP.md."""
    lines = []
    lines.append("# UNIFIED_DEPENDENCY_MAP — Combined Interface + Implementation Dependencies")
    lines.append("")
    lines.append("> Auto-generated by `scripts/unify_deps.py`. Do not edit manually.")
    lines.append("")
    lines.append("This document presents the **unified dependency graph** that merges")
    lines.append("structural dependencies from interface declarations (Phase 3) with")
    lines.append("behavioral dependencies from ST implementation bodies (Phase 4).")
    lines.append("")
    lines.append("Every edge carries **provenance** information:")
    lines.append("- **interface** — Declared in VAR_INPUT, VAR_OUTPUT, VAR, etc.")
    lines.append("- **implementation** — Found in ST code (FB calls, method calls, etc.)")
    lines.append("- **both** — Present in both sources")
    lines.append("")

    s = output["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| Total graph nodes | %d |" % s["total_nodes"])
    lines.append("| Total unified edges | %d |" % s["total_unified_edges"])
    lines.append("| Interface-only edges | %d |" % s["interface_only_edges"])
    lines.append("| Implementation-only edges | %d |" % s["implementation_only_edges"])
    lines.append("| Edges in both sources | %d |" % s["edges_in_both"])
    lines.append("| Total interface edges | %d |" % s["total_interface_edges"])
    lines.append("| Total implementation edges | %d |" % s["total_implementation_edges"])
    lines.append("| Types referenced ONLY in impl | %d |" % s["impl_only_type_count"])
    lines.append("| Types referenced ONLY in interface | %d |" % s["interface_only_type_count"])
    lines.append("| Nodes with transitive deps | %d |" % s["nodes_with_transitive_deps"])
    lines.append("| Nodes with transitive impact | %d |" % s["nodes_with_transitive_impact"])
    lines.append("| Max transitive dep count | %d |" % s["max_transitive_dep_count"])
    lines.append("| Max transitive impact count | %d |" % s["max_transitive_impact_count"])
    lines.append("")

    # Provenance breakdown
    lines.append("## Provenance Breakdown")
    lines.append("")
    lines.append("### Edges by Provenance")
    lines.append("")
    lines.append("| Provenance | Count | Description |")
    lines.append("|---|---|---|")
    lines.append("| interface | %d | Declared in POU/DUT interface variables |" % s["interface_only_edges"])
    lines.append("| implementation | %d | Found in ST implementation bodies only |" % s["implementation_only_edges"])
    lines.append("| both | %d | Present in both interface and implementation |" % s["edges_in_both"])
    lines.append("")

    # Structural vs Behavioral comparison
    lines.append("## Structural vs Behavioral Dependencies")
    lines.append("")
    lines.append("| Aspect | Structural (Interface) | Behavioral (Implementation) |")
    lines.append("|---|---|---|")
    lines.append("| Source | VAR_INPUT, VAR_OUTPUT, VAR, VAR_GLOBAL | ST code bodies (methods, properties, POU body) |")
    lines.append("| Certainty | Compiler-enforced (definite) | Regex-inferred (probabilistic) |")
    lines.append("| Captures | Declared type relationships | Runtime usage patterns |")
    lines.append("| Edge count | %d | %d |" % (s["total_interface_edges"], s["total_implementation_edges"]))
    lines.append("")

    # Impl-only types
    if output["impl_only_types"]:
        lines.append("## Types Referenced ONLY in Implementation")
        lines.append("")
        lines.append("These types appear in ST code but are NOT declared as variable")
        lines.append("types in any POU interface. They represent behavioral dependencies")
        lines.append("that would be invisible to interface-only analysis.")
        lines.append("")
        lines.append("| Type | Kind | Defined In |")
        lines.append("|---|---|---|")

        for type_name in output["impl_only_types"][:40]:
            reg = node_registry.get(type_name, {})
            kind = reg.get("kind", "unknown")
            defined_in = reg.get("defined_in", "unknown")
            lines.append("| `%s` | %s | %s |" % (type_name, kind, defined_in))
        if len(output["impl_only_types"]) > 40:
            lines.append("| ... | | *(+%d more)* |" % (len(output["impl_only_types"]) - 40))
        lines.append("")

    # Interface-only types
    if output["interface_only_types"]:
        lines.append("## Types Referenced ONLY in Interface")
        lines.append("")
        lines.append("These types are declared in POU interfaces but do not appear")
        lines.append("in any ST implementation body. They may be:")
        lines.append("- Placeholder declarations")
        lines.append("- Types used only for type compatibility / inheritance")
        lines.append("- Dead code (declared but never actually used)")
        lines.append("")
        lines.append("| Type | Kind | Defined In |")
        lines.append("|---|---|---|")

        for type_name in output["interface_only_types"][:40]:
            reg = node_registry.get(type_name, {})
            kind = reg.get("kind", "unknown")
            defined_in = reg.get("defined_in", "unknown")
            lines.append("| `%s` | %s | %s |" % (type_name, kind, defined_in))
        if len(output["interface_only_types"]) > 40:
            lines.append("| ... | | *(+%d more)* |" % (len(output["interface_only_types"]) - 40))
        lines.append("")

    # Combined centrality
    lines.append("## Combined Centrality Rankings (Top 30)")
    lines.append("")
    lines.append("Nodes ranked by total degree in the unified graph, with separate")
    lines.append("fan-in/fan-out counts for interface and implementation sources.")
    lines.append("")
    lines.append("| Rank | Node | Kind | IF Fan-In | IF Fan-Out | Impl Fan-In | Impl Fan-Out | Total Degree | Trans. Impact | Trans. Deps |")
    lines.append("|---|---|---|---|---|---|---|---|---|---|")

    for i, entry in enumerate(output["combined_centrality"][:30], 1):
        lines.append(
            "| %d | `%s` | %s | %d | %d | %d | %d | %d | %d | %d |"
            % (
                i, entry["node"], entry["kind"],
                entry["interface_fan_in"], entry["interface_fan_out"],
                entry["impl_fan_in"], entry["impl_fan_out"],
                entry["total_degree"],
                entry["transitive_impact"], entry["transitive_deps"],
            )
        )
    lines.append("")

    # Key objects
    if output["key_objects"]:
        lines.append("## Key Object Analysis (Parser / Server / System / etc.)")
        lines.append("")
        lines.append("Detailed unified dependency view for objects whose names suggest")
        lines.append("core system roles.")
        lines.append("")

        for name in sorted(output["key_objects"].keys()):
            obj = output["key_objects"][name]
            lines.append("### `%s` (%s)" % (name, obj["kind"]))
            lines.append("")
            lines.append("Defined in: `%s`" % obj["defined_in"])
            lines.append("")
            lines.append("| Metric | Interface | Implementation |")
            lines.append("|---|---|---|")
            lines.append("| Direct deps (fan-out) | %d | %d |" % (obj["interface_dep_count"], obj["impl_dep_count"]))
            lines.append("| Used by (fan-in) | %d | %d |" % (obj["interface_used_by_count"], obj["impl_used_by_count"]))
            lines.append("| Transitive deps | %d | — |" % obj["transitive_dep_count"])
            lines.append("| Transitive impact | %d | — |" % obj["transitive_impact_count"])
            lines.append("")

            if obj["direct_deps"]:
                lines.append("**Direct dependencies:**")
                lines.append("")
                lines.append("| Target | Provenance | Interface Context | Implementation Context |")
                lines.append("|---|---|---|---|")
                for dep in obj["direct_deps"]:
                    prov = dep["provenance"]
                    iface_ctx = ", ".join(
                        "%s.%s" % (c[0], c[1]) for c in dep["interface_categories"]
                    ) if dep["interface_categories"] else "—"
                    impl_ctx = ", ".join(dep["implementation_categories"]) if dep["implementation_categories"] else "—"
                    lines.append(
                        "| `%s` | %s | %s | %s |"
                        % (dep["target"], prov, iface_ctx, impl_ctx)
                    )
                lines.append("")

            if obj["used_by"]:
                lines.append("**Used by (direct):**")
                lines.append("")
                for ub in obj["used_by"][:20]:
                    lines.append("- `%s` (%s)" % (ub["source"], ub["provenance"]))
                if len(obj["used_by"]) > 20:
                    lines.append("- *(+%d more)*" % (len(obj["used_by"]) - 20))
                lines.append("")

            lines.append("---")
            lines.append("")

    # Impact analysis: unified view
    lines.append("## Unified Impact Analysis")
    lines.append("")
    lines.append("Types ranked by transitive impact in the **unified** graph.")
    lines.append("A change to any of these types affects the listed number of")
    lines.append("objects through combined interface + implementation paths.")
    lines.append("")
    lines.append("| Rank | Type | Kind | Transitive Impact | Interface Fan-In | Impl Fan-In |")
    lines.append("|---|---|---|---|---|---|")

    impact_sorted = sorted(
        output["combined_centrality"],
        key=lambda x: (-x["transitive_impact"], x["node"])
    )
    for i, entry in enumerate(impact_sorted[:30], 1):
        if entry["transitive_impact"] > 0:
            lines.append(
                "| %d | `%s` | %s | %d | %d | %d |"
                % (
                    i, entry["node"], entry["kind"],
                    entry["transitive_impact"],
                    entry["interface_fan_in"],
                    entry["impl_fan_in"],
                )
            )
    lines.append("")

    # Implementation-only impact
    lines.append("## Implementation-Only Impact (Not in Interface)")
    lines.append("")
    lines.append("These types have impact that comes **exclusively** from implementation")
    lines.append("references — they would be invisible to interface-only analysis.")
    lines.append("")

    impl_only_impact = [
        e for e in impact_sorted
        if e["impl_fan_in"] > 0 and e["interface_fan_in"] == 0 and e["transitive_impact"] > 0
    ]
    if impl_only_impact:
        lines.append("| Rank | Type | Kind | Impl Fan-In | Transitive Impact |")
        lines.append("|---|---|---|---|---|")
        for i, entry in enumerate(impl_only_impact[:20], 1):
            lines.append(
                "| %d | `%s` | %s | %d | %d |"
                % (i, entry["node"], entry["kind"], entry["impl_fan_in"], entry["transitive_impact"])
            )
        lines.append("")
    else:
        lines.append("No types have implementation-only impact with transitive reach.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Update INDEX.json
# ---------------------------------------------------------------------------

def update_index_with_phase45(index_path):
    """Update INDEX.json to reference Phase 4.5 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    idx["phase4_5_artifacts"] = {
        "UNIFIED_DEPS.json": (
            "Machine-readable unified dependency graph merging interface-derived "
            "(Phase 3) and implementation-derived (Phase 4) edges with provenance "
            "tracking, combined transitive analysis, and per-object unified views."
        ),
        "UNIFIED_DEPENDENCY_MAP.md": (
            "Human-readable unified dependency map with structural vs behavioral "
            "comparison, impl-only type discovery, key object analysis, and "
            "combined impact rankings."
        ),
        "generated_by": "scripts/unify_deps.py",
        "description": (
            "Phase 4.5: Unified dependency graph. Merges interface and "
            "implementation dependency graphs with provenance on every edge, "
            "enabling queries that distinguish structural from behavioral "
            "dependencies and identify impl-only impact."
        ),
    }

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
        f.write("\n")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description=(
            "Unify interface-derived (Phase 3) and implementation-derived "
            "(Phase 4) dependency graphs into a single graph with provenance "
            "tracking (Phase 4.5)."
        )
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 4.5 artifact references.",
    )
    args = parser.parse_args()

    export_dir = os.path.normpath(args.export_dir)

    if not os.path.isdir(export_dir):
        print("ERROR: Export directory not found: %s" % export_dir, file=sys.stderr)
        sys.exit(1)

    # Load prerequisites
    xref_path = os.path.join(export_dir, "XREF.json")
    impl_path = os.path.join(export_dir, "IMPL_DEPS.json")
    pou_index_path = os.path.join(export_dir, "POU_INDEX.json")

    xref = load_json(xref_path)
    if xref is None:
        print("ERROR: XREF.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/build_xref.py first (Phase 3).", file=sys.stderr)
        sys.exit(1)

    impl_data = load_json(impl_path)
    if impl_data is None:
        print("ERROR: IMPL_DEPS.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/extract_impl_deps.py first (Phase 4).", file=sys.stderr)
        sys.exit(1)

    pou_index = load_json(pou_index_path)
    if pou_index is None:
        print("ERROR: POU_INDEX.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/index_xml.py first (Phase 2).", file=sys.stderr)
        sys.exit(1)

    print("Loading Phase 3 (XREF.json) ...")
    print("Loading Phase 4 (IMPL_DEPS.json) ...")
    print("Loading Phase 2 (POU_INDEX.json) ...")

    # Extract edges from both sources
    print("Extracting interface-derived edges ...")
    interface_edges = extract_interface_edges(xref)
    print("  Found %d interface edges" % len(interface_edges))

    print("Extracting implementation-derived edges ...")
    implementation_edges = extract_implementation_edges(impl_data)
    print("  Found %d implementation edges" % len(implementation_edges))

    # Unify
    print("Unifying edges ...")
    unified_edges, edge_index = unify_edges(interface_edges, implementation_edges)
    print("  Unified graph: %d edges" % len(unified_edges))

    # Classify
    iface_only, impl_only, both = classify_edges_by_provenance(unified_edges)
    print("  Interface-only: %d" % len(iface_only))
    print("  Implementation-only: %d" % len(impl_only))
    print("  Both sources: %d" % len(both))

    # Build node registry
    print("Building node registry ...")
    node_registry = build_node_registry(xref, impl_data, pou_index)

    # Build adjacency lists
    print("Building adjacency lists ...")
    forward, reverse, all_nodes = build_adjacency_lists(unified_edges)

    # Transitive analysis
    print("Computing transitive closure ...")
    closure = compute_transitive_closure(forward, all_nodes)

    print("Computing impact cascade ...")
    cascade = compute_impact_cascade(reverse, all_nodes)

    # Build output
    print("Assembling UNIFIED_DEPS.json ...")
    output = build_unified_output(
        xref, impl_data, pou_index, unified_edges, edge_index,
        forward, reverse, all_nodes, closure, cascade, node_registry
    )

    # Write UNIFIED_DEPS.json
    unified_path = os.path.join(export_dir, "UNIFIED_DEPS.json")
    with open(unified_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Unified dependency graph written to: %s" % unified_path)

    # Build and write UNIFIED_DEPENDENCY_MAP.md
    print("Generating UNIFIED_DEPENDENCY_MAP.md ...")
    unified_map = build_unified_dependency_map(output, node_registry)
    map_path = os.path.join(export_dir, "UNIFIED_DEPENDENCY_MAP.md")
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(unified_map)
    print("Unified dependency map written to: %s" % map_path)

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_phase45(index_path)
        print("INDEX.json updated with Phase 4.5 artifact references.")

    # Print summary
    s = output["summary"]
    print("\nPhase 4.5 Summary:")
    print("  Total graph nodes: %d" % s["total_nodes"])
    print("  Total unified edges: %d" % s["total_unified_edges"])
    print("  Interface-only edges: %d" % s["interface_only_edges"])
    print("  Implementation-only edges: %d" % s["implementation_only_edges"])
    print("  Edges in both sources: %d" % s["edges_in_both"])
    print("  Impl-only types: %d" % s["impl_only_type_count"])
    print("  Interface-only types: %d" % s["interface_only_type_count"])
    print("  Max transitive impact: %d" % s["max_transitive_impact_count"])
    print("  Max transitive deps: %d" % s["max_transitive_dep_count"])

    if output["impl_only_types"]:
        print("\n  Top 10 impl-only types (by name):")
        for t in output["impl_only_types"][:10]:
            reg = node_registry.get(t, {})
            print("    %-45s  (%s in %s)" % (t, reg.get("kind", "?"), reg.get("defined_in", "?")))


if __name__ == "__main__":
    main()

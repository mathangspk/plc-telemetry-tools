"""
analyze_graph.py — Phase 3.5: Transitive dependency / cascade analysis.

Reads XREF.json (produced by scripts/build_xref.py) and computes:
  - Transitive dependency closure (forward): for each object, all types it
    transitively depends on through the uses graph.
  - Impact cascade (reverse): for each type/object, the full set of objects
    that would be affected by a change (reverse transitive closure).
  - Shortest dependency paths between notable object pairs.
  - Graph centrality metrics (in-degree, out-degree, total degree).

Produces:
  - TRANSITIVE_CLOSURE.json  — Machine-readable transitive dependency data.
  - CASCADE_ANALYSIS.md      — Human-readable cascade/impact analysis.

Usage:
    python scripts/analyze_graph.py exports/v1

This script is designed to run AFTER build_xref.py. It does NOT parse XML
files or POU_INDEX.json directly; it consumes the XREF.json artifact.
"""

import argparse
import json
import os
import sys
from collections import defaultdict, deque
from datetime import datetime, timezone

# ---------------------------------------------------------------------------
# Graph construction from XREF.json
# ---------------------------------------------------------------------------


def build_adjacency_lists(xref):
    """Build forward and reverse adjacency lists from XREF.json.

    Forward graph (uses):
      node -> set of nodes it directly depends on.
      Nodes are type names (POU/DUT names) that appear as keys in uses
      or as values in uses[*].types.

    Reverse graph (used_by / impact):
      node -> set of nodes that directly depend on it.

    Returns (forward, reverse, all_nodes).
    """
    forward = defaultdict(set)  # A -> {B, C} means A uses B and C
    reverse = defaultdict(set)  # B -> {A} means A uses B (B is used by A)
    all_nodes = set()

    uses = xref.get("uses", {})
    for obj_key, obj_data in uses.items():
        # obj_key is like "POU:Name" or "DUT:Name"
        # Extract the bare name for graph nodes
        obj_name = obj_key.split(":", 1)[1]
        all_nodes.add(obj_name)

        for type_name in obj_data.get("types", {}):
            all_nodes.add(type_name)
            forward[obj_name].add(type_name)
            reverse[type_name].add(obj_name)

    return forward, reverse, all_nodes


# ---------------------------------------------------------------------------
# Transitive closure (forward) — BFS from each node
# ---------------------------------------------------------------------------


def compute_transitive_closure(forward, all_nodes):
    """Compute the transitive closure of the forward (uses) graph.

    For each node, returns the set of all nodes reachable via one or more
    forward edges (i.e., all types this object transitively depends on).

    Returns dict: node -> set of transitively-reachable nodes.
    """
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


# ---------------------------------------------------------------------------
# Impact cascade (reverse transitive closure) — BFS from each node
# ---------------------------------------------------------------------------


def compute_impact_cascade(reverse, all_nodes):
    """Compute the reverse transitive closure (impact cascade).

    For each node, returns the set of all nodes that would be affected
    if this node changed (i.e., all objects that transitively depend on it).

    Returns dict: node -> set of transitively-affected nodes.
    """
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
# Shortest path (BFS) between two nodes
# ---------------------------------------------------------------------------


def shortest_path(forward, source, target):
    """Find the shortest dependency path from source to target using BFS.

    Returns a list of node names representing the path, or None if no path.
    """
    if source == target:
        return [source]

    visited = {source}
    queue = deque([(source, [source])])

    while queue:
        current, path = queue.popleft()
        for neighbor in forward.get(current, set()):
            if neighbor == target:
                return path + [neighbor]
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append((neighbor, path + [neighbor]))

    return None


# ---------------------------------------------------------------------------
# Centrality metrics
# ---------------------------------------------------------------------------


def compute_centrality(forward, reverse, all_nodes):
    """Compute basic centrality metrics for each node.

    Returns a list of dicts sorted by total_degree descending:
      - node: name
      - in_degree: number of objects that directly use this node (fan-in)
      - out_degree: number of types this node directly uses (fan-out)
      - total_degree: in_degree + out_degree
      - transitive_impact: count of objects transitively affected
      - transitive_deps: count of types transitively depended on
    """
    metrics = []
    for node in all_nodes:
        in_deg = len(reverse.get(node, set()))
        out_deg = len(forward.get(node, set()))
        metrics.append(
            {
                "node": node,
                "in_degree": in_deg,
                "out_degree": out_deg,
                "total_degree": in_deg + out_deg,
            }
        )

    metrics.sort(key=lambda m: (-m["total_degree"], m["node"]))
    return metrics


def enrich_centrality_with_transitive(metrics, closure, cascade):
    """Add transitive impact/dependency counts to centrality metrics."""
    for m in metrics:
        node = m["node"]
        m["transitive_impact"] = len(cascade.get(node, set()))
        m["transitive_deps"] = len(closure.get(node, set()))
    return metrics


# ---------------------------------------------------------------------------
# Notable dependency chains
# ---------------------------------------------------------------------------


def find_notable_chains(forward, reverse, all_nodes, top_n=20):
    """Identify notable dependency chains in the graph.

    Finds:
      1. Longest direct dependency chains (objects with high fan-out that
         point to objects that also have high fan-out).
      2. Bridge nodes — nodes with both significant fan-in and fan-out
         (potential coupling points).
      3. Leaf nodes — nodes with fan-in > 0 but fan-out == 0 (terminal types).
      4. Root nodes — nodes with fan-out > 0 but fan-in == 0 (top-level consumers).

    Returns a dict with categorized findings.
    """
    bridges = []
    leaves = []
    roots = []

    for node in all_nodes:
        in_deg = len(reverse.get(node, set()))
        out_deg = len(forward.get(node, set()))

        if in_deg >= 2 and out_deg >= 2:
            bridges.append(
                {
                    "node": node,
                    "in_degree": in_deg,
                    "out_degree": out_deg,
                }
            )
        elif in_deg > 0 and out_deg == 0:
            leaves.append(
                {
                    "node": node,
                    "in_degree": in_deg,
                }
            )
        elif out_deg > 0 and in_deg == 0:
            roots.append(
                {
                    "node": node,
                    "out_degree": out_deg,
                }
            )

    bridges.sort(key=lambda b: (-(b["in_degree"] * b["out_degree"]), b["node"]))
    leaves.sort(key=lambda l: (-l["in_degree"], l["node"]))
    roots.sort(key=lambda r: (-r["out_degree"], r["node"]))

    return {
        "bridges": bridges[:top_n],
        "leaves": leaves[:top_n],
        "roots": roots[:top_n],
    }


# ---------------------------------------------------------------------------
# Path queries for notable object pairs
# ---------------------------------------------------------------------------


def compute_notable_paths(forward, all_nodes, xref):
    """Compute shortest paths between notable object pairs.

    Selects pairs based on:
      - Top fan-in types and the objects that use them.
      - Top fan-out objects and the types they use.
      - Build objects (names ending in "Build") and their transitive deps.

    Returns a list of path results.
    """
    paths = []
    seen_pairs = set()

    # Build objects and their transitive dependencies
    build_objects = [n for n in all_nodes if n.endswith("Build")]
    for build_obj in sorted(build_objects):
        trans_deps = set()
        queue = deque(forward.get(build_obj, set()))
        visited = set()
        while queue:
            current = queue.popleft()
            if current in visited:
                continue
            visited.add(current)
            trans_deps.add(current)
            for neighbor in forward.get(current, set()):
                if neighbor not in visited:
                    queue.append(neighbor)

        # Find paths to a few key transitive deps
        key_deps = sorted(trans_deps)[:5]
        for dep in key_deps:
            pair_key = (build_obj, dep)
            if pair_key in seen_pairs:
                continue
            seen_pairs.add(pair_key)

            path = shortest_path(forward, build_obj, dep)
            if path:
                paths.append(
                    {
                        "source": build_obj,
                        "target": dep,
                        "hops": len(path) - 1,
                        "path": path,
                    }
                )

    # Sort by hops descending (longer paths first)
    paths.sort(key=lambda p: (-p["hops"], p["source"], p["target"]))
    return paths[:50]  # cap output


# ---------------------------------------------------------------------------
# Build the full transitive closure output
# ---------------------------------------------------------------------------


def build_transitive_output(
    xref, forward, reverse, all_nodes, closure, cascade, centrality, notable, paths
):
    """Assemble the full TRANSITIVE_CLOSURE.json structure."""
    # Convert sets to sorted lists for JSON serialization
    closure_output = {}
    for node in sorted(closure.keys()):
        deps = sorted(closure[node])
        if deps:
            closure_output[node] = deps

    cascade_output = {}
    for node in sorted(cascade.keys()):
        affected = sorted(cascade[node])
        if affected:
            cascade_output[node] = affected

    # Top impact types (highest transitive impact)
    top_impact = sorted(
        [
            {"node": n, "impact_count": len(cascade[n])}
            for n in all_nodes
            if cascade.get(n)
        ],
        key=lambda x: (-x["impact_count"], x["node"]),
    )[:30]

    # Top dependency depth (highest transitive deps)
    top_deps = sorted(
        [
            {"node": n, "dep_count": len(closure[n])}
            for n in all_nodes
            if closure.get(n)
        ],
        key=lambda x: (-x["dep_count"], x["node"]),
    )[:30]

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": (
            "Transitive dependency and impact cascade analysis generated by "
            "scripts/analyze_graph.py from XREF.json."
        ),
        "summary": {
            "total_nodes": len(all_nodes),
            "total_direct_edges": sum(len(v) for v in forward.values()),
            "nodes_with_transitive_deps": len([n for n in all_nodes if closure.get(n)]),
            "nodes_with_transitive_impact": len(
                [n for n in all_nodes if cascade.get(n)]
            ),
            "max_transitive_dep_depth": max(
                (len(closure[n]) for n in all_nodes), default=0
            ),
            "max_transitive_impact_count": max(
                (len(cascade[n]) for n in all_nodes), default=0
            ),
        },
        "transitive_closure": closure_output,
        "impact_cascade": cascade_output,
        "top_impact_types": top_impact,
        "top_dependency_objects": top_deps,
        "centrality": centrality,
        "notable_nodes": notable,
        "notable_paths": paths,
    }


# ---------------------------------------------------------------------------
# Human-readable CASCADE_ANALYSIS.md
# ---------------------------------------------------------------------------


def build_cascade_analysis_md(
    output, xref, forward, reverse, all_nodes, closure, cascade
):
    """Generate a human-readable CASCADE_ANALYSIS.md from transitive data."""
    lines = []
    lines.append("# CASCADE_ANALYSIS — Transitive Dependency & Impact Analysis")
    lines.append("")
    lines.append(
        "> Auto-generated by `scripts/analyze_graph.py`. Do not edit manually."
    )
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = output["summary"]
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| Total graph nodes | %d |" % s["total_nodes"])
    lines.append("| Total direct dependency edges | %d |" % s["total_direct_edges"])
    lines.append(
        "| Nodes with transitive dependencies | %d |" % s["nodes_with_transitive_deps"]
    )
    lines.append(
        "| Nodes with transitive impact | %d |" % s["nodes_with_transitive_impact"]
    )
    lines.append(
        "| Max transitive dependency count | %d |" % s["max_transitive_dep_depth"]
    )
    lines.append(
        "| Max transitive impact count | %d |" % s["max_transitive_impact_count"]
    )
    lines.append("")

    # Top impact types
    lines.append("## Highest-Impact Types (Change Cascade)")
    lines.append("")
    lines.append("If you change one of these types, the following number of")
    lines.append("other objects are transitively affected (direct + indirect).")
    lines.append("")
    lines.append("| Type | Direct Users | Transitive Impact |")
    lines.append("|---|---|---|")

    for entry in output["top_impact_types"][:25]:
        node = entry["node"]
        direct = len(reverse.get(node, set()))
        transitive = entry["impact_count"]
        lines.append("| `%s` | %d | %d |" % (node, direct, transitive))
    lines.append("")

    # Most-dependent objects
    lines.append("## Most-Dependent Objects (Transitive)")
    lines.append("")
    lines.append("These objects transitively depend on the most other types.")
    lines.append("They are the most sensitive to upstream changes.")
    lines.append("")
    lines.append("| Object | Direct Deps | Transitive Deps |")
    lines.append("|---|---|---|")

    for entry in output["top_dependency_objects"][:25]:
        node = entry["node"]
        direct = len(forward.get(node, set()))
        transitive = entry["dep_count"]
        lines.append("| `%s` | %d | %d |" % (node, direct, transitive))
    lines.append("")

    # Bridge nodes
    lines.append("## Bridge Nodes (Coupling Points)")
    lines.append("")
    lines.append("These nodes have both significant fan-in and fan-out, making them")
    lines.append("potential coupling points in the architecture. Changes to a bridge")
    lines.append("node can ripple both upstream and downstream.")
    lines.append("")
    lines.append("| Node | Fan-In | Fan-Out | Product |")
    lines.append("|---|---|---|---|")

    for b in output["notable_nodes"]["bridges"][:20]:
        product = b["in_degree"] * b["out_degree"]
        lines.append(
            "| `%s` | %d | %d | %d |"
            % (b["node"], b["in_degree"], b["out_degree"], product)
        )
    lines.append("")

    # Leaf nodes (terminal types)
    lines.append("## Leaf Nodes (Terminal Types)")
    lines.append("")
    lines.append("These types are used by other objects but do not themselves depend")
    lines.append("on any other project-defined types. They are the foundation of the")
    lines.append("dependency graph.")
    lines.append("")
    lines.append("| Type | Used By (Direct) |")
    lines.append("|---|---|")

    for leaf in output["notable_nodes"]["leaves"][:20]:
        lines.append("| `%s` | %d |" % (leaf["node"], leaf["in_degree"]))
    lines.append("")

    # Root nodes (top-level consumers)
    lines.append("## Root Nodes (Top-Level Consumers)")
    lines.append("")
    lines.append("These objects depend on other types but are not themselves used by")
    lines.append("any other project-defined object. They are likely top-level")
    lines.append("composition points or build wrappers.")
    lines.append("")
    lines.append("| Object | Depends On (Direct) |")
    lines.append("|---|---|")

    for root in output["notable_nodes"]["roots"][:20]:
        lines.append("| `%s` | %d |" % (root["node"], root["out_degree"]))
    lines.append("")

    # Notable dependency paths
    lines.append("## Notable Dependency Paths")
    lines.append("")
    lines.append("Shortest dependency paths from Build objects to their transitive")
    lines.append("dependencies, showing the chain of types connecting them.")
    lines.append("")

    if output["notable_paths"]:
        for p in output["notable_paths"][:30]:
            path_str = " -> ".join("`%s`" % n for n in p["path"])
            lines.append(
                "### `%s` -> `%s` (%d hops)" % (p["source"], p["target"], p["hops"])
            )
            lines.append("")
            lines.append("Path: %s" % path_str)
            lines.append("")
    else:
        lines.append("No notable paths found.")
        lines.append("")

    # Full cascade detail for high-impact types
    lines.append("## Full Cascade Detail (Top 10 Impact Types)")
    lines.append("")
    lines.append("For each of the top 10 highest-impact types, the complete list of")
    lines.append("transitively affected objects is shown.")
    lines.append("")

    for entry in output["top_impact_types"][:10]:
        node = entry["node"]
        affected = cascade.get(node, set())
        if not affected:
            continue

        direct_users = reverse.get(node, set())
        indirect_users = affected - direct_users

        lines.append("### `%s` (affects %d objects total)" % (node, len(affected)))
        lines.append("")
        lines.append("**Direct users (%d):**" % len(direct_users))
        lines.append("")
        for u in sorted(direct_users):
            lines.append("- `%s`" % u)
        lines.append("")

        if indirect_users:
            lines.append("**Indirect users (%d):**" % len(indirect_users))
            lines.append("")
            for u in sorted(indirect_users):
                # Show the path from node to u
                path = shortest_path(forward, u, node)
                # Reverse it: node -> ... -> u
                if path:
                    path.reverse()
                    path_str = " -> ".join("`%s`" % n for n in path)
                    lines.append("- `%s` (via %s)" % (u, path_str))
                else:
                    lines.append("- `%s`" % u)
            lines.append("")
        else:
            lines.append("No indirect users — all impact is direct.")
            lines.append("")

    # Centrality table
    lines.append("## Centrality Rankings (Top 30)")
    lines.append("")
    lines.append("Objects ranked by total degree (fan-in + fan-out).")
    lines.append("")
    lines.append(
        "| Rank | Node | Fan-In | Fan-Out | Total | Trans. Impact | Trans. Deps |"
    )
    lines.append("|---|---|---|---|---|---|---|")

    for i, m in enumerate(output["centrality"][:30], 1):
        lines.append(
            "| %d | `%s` | %d | %d | %d | %d | %d |"
            % (
                i,
                m["node"],
                m["in_degree"],
                m["out_degree"],
                m["total_degree"],
                m["transitive_impact"],
                m["transitive_deps"],
            )
        )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Update INDEX.json
# ---------------------------------------------------------------------------


def update_index_with_phase35(index_path):
    """Update INDEX.json to reference Phase 3.5 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    idx["phase3_5_artifacts"] = {
        "TRANSITIVE_CLOSURE.json": (
            "Machine-readable transitive dependency closure, impact cascade, "
            "centrality metrics, and notable dependency paths."
        ),
        "CASCADE_ANALYSIS.md": (
            "Human-readable cascade/impact analysis with bridge nodes, leaf/root "
            "classification, full cascade detail, and centrality rankings."
        ),
        "generated_by": "scripts/analyze_graph.py",
        "description": (
            "Phase 3.5: Transitive dependency and cascade analysis on top of "
            "the Phase 3 cross-reference graph."
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
            "Compute transitive dependency closure and impact cascade from "
            "XREF.json (Phase 3.5)."
        )
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 3.5 artifact references.",
    )
    args = parser.parse_args()

    export_dir = os.path.normpath(args.export_dir)

    if not os.path.isdir(export_dir):
        print("ERROR: Export directory not found: %s" % export_dir, file=sys.stderr)
        sys.exit(1)

    xref_path = os.path.join(export_dir, "XREF.json")
    if not os.path.isfile(xref_path):
        print("ERROR: XREF.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/build_xref.py first to generate XREF.json.", file=sys.stderr)
        sys.exit(1)

    print("Loading XREF.json from %s ..." % xref_path)
    with open(xref_path, "r", encoding="utf-8") as f:
        xref = json.load(f)

    print("Building adjacency lists ...")
    forward, reverse, all_nodes = build_adjacency_lists(xref)

    print("Computing transitive closure (forward) ...")
    closure = compute_transitive_closure(forward, all_nodes)

    print("Computing impact cascade (reverse) ...")
    cascade = compute_impact_cascade(reverse, all_nodes)

    print("Computing centrality metrics ...")
    centrality = compute_centrality(forward, reverse, all_nodes)
    centrality = enrich_centrality_with_transitive(centrality, closure, cascade)

    print("Identifying notable nodes (bridges, leaves, roots) ...")
    notable = find_notable_chains(forward, reverse, all_nodes)

    print("Computing notable dependency paths ...")
    paths = compute_notable_paths(forward, all_nodes, xref)

    # Build output
    print("Assembling TRANSITIVE_CLOSURE.json ...")
    output = build_transitive_output(
        xref, forward, reverse, all_nodes, closure, cascade, centrality, notable, paths
    )

    # Write TRANSITIVE_CLOSURE.json
    tc_path = os.path.join(export_dir, "TRANSITIVE_CLOSURE.json")
    with open(tc_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Transitive closure written to: %s" % tc_path)

    # Build and write CASCADE_ANALYSIS.md
    print("Generating CASCADE_ANALYSIS.md ...")
    cascade_md = build_cascade_analysis_md(
        output, xref, forward, reverse, all_nodes, closure, cascade
    )
    cascade_path = os.path.join(export_dir, "CASCADE_ANALYSIS.md")
    with open(cascade_path, "w", encoding="utf-8") as f:
        f.write(cascade_md)
    print("Cascade analysis written to: %s" % cascade_path)

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_phase35(index_path)
        print("INDEX.json updated with Phase 3.5 artifact references.")

    # Print summary
    s = output["summary"]
    print("\nPhase 3.5 Summary:")
    print("  Total graph nodes: %d" % s["total_nodes"])
    print("  Total direct edges: %d" % s["total_direct_edges"])
    print("  Nodes with transitive deps: %d" % s["nodes_with_transitive_deps"])
    print("  Nodes with transitive impact: %d" % s["nodes_with_transitive_impact"])
    print("  Max transitive dep count: %d" % s["max_transitive_dep_depth"])
    print("  Max transitive impact count: %d" % s["max_transitive_impact_count"])

    if output["top_impact_types"]:
        print("\n  Top 5 highest-impact types:")
        for entry in output["top_impact_types"][:5]:
            print(
                "    %-45s  affects %d objects" % (entry["node"], entry["impact_count"])
            )

    if output["notable_paths"]:
        print(
            "\n  Longest notable path: %d hops (%s -> %s)"
            % (
                output["notable_paths"][0]["hops"],
                output["notable_paths"][0]["source"],
                output["notable_paths"][0]["target"],
            )
        )


if __name__ == "__main__":
    main()

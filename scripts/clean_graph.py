"""
clean_graph.py — Phase 5: Graph Cleaning & Confidence Scoring.

Processes the Phase 4.5 unified dependency graph (UNIFIED_DEPS.json) to:
  1. Remove known false positives (IEC keywords, conversion functions,
     standard library functions, local variable names, self-references,
     and common method/property names that are not project types).
  2. Assign confidence scores to remaining edges based on provenance
     and implementation category strength.
  3. Produce a cleaned, machine-readable graph artifact (CLEAN_DEPS.json).
  4. Produce a human-readable report (CLEAN_DEPENDENCY_MAP.md).

Usage:
    python scripts/clean_graph.py exports/v1

This script is designed to run AFTER unify_deps.py (Phase 4.5).
It consumes UNIFIED_DEPS.json and POU_INDEX.json.

Confidence scoring model:
  Every surviving edge carries a "confidence" field (0.0–1.0):
    - 0.95–1.00  "high"      — provenance == "both" (structurally declared AND behaviorally used)
    - 0.70–0.94  "medium"    — provenance == "interface" (compiler-enforced declaration)
    - 0.30–0.69  "low"       — provenance == "implementation" (regex-inferred)
      Within implementation, sub-scoring applies:
        - fb_call + impl_ref  → 0.60–0.69
        - method_call          → 0.50–0.59
        - property_access      → 0.40–0.49
        - type_cast only       → 0.30–0.39
        - impl_ref only        → 0.35–0.44

Filtering rules (edges removed):
  1. IEC keywords (IF, CASE, AND, OR, etc.)
  2. Standard type conversion functions (*_TO_*)
  3. Standard library FBs/functions (TON, MAX, MIN, ADR, etc.)
  4. Self-references (source == target)
  5. Local variable names (l*, r*, etc. not in known type registry)
  6. Common method/property names that are not project-defined types
  7. Targets with unknown kind (not in POU_INDEX.json)
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone


# ---------------------------------------------------------------------------
# False-positive filter lists
# ---------------------------------------------------------------------------

# IEC 61131-3 keywords that should never be dependency targets.
IEC_KEYWORDS = frozenset([
    "IF", "ELSE", "ELSIF", "THEN", "END_IF",
    "FOR", "TO", "BY", "DO", "END_FOR",
    "WHILE", "END_WHILE",
    "REPEAT", "UNTIL", "END_REPEAT",
    "CASE", "OF", "END_CASE",
    "RETURN", "EXIT", "CONTINUE",
    "VAR", "VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR_TEMP",
    "VAR_GLOBAL", "VAR_EXTERNAL", "VAR_ACCESS", "END_VAR",
    "TRUE", "FALSE",
    "AND", "OR", "NOT", "XOR", "MOD",
    "PROGRAM", "END_PROGRAM",
    "FUNCTION", "END_FUNCTION",
    "FUNCTION_BLOCK", "END_FUNCTION_BLOCK",
    "CLASS", "END_CLASS",
    "METHOD", "END_METHOD",
    "PROPERTY", "END_PROPERTY",
    "INTERFACE", "END_INTERFACE",
    "STRUCT", "END_STRUCT",
    "TYPE", "END_TYPE",
    "CONSTANT", "RETAIN", "NON_RETAIN",
    "AT", "OF",
    "ACTION", "END_ACTION",
    "STEP", "END_STEP",
    "TRANSITION", "END_TRANSITION",
    "SUPER", "THIS", "NULL",
    "WITH", "FROM", "USING",
])

# IEC 61131-3 standard conversion functions.
CONVERSION_FUNCTIONS = frozenset([
    # All *_TO_* patterns are handled by regex, but common ones listed for clarity.
    "BOOL_TO_BYTE", "BOOL_TO_WORD", "BOOL_TO_DWORD", "BOOL_TO_LWORD",
    "BOOL_TO_SINT", "BOOL_TO_USINT", "BOOL_TO_INT", "BOOL_TO_UINT",
    "BOOL_TO_DINT", "BOOL_TO_UDINT", "BOOL_TO_LINT", "BOOL_TO_ULINT",
    "BOOL_TO_REAL", "BOOL_TO_LREAL", "BOOL_TO_STRING", "BOOL_TO_WSTRING",
    "BYTE_TO_BOOL", "BYTE_TO_WORD", "BYTE_TO_DWORD", "BYTE_TO_LWORD",
    "BYTE_TO_SINT", "BYTE_TO_USINT", "BYTE_TO_INT", "BYTE_TO_UINT",
    "BYTE_TO_DINT", "BYTE_TO_UDINT", "BYTE_TO_LINT", "BYTE_TO_ULINT",
    "BYTE_TO_REAL", "BYTE_TO_LREAL", "BYTE_TO_STRING", "BYTE_TO_WSTRING",
    "WORD_TO_BOOL", "WORD_TO_BYTE", "WORD_TO_DWORD", "WORD_TO_LWORD",
    "WORD_TO_SINT", "WORD_TO_USINT", "WORD_TO_INT", "WORD_TO_UINT",
    "WORD_TO_DINT", "WORD_TO_UDINT", "WORD_TO_LINT", "WORD_TO_ULINT",
    "WORD_TO_REAL", "WORD_TO_LREAL", "WORD_TO_STRING", "WORD_TO_WSTRING",
    "DWORD_TO_BOOL", "DWORD_TO_BYTE", "DWORD_TO_WORD", "DWORD_TO_LWORD",
    "DWORD_TO_SINT", "DWORD_TO_USINT", "DWORD_TO_INT", "DWORD_TO_UINT",
    "DWORD_TO_DINT", "DWORD_TO_UDINT", "DWORD_TO_LINT", "DWORD_TO_ULINT",
    "DWORD_TO_REAL", "DWORD_TO_LREAL", "DWORD_TO_STRING", "DWORD_TO_WSTRING",
    "LWORD_TO_BOOL", "LWORD_TO_BYTE", "LWORD_TO_WORD", "LWORD_TO_DWORD",
    "LWORD_TO_SINT", "LWORD_TO_USINT", "LWORD_TO_INT", "LWORD_TO_UINT",
    "LWORD_TO_DINT", "LWORD_TO_UDINT", "LWORD_TO_LINT", "LWORD_TO_ULINT",
    "LWORD_TO_REAL", "LWORD_TO_LREAL", "LWORD_TO_STRING", "LWORD_TO_WSTRING",
    "SINT_TO_BOOL", "SINT_TO_BYTE", "SINT_TO_WORD", "SINT_TO_DWORD",
    "SINT_TO_LWORD", "SINT_TO_USINT", "SINT_TO_INT", "SINT_TO_UINT",
    "SINT_TO_DINT", "SINT_TO_UDINT", "SINT_TO_LINT", "SINT_TO_ULINT",
    "SINT_TO_REAL", "SINT_TO_LREAL", "SINT_TO_STRING", "SINT_TO_WSTRING",
    "USINT_TO_BOOL", "USINT_TO_BYTE", "USINT_TO_WORD", "USINT_TO_DWORD",
    "USINT_TO_LWORD", "USINT_TO_SINT", "USINT_TO_INT", "USINT_TO_UINT",
    "USINT_TO_DINT", "USINT_TO_UDINT", "USINT_TO_LINT", "USINT_TO_ULINT",
    "USINT_TO_REAL", "USINT_TO_LREAL", "USINT_TO_STRING", "USINT_TO_WSTRING",
    "INT_TO_BOOL", "INT_TO_BYTE", "INT_TO_WORD", "INT_TO_DWORD",
    "INT_TO_LWORD", "INT_TO_SINT", "INT_TO_USINT", "INT_TO_UINT",
    "INT_TO_DINT", "INT_TO_UDINT", "INT_TO_LINT", "INT_TO_ULINT",
    "INT_TO_REAL", "INT_TO_LREAL", "INT_TO_STRING", "INT_TO_WSTRING",
    "UINT_TO_BOOL", "UINT_TO_BYTE", "UINT_TO_WORD", "UINT_TO_DWORD",
    "UINT_TO_LWORD", "UINT_TO_SINT", "UINT_TO_USINT", "UINT_TO_INT",
    "UINT_TO_DINT", "UINT_TO_UDINT", "UINT_TO_LINT", "UINT_TO_ULINT",
    "UINT_TO_REAL", "UINT_TO_LREAL", "UINT_TO_STRING", "UINT_TO_WSTRING",
    "DINT_TO_BOOL", "DINT_TO_BYTE", "DINT_TO_WORD", "DINT_TO_DWORD",
    "DINT_TO_LWORD", "DINT_TO_SINT", "DINT_TO_USINT", "DINT_TO_INT",
    "DINT_TO_UINT", "DINT_TO_UDINT", "DINT_TO_LINT", "DINT_TO_ULINT",
    "DINT_TO_REAL", "DINT_TO_LREAL", "DINT_TO_STRING", "DINT_TO_WSTRING",
    "UDINT_TO_BOOL", "UDINT_TO_BYTE", "UDINT_TO_WORD", "UDINT_TO_DWORD",
    "UDINT_TO_LWORD", "UDINT_TO_SINT", "UDINT_TO_USINT", "UDINT_TO_INT",
    "UDINT_TO_UINT", "UDINT_TO_DINT", "UDINT_TO_LINT", "UDINT_TO_ULINT",
    "UDINT_TO_REAL", "UDINT_TO_LREAL", "UDINT_TO_STRING", "UDINT_TO_WSTRING",
    "LINT_TO_BOOL", "LINT_TO_BYTE", "LINT_TO_WORD", "LINT_TO_DWORD",
    "LINT_TO_LWORD", "LINT_TO_SINT", "LINT_TO_USINT", "LINT_TO_INT",
    "LINT_TO_UINT", "LINT_TO_DINT", "LINT_TO_UDINT", "LINT_TO_ULINT",
    "LINT_TO_REAL", "LINT_TO_LREAL", "LINT_TO_STRING", "LINT_TO_WSTRING",
    "ULINT_TO_BOOL", "ULINT_TO_BYTE", "ULINT_TO_WORD", "ULINT_TO_DWORD",
    "ULINT_TO_LWORD", "ULINT_TO_SINT", "ULINT_TO_USINT", "ULINT_TO_INT",
    "ULINT_TO_UINT", "ULINT_TO_DINT", "ULINT_TO_UDINT", "ULINT_TO_LINT",
    "ULINT_TO_REAL", "ULINT_TO_LREAL", "ULINT_TO_STRING", "ULINT_TO_WSTRING",
    "REAL_TO_BOOL", "REAL_TO_BYTE", "REAL_TO_WORD", "REAL_TO_DWORD",
    "REAL_TO_LWORD", "REAL_TO_SINT", "REAL_TO_USINT", "REAL_TO_INT",
    "REAL_TO_UINT", "REAL_TO_DINT", "REAL_TO_UDINT", "REAL_TO_LINT",
    "REAL_TO_ULINT", "REAL_TO_LREAL", "REAL_TO_STRING", "REAL_TO_WSTRING",
    "REAL_TO_TIME", "REAL_TO_LTIME",
    "LREAL_TO_BOOL", "LREAL_TO_BYTE", "LREAL_TO_WORD", "LREAL_TO_DWORD",
    "LREAL_TO_LWORD", "LREAL_TO_SINT", "LREAL_TO_USINT", "LREAL_TO_INT",
    "LREAL_TO_UINT", "LREAL_TO_DINT", "LREAL_TO_UDINT", "LREAL_TO_LINT",
    "LREAL_TO_ULINT", "LREAL_TO_REAL", "LREAL_TO_STRING", "LREAL_TO_WSTRING",
    "LREAL_TO_TIME", "LREAL_TO_LTIME",
    "TIME_TO_BOOL", "TIME_TO_BYTE", "TIME_TO_WORD", "TIME_TO_DWORD",
    "TIME_TO_LWORD", "TIME_TO_SINT", "TIME_TO_USINT", "TIME_TO_INT",
    "TIME_TO_UINT", "TIME_TO_DINT", "TIME_TO_UDINT", "TIME_TO_LINT",
    "TIME_TO_ULINT", "TIME_TO_REAL", "TIME_TO_LREAL", "TIME_TO_STRING",
    "TIME_TO_LTIME",
    "LTIME_TO_BOOL", "LTIME_TO_BYTE", "LTIME_TO_WORD", "LTIME_TO_DWORD",
    "LTIME_TO_LWORD", "LTIME_TO_SINT", "LTIME_TO_USINT", "LTIME_TO_INT",
    "LTIME_TO_UINT", "LTIME_TO_DINT", "LTIME_TO_UDINT", "LTIME_TO_LINT",
    "LTIME_TO_ULINT", "LTIME_TO_REAL", "LTIME_TO_LREAL", "LTIME_TO_STRING",
    "LTIME_TO_WSTRING", "LTIME_TO_TIME",
    "STRING_TO_BOOL", "STRING_TO_BYTE", "STRING_TO_WORD", "STRING_TO_DWORD",
    "STRING_TO_LWORD", "STRING_TO_SINT", "STRING_TO_USINT", "STRING_TO_INT",
    "STRING_TO_UINT", "STRING_TO_DINT", "STRING_TO_UDINT", "STRING_TO_LINT",
    "STRING_TO_ULINT", "STRING_TO_REAL", "STRING_TO_LREAL", "STRING_TO_TIME",
    "STRING_TO_LTIME", "STRING_TO_WSTRING",
    "WSTRING_TO_BOOL", "WSTRING_TO_BYTE", "WSTRING_TO_WORD", "WSTRING_TO_DWORD",
    "WSTRING_TO_LWORD", "WSTRING_TO_SINT", "WSTRING_TO_USINT", "WSTRING_TO_INT",
    "WSTRING_TO_UINT", "WSTRING_TO_DINT", "WSTRING_TO_UDINT", "WSTRING_TO_LINT",
    "WSTRING_TO_ULINT", "WSTRING_TO_REAL", "WSTRING_TO_LREAL", "WSTRING_TO_TIME",
    "WSTRING_TO_LTIME", "WSTRING_TO_STRING",
    "DATE_TO_STRING", "DATE_TO_LDATE", "LDATE_TO_STRING", "LDATE_TO_DATE",
    "TOD_TO_STRING", "LTOD_TO_STRING", "TOD_TO_LTOD", "LTOD_TO_TOD",
    "DT_TO_STRING", "LDT_TO_STRING", "DT_TO_LDT", "LDT_TO_DT",
    "TIME_TO_REAL", "TIME_TO_LREAL",
    "ULINT_TO_TIME", "ULINT_TO_STRING",
    "UDINT_TO_DWORD", "UDINT_TO_STRING",
    "INT_TO_LINT", "LINT_TO_INT",
    "INT_TO_UINT", "UINT_TO_INT",
    "INT_TO_DINT", "DINT_TO_INT",
    "INT_TO_STRING", "STRING_TO_INT",
    "BOOL_TO_STRING", "DWORD_TO_STRING", "STRING_TO_DWORD",
    "BYTE_TO_STRING", "WORD_TO_STRING",
    "REAL_TO_ULINT", "REAL_TO_SINT", "REAL_TO_INT",
    "SINT_TO_REAL", "ULINT_TO_REAL",
    "TIME_TO_STRING", "ULINT_TO_TIME", "ULINT_TO_STRING",
])

# Standard library FBs/functions that are NOT project-defined types.
STANDARD_LIBRARY_FBS = frozenset([
    # Timers
    "TON", "TOF", "TP", "TONR",
    # Counters
    "CTU", "CTD", "CTUD",
    # Triggers / edge detection
    "R_TRIG", "F_TRIG", "RF_TRIG", "RS", "SR",
    # Selectors / mux / comparators
    "SEL", "MAX", "MIN", "LIMIT", "MUX",
    "GT", "GE", "EQ", "LE", "LT", "NE",
    # Math
    "ABS", "SQRT", "LN", "LOG", "EXP", "SIN", "COS", "TAN", "ASIN", "ACOS", "ATAN",
    # String operations
    "LEN", "LEFT", "RIGHT", "MID", "CONCAT", "INSERT", "DELETE", "REPLACE",
    "FIND", "UPPER", "LOWER", "TRIM",
    # Bit operations
    "SHL", "SHR", "ROL", "ROR",
    # SysLib / 3S specific
    "SysSockCreate", "SysSockBind", "SysSockListen", "SysSockAccept",
    "SysSockClose", "SysSockSend", "SysSockRecv",
    # Common built-ins
    "ADR", "SIZEOF",
    # C library functions that appear in ST
    "strcmp", "strcpy", "strlen", "memcmp", "memcpy",
])

# Common method/property names that are NOT project-defined types.
# These are names that appear as targets due to property_access or method_call
# patterns but are actually member names, not type names.
COMMON_MEMBER_NAMES = frozenset([
    "trigger", "test", "report", "configure", "describe", "execute",
    "reset", "starting", "overflow", "post", "pre", "inactive", "active",
    "mode", "request", "park", "unpark", "unlock", "recurse", "flag",
    "identifiers", "finish", "and", "defined", "good", "matchOption",
    "getToken", "getTokenForBool", "getTokenForUINT", "getTokenForUDINT",
    "getTokenForEnum", "getTokenForUDINT", "configureUDINT", "configureX",
    "clearCommand", "command", "executeAllCommands", "executeCommand",
    "executeContextFail", "fCheckDebugFlags", "defaultPersistence",
    "describeSyntaxExecutable", "lReadStream", "prompt",
    "getNextExecuteCommand", "registerOperational", "registerActive",
    "registerEnum", "defineOption_1", "registerEnum",
    "cycleOutput", "cycleOutputOff", "cycleStandby", "currentDerating",
    "processRequestedBMSState", "resolveRequestedBMSState",
    "resolveRequestedTMSState",
    "enableAndRequest", "getMode",
    "mapSpreader", "mapSteerA", "mapSteerB", "mapSteerC", "mapSteerD",
    "mapSteerAngleA", "mapSteerAngleB", "mapSteerAngleC", "mapSteerAngleD",
    "mapTransA", "mapTransB", "mapTransC", "mapTransD",
    "mapWinchA", "mapWinchB", "mapWinchC", "mapWinchD",
    "mapWinchAngleA", "mapWinchAngleB", "mapWinchAngleC", "mapWinchAngleD",
    "mapBMSA", "mapBMSB", "mapChargerA", "mapChargerB", "mapChargerC",
    "mapSecondaryPowerSupplyA", "mapSecondaryPowerSupplyB",
    "mapUInterfaceCabin", "mapUInterfaceRadio",
    "TransA", "TransB", "TransC", "TransD",
    "operatorA", "operatorB", "operatorAB", "operatorNull",
    "_operatorA", "_operatorB", "_operatorAB", "_operatorNull",
    "Mode", "mode",
    "Definition",
    "Client", "ClientA", "ClientB",
    "CurrentPacker", "Packer",
    "Peripheral",
])

# Regex pattern for local variable name prefixes (IEC convention).
# Variables starting with these prefixes followed by an uppercase letter are
# likely local variables, not project-defined types.
LOCAL_VAR_PREFIX_PATTERN = re.compile(
    r'^(l|r|s|b|i|di|w|dw|t|c|e|a|x|y|z|u)'  # prefix
    r'[A-Z]'                                     # followed by uppercase
    r'[A-Za-z0-9_]*$'                            # rest of identifier
)


# ---------------------------------------------------------------------------
# Filtering logic
# ---------------------------------------------------------------------------

def is_conversion_function(name):
    """Check if a name matches the *_TO_* conversion function pattern."""
    return "_TO_" in name


def is_local_variable_name(name, known_types):
    """Check if a name looks like a local variable (not a known project type)."""
    if name in known_types:
        return False
    return bool(LOCAL_VAR_PREFIX_PATTERN.match(name))


def should_filter_edge(edge, known_types):
    """Determine if an edge should be filtered out as a false positive.

    Returns (should_filter: bool, reason: str).
    """
    target = edge["target"]
    source = edge["source"]

    # 1. Self-references
    if source == target:
        return True, "self_reference"

    # 2. IEC keywords
    if target.upper() in IEC_KEYWORDS:
        return True, "iec_keyword"

    # 3. Conversion functions
    if is_conversion_function(target) or target in CONVERSION_FUNCTIONS:
        return True, "conversion_function"

    # 4. Standard library FBs/functions
    if target in STANDARD_LIBRARY_FBS:
        return True, "standard_library"

    # 5. Common member names (not project types)
    if target in COMMON_MEMBER_NAMES and target not in known_types:
        return True, "common_member_name"

    # 6. Local variable names (not in known type registry)
    if is_local_variable_name(target, known_types):
        return True, "local_variable_name"

    # 7. Unknown kind (not in POU_INDEX.json)
    # We check this via the known_types set — if target is not known, it's
    # likely a false positive from regex matching.
    if target not in known_types:
        return True, "unknown_type"

    return False, ""


# ---------------------------------------------------------------------------
# Confidence scoring
# ---------------------------------------------------------------------------

def compute_confidence(edge):
    """Compute a confidence score (0.0–1.0) for an edge.

    Scoring is based on provenance and implementation category strength.
    """
    provenance = edge["provenance"]
    impl_cats = edge.get("implementation_categories", [])
    iface_cats = edge.get("interface_categories", [])

    if provenance == "both":
        # Confirmed by both interface and implementation — highest confidence
        base = 0.95
        # Bonus for multiple implementation categories
        if len(impl_cats) >= 2:
            base = 0.98
        return round(base, 2), "high"

    elif provenance == "interface":
        # Compiler-enforced declaration — medium-high confidence
        base = 0.80
        # More interface contexts → slightly higher confidence
        if len(iface_cats) >= 2:
            base = 0.85
        return round(base, 2), "medium"

    elif provenance == "implementation":
        # Regex-inferred — lower confidence, sub-scored by category
        has_fb_call = "fb_call" in impl_cats
        has_impl_ref = "impl_ref" in impl_cats
        has_method_call = "method_call" in impl_cats
        has_property_access = "property_access" in impl_cats
        has_type_cast = "type_cast" in impl_cats

        if has_fb_call and has_impl_ref:
            # FB call + general reference — strongest impl signal
            return 0.65, "low"
        elif has_fb_call:
            # FB call alone — moderate impl signal
            return 0.60, "low"
        elif has_method_call and has_property_access:
            # Method + property on same object — good signal
            return 0.55, "low"
        elif has_method_call:
            # Method call — moderate signal
            return 0.50, "low"
        elif has_property_access:
            # Property access — weaker signal (could be any member)
            return 0.40, "low"
        elif has_impl_ref:
            # General reference — weak signal
            return 0.35, "low"
        elif has_type_cast:
            # Type cast only — weakest signal
            return 0.30, "low"
        else:
            return 0.30, "low"

    return 0.0, "unknown"


# ---------------------------------------------------------------------------
# Main cleaning pipeline
# ---------------------------------------------------------------------------

def load_json(path):
    """Load a JSON file."""
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_known_types(pou_index):
    """Build a set of all known POU and DUT names from POU_INDEX.json."""
    known = set()
    for file_entry in pou_index.get("files", []):
        for pou in file_entry.get("pous", []):
            known.add(pou["name"])
        for dut in file_entry.get("duts", []):
            known.add(dut["name"])
    return known


def clean_graph(unified_data, known_types):
    """Filter edges and assign confidence scores.

    Returns:
      - clean_edges: list of surviving edges with confidence scores
      - filter_stats: dict of filtering statistics
    """
    clean_edges = []
    filter_reasons = defaultdict(int)
    total_edges = len(unified_data["edges"])

    for edge in unified_data["edges"]:
        should_filter, reason = should_filter_edge(edge, known_types)
        if should_filter:
            filter_reasons[reason] += 1
            continue

        # Assign confidence score
        confidence, confidence_label = compute_confidence(edge)
        clean_edge = {
            "source": edge["source"],
            "target": edge["target"],
            "provenance": edge["provenance"],
            "confidence": confidence,
            "confidence_label": confidence_label,
            "source_kind": edge["source_kind"],
            "source_file": edge["source_file"],
            "interface_categories": edge["interface_categories"],
            "implementation_categories": edge["implementation_categories"],
        }
        clean_edges.append(clean_edge)

    filter_stats = {
        "total_input_edges": total_edges,
        "total_clean_edges": len(clean_edges),
        "total_filtered": total_edges - len(clean_edges),
        "filter_reasons": dict(sorted(filter_reasons.items(), key=lambda x: -x[1])),
    }

    return clean_edges, filter_stats


def build_clean_output(unified_data, clean_edges, filter_stats, known_types):
    """Assemble the CLEAN_DEPS.json output structure."""
    # Recompute summary stats on clean edges
    nodes = set()
    for edge in clean_edges:
        nodes.add(edge["source"])
        nodes.add(edge["target"])

    prov_counts = defaultdict(int)
    conf_counts = defaultdict(int)
    for edge in clean_edges:
        prov_counts[edge["provenance"]] += 1
        conf_counts[edge["confidence_label"]] += 1

    # Build adjacency for clean graph
    forward = defaultdict(set)
    reverse = defaultdict(set)
    for edge in clean_edges:
        forward[edge["source"]].add(edge["target"])
        reverse[edge["target"]].add(edge["source"])

    # Top nodes by degree in clean graph
    degree_list = []
    for node in nodes:
        in_deg = len(reverse.get(node, set()))
        out_deg = len(forward.get(node, set()))
        degree_list.append({
            "node": node,
            "total_degree": in_deg + out_deg,
            "fan_in": in_deg,
            "fan_out": out_deg,
        })
    degree_list.sort(key=lambda x: (-x["total_degree"], x["node"]))

    # Confidence distribution summary
    confidence_summary = {
        "high": {
            "count": conf_counts.get("high", 0),
            "description": "Confirmed by both interface and implementation",
        },
        "medium": {
            "count": conf_counts.get("medium", 0),
            "description": "Compiler-enforced interface declaration",
        },
        "low": {
            "count": conf_counts.get("low", 0),
            "description": "Regex-inferred from implementation code",
        },
    }

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": (
            "Cleaned dependency graph generated by scripts/clean_graph.py (Phase 5). "
            "Filters false positives from the Phase 4.5 unified graph and assigns "
            "confidence scores based on provenance and category strength."
        ),
        "source": "UNIFIED_DEPS.json (Phase 4.5)",
        "summary": {
            "total_nodes": len(nodes),
            "total_edges": len(clean_edges),
            "edges_by_provenance": dict(prov_counts),
            "edges_by_confidence": {
                k: v["count"] for k, v in confidence_summary.items()
            },
            "filter_stats": filter_stats,
        },
        "confidence_summary": confidence_summary,
        "top_nodes_by_degree": degree_list[:50],
        "edges": clean_edges,
    }


# ---------------------------------------------------------------------------
# Human-readable report
# ---------------------------------------------------------------------------

def build_clean_dependency_map(output, filter_stats, unified_data):
    """Generate a human-readable CLEAN_DEPENDENCY_MAP.md."""
    lines = []
    lines.append("# CLEAN_DEPENDENCY_MAP — Filtered & Scored Dependency Graph")
    lines.append("")
    lines.append("> Auto-generated by `scripts/clean_graph.py` (Phase 5). Do not edit manually.")
    lines.append("")
    lines.append("This document presents the **cleaned dependency graph** produced by")
    lines.append("filtering known false positives from the Phase 4.5 unified graph and")
    lines.append("assigning confidence scores to every surviving edge.")
    lines.append("")

    s = output["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| Total graph nodes (clean) | %d |" % s["total_nodes"])
    lines.append("| Total edges (clean) | %d |" % s["total_edges"])
    lines.append("| Edges removed (filtered) | %d |" % filter_stats["total_filtered"])
    lines.append("| Edges retained | %d |" % filter_stats["total_clean_edges"])
    lines.append("")

    # Filtering results
    lines.append("## Filtering Results")
    lines.append("")
    lines.append("The following categories of false positives were removed from the")
    lines.append("Phase 4.5 unified graph:")
    lines.append("")
    lines.append("| Filter Reason | Edges Removed | Description |")
    lines.append("|---|---|---|")

    reason_descriptions = {
        "unknown_type": "Target not found in POU/DUT registry (regex false positive)",
        "local_variable_name": "Target matches local variable naming convention (l*, r*, etc.)",
        "conversion_function": "Standard IEC type conversion function (*_TO_*)",
        "iec_keyword": "IEC 61131-3 language keyword (IF, CASE, AND, etc.)",
        "standard_library": "Standard library FB/function (TON, MAX, MIN, ADR, etc.)",
        "self_reference": "POU referencing itself (source == target)",
        "common_member_name": "Common method/property name, not a project-defined type",
    }

    for reason, count in filter_stats["filter_reasons"].items():
        desc = reason_descriptions.get(reason, reason)
        lines.append("| %s | %d | %s |" % (reason, count, desc))
    lines.append("")

    # Confidence distribution
    lines.append("## Confidence Distribution")
    lines.append("")
    lines.append("Every surviving edge is assigned a confidence score based on its")
    lines.append("provenance and the strength of the evidence:")
    lines.append("")
    lines.append("| Confidence | Score Range | Count | Description |")
    lines.append("|---|---|---|---|")

    conf = output["confidence_summary"]
    lines.append("| **high** | 0.95–1.00 | %d | Confirmed by both interface and implementation |" % conf["high"]["count"])
    lines.append("| **medium** | 0.70–0.94 | %d | Compiler-enforced interface declaration |" % conf["medium"]["count"])
    lines.append("| **low** | 0.30–0.69 | %d | Regex-inferred from implementation code |" % conf["low"]["count"])
    lines.append("")

    # Provenance breakdown
    lines.append("## Edges by Provenance (Clean Graph)")
    lines.append("")
    lines.append("| Provenance | Count | Description |")
    lines.append("|---|---|---|")

    prov = s["edges_by_provenance"]
    lines.append("| interface | %d | Declared in POU/DUT interface variables only |" % prov.get("interface", 0))
    lines.append("| implementation | %d | Found in ST implementation bodies only |" % prov.get("implementation", 0))
    lines.append("| both | %d | Present in both interface and implementation |" % prov.get("both", 0))
    lines.append("")

    # Signal improvement
    total_input = filter_stats["total_input_edges"]
    total_clean = filter_stats["total_clean_edges"]
    reduction_pct = (1.0 - total_clean / total_input) * 100 if total_input > 0 else 0
    lines.append("## Signal Improvement")
    lines.append("")
    lines.append("| Metric | Before (Phase 4.5) | After (Phase 5) | Change |")
    lines.append("|---|---|---|---|")
    lines.append("| Total edges | %d | %d | -%.1f%% |" % (total_input, total_clean, reduction_pct))
    lines.append("| Total nodes | %d | %d | — |" % (
        unified_data["summary"]["total_nodes"], s["total_nodes"]))
    lines.append("")
    lines.append("The cleaned graph removes **%.1f%%** of edges that were identified" % reduction_pct)
    lines.append("as false positives, significantly improving the signal-to-noise ratio")
    lines.append("for impact analysis and exploration.")
    lines.append("")

    # Top nodes by degree (clean)
    lines.append("## Top Nodes by Degree (Clean Graph)")
    lines.append("")
    lines.append("Nodes ranked by total degree in the **cleaned** graph.")
    lines.append("")
    lines.append("| Rank | Node | Total Degree | Fan-In | Fan-Out |")
    lines.append("|---|---|---|---|---|")

    for i, entry in enumerate(output["top_nodes_by_degree"][:30], 1):
        lines.append(
            "| %d | `%s` | %d | %d | %d |"
            % (i, entry["node"], entry["total_degree"], entry["fan_in"], entry["fan_out"])
        )
    lines.append("")

    # High-confidence edges
    high_edges = [e for e in output["edges"] if e["confidence_label"] == "high"]
    if high_edges:
        lines.append("## High-Confidence Edges (provenance = both)")
        lines.append("")
        lines.append("These edges are confirmed by **both** interface declarations and")
        lines.append("implementation usage — the most reliable dependencies in the graph.")
        lines.append("")
        lines.append("| Source | Target | Confidence | Interface Context | Implementation Context |")
        lines.append("|---|---|---|---|---|")

        for edge in sorted(high_edges, key=lambda e: (-e["confidence"], e["source"], e["target"])):
            iface_ctx = ", ".join(
                "%s.%s" % (c[0], c[1]) for c in edge["interface_categories"]
            ) if edge["interface_categories"] else "—"
            impl_ctx = ", ".join(edge["implementation_categories"]) if edge["implementation_categories"] else "—"
            lines.append(
                "| `%s` | `%s` | %.2f | %s | %s |"
                % (edge["source"], edge["target"], edge["confidence"], iface_ctx, impl_ctx)
            )
        lines.append("")

    # Medium-confidence edges (interface-only)
    medium_edges = [e for e in output["edges"] if e["confidence_label"] == "medium"]
    if medium_edges:
        lines.append("## Medium-Confidence Edges (interface-only)")
        lines.append("")
        lines.append("These edges come from **interface declarations** — compiler-enforced")
        lines.append("but not necessarily exercised in implementation code.")
        lines.append("")
        lines.append("| Source | Target | Confidence | Interface Context |")
        lines.append("|---|---|---|---|")

        for edge in sorted(medium_edges, key=lambda e: (-e["confidence"], e["source"], e["target"]))[:50]:
            iface_ctx = ", ".join(
                "%s.%s" % (c[0], c[1]) for c in edge["interface_categories"]
            ) if edge["interface_categories"] else "—"
            lines.append(
                "| `%s` | `%s` | %.2f | %s |"
                % (edge["source"], edge["target"], edge["confidence"], iface_ctx)
            )
        if len(medium_edges) > 50:
            lines.append("| ... | | | *(+%d more)* |" % (len(medium_edges) - 50))
        lines.append("")

    # Low-confidence edges summary
    low_edges = [e for e in output["edges"] if e["confidence_label"] == "low"]
    if low_edges:
        lines.append("## Low-Confidence Edges (implementation-only)")
        lines.append("")
        lines.append("These edges are inferred from **ST implementation code** via regex")
        lines.append("pattern matching. They represent behavioral dependencies that may")
        lines.append("or may not be genuine project-level couplings.")
        lines.append("")
        lines.append("### By Implementation Category")
        lines.append("")

        cat_counts = defaultdict(int)
        for edge in low_edges:
            for cat in edge["implementation_categories"]:
                cat_counts[cat] += 1

        lines.append("| Category | Edge Count |")
        lines.append("|---|---|")
        for cat in sorted(cat_counts.keys(), key=lambda c: -cat_counts[c]):
            lines.append("| %s | %d |" % (cat, cat_counts[cat]))
        lines.append("")

        # Top low-confidence targets
        target_counts = defaultdict(int)
        for edge in low_edges:
            target_counts[edge["target"]] += 1

        lines.append("### Most-Referenced Targets (Low Confidence)")
        lines.append("")
        lines.append("| Target | Referenced By (Impl) |")
        lines.append("|---|---|")
        for target, count in sorted(target_counts.items(), key=lambda x: -x[1])[:30]:
            lines.append("| `%s` | %d |" % (target, count))
        lines.append("")

    # Impact analysis on clean graph
    lines.append("## Clean Graph Impact Analysis")
    lines.append("")
    lines.append("Types ranked by fan-in in the **cleaned** graph. A change to any")
    lines.append("of these types affects the listed number of objects through")
    lines.append("verified dependency paths.")
    lines.append("")
    lines.append("| Rank | Type | Fan-In | Fan-Out | High-Conf Users |")
    lines.append("|---|---|---|---|---|")

    # Compute fan-in with high-confidence subset
    fan_in = defaultdict(int)
    fan_out = defaultdict(int)
    high_fan_in = defaultdict(int)
    for edge in output["edges"]:
        fan_in[edge["target"]] += 1
        fan_out[edge["source"]] += 1
        if edge["confidence_label"] == "high":
            high_fan_in[edge["target"]] += 1

    impact_sorted = sorted(
        [(node, fan_in.get(node, 0), fan_out.get(node, 0), high_fan_in.get(node, 0))
         for node in set(list(fan_in.keys()) + list(fan_out.keys()))],
        key=lambda x: (-x[1], x[0])
    )

    for i, (node, fi, fo, hfi) in enumerate(impact_sorted[:30], 1):
        if fi > 0:
            lines.append(
                "| %d | `%s` | %d | %d | %d |"
                % (i, node, fi, fo, hfi)
            )
    lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Update INDEX.json
# ---------------------------------------------------------------------------

def update_index_with_phase5(index_path):
    """Update INDEX.json to reference Phase 5 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    idx["phase5_artifacts"] = {
        "CLEAN_DEPS.json": (
            "Machine-readable cleaned dependency graph with false positives removed "
            "and confidence scores assigned to every edge. Filters IEC keywords, "
            "conversion functions, standard library items, local variable names, "
            "self-references, and unknown types."
        ),
        "CLEAN_DEPENDENCY_MAP.md": (
            "Human-readable report summarizing filtering results, confidence "
            "distribution, signal improvement metrics, and the cleaned dependency "
            "picture with impact analysis."
        ),
        "generated_by": "scripts/clean_graph.py",
        "description": (
            "Phase 5: Graph cleaning and confidence scoring. Filters false positives "
            "from the Phase 4.5 unified graph and assigns confidence scores based on "
            "provenance (high=both, medium=interface, low=implementation) and "
            "implementation category strength."
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
            "Clean the Phase 4.5 unified dependency graph by removing false "
            "positives and assigning confidence scores (Phase 5)."
        )
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 5 artifact references.",
    )
    args = parser.parse_args()

    export_dir = os.path.normpath(args.export_dir)

    if not os.path.isdir(export_dir):
        print("ERROR: Export directory not found: %s" % export_dir, file=sys.stderr)
        sys.exit(1)

    # Load prerequisites
    unified_path = os.path.join(export_dir, "UNIFIED_DEPS.json")
    pou_index_path = os.path.join(export_dir, "POU_INDEX.json")

    if not os.path.isfile(unified_path):
        print("ERROR: UNIFIED_DEPS.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/unify_deps.py first (Phase 4.5).", file=sys.stderr)
        sys.exit(1)

    if not os.path.isfile(pou_index_path):
        print("ERROR: POU_INDEX.json not found in %s" % export_dir, file=sys.stderr)
        print("Run scripts/index_xml.py first (Phase 2).", file=sys.stderr)
        sys.exit(1)

    print("Loading UNIFIED_DEPS.json ...")
    unified_data = load_json(unified_path)

    print("Loading POU_INDEX.json ...")
    pou_index = load_json(pou_index_path)

    # Build known type registry
    known_types = build_known_types(pou_index)
    print("  Known types: %d" % len(known_types))

    # Clean the graph
    print("Filtering false positives ...")
    clean_edges, filter_stats = clean_graph(unified_data, known_types)

    print("  Input edges:  %d" % filter_stats["total_input_edges"])
    print("  Filtered out: %d" % filter_stats["total_filtered"])
    print("  Clean edges:  %d" % filter_stats["total_clean_edges"])
    print("")
    print("  Filter breakdown:")
    for reason, count in filter_stats["filter_reasons"].items():
        print("    %-30s %d" % (reason, count))

    # Assign confidence scores (already done in clean_graph, but verify)
    print("\nAssigning confidence scores ...")
    conf_counts = defaultdict(int)
    for edge in clean_edges:
        conf_counts[edge["confidence_label"]] += 1
    for label in ["high", "medium", "low"]:
        print("  %-10s %d" % (label, conf_counts.get(label, 0)))

    # Build output
    print("\nAssembling CLEAN_DEPS.json ...")
    output = build_clean_output(unified_data, clean_edges, filter_stats, known_types)

    # Write CLEAN_DEPS.json
    clean_path = os.path.join(export_dir, "CLEAN_DEPS.json")
    with open(clean_path, "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Clean dependency graph written to: %s" % clean_path)

    # Build and write CLEAN_DEPENDENCY_MAP.md
    print("Generating CLEAN_DEPENDENCY_MAP.md ...")
    clean_map = build_clean_dependency_map(output, filter_stats, unified_data)
    map_path = os.path.join(export_dir, "CLEAN_DEPENDENCY_MAP.md")
    with open(map_path, "w", encoding="utf-8") as f:
        f.write(clean_map)
    print("Clean dependency map written to: %s" % map_path)

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_phase5(index_path)
        print("INDEX.json updated with Phase 5 artifact references.")

    # Print summary
    s = output["summary"]
    print("\nPhase 5 Summary:")
    print("  Clean graph nodes: %d" % s["total_nodes"])
    print("  Clean graph edges: %d" % s["total_edges"])
    print("  Edges filtered:    %d (%.1f%%)" % (
        filter_stats["total_filtered"],
        (filter_stats["total_filtered"] / filter_stats["total_input_edges"] * 100)
        if filter_stats["total_input_edges"] > 0 else 0
    ))
    print("  High confidence:   %d" % conf_counts.get("high", 0))
    print("  Medium confidence: %d" % conf_counts.get("medium", 0))
    print("  Low confidence:    %d" % conf_counts.get("low", 0))


if __name__ == "__main__":
    main()

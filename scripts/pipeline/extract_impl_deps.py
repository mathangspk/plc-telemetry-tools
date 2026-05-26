"""
extract_impl_deps.py — Phase 4: Implementation-level dependency extraction.

Reads POU_INDEX.json and the raw XML export files to extract dependencies from
ST (Structured Text) implementation bodies — method bodies, property accessors,
and POU bodies — that are NOT captured by interface-only analysis (Phase 3).

Produces:
  - IMPL_DEPS.json          — Machine-readable implementation-level dependency data.
  - IMPL_DEPENDENCY_MAP.md  — Human-readable implementation dependency analysis.

Usage:
    python scripts/extract_impl_deps.py exports/v1

This script is designed to run AFTER index_xml.py. It reads both POU_INDEX.json
(for the known type registry) and the raw XML files (for ST implementation bodies).

Phase 4 distinguishes clearly between:
  - "interface" dependencies: derived from VAR_INPUT/VAR_OUTPUT/VAR/etc. declarations
    (already captured by Phase 3 / build_xref.py).
  - "implementation" dependencies: discovered by scanning ST code bodies for
    FB/function calls, property accesses, method invocations, and local type refs.
"""

import argparse
import json
import os
import re
import sys
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime, timezone

# PLCopenXML namespace
NS = {"plc": "http://www.plcopen.org/xml/tc6_0200"}

# IEC 61131-3 primitive / built-in types — never treated as project dependencies.
PRIMITIVE_TYPES = frozenset(
    [
        "BOOL",
        "SINT",
        "USINT",
        "INT",
        "UINT",
        "DINT",
        "UDINT",
        "LINT",
        "ULINT",
        "REAL",
        "LREAL",
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
        "STRING",
        "WSTRING",
        "CHAR",
        "WCHAR",
        "BYTE",
        "WORD",
        "DWORD",
        "LWORD",
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

# IEC 61131-3 standard library FBs/functions that are NOT project-defined.
# These are excluded from project dependency graphs but tracked separately.
STANDARD_LIBRARY_NAMES = frozenset(
    [
        # Timers
        "TON",
        "TOF",
        "TP",
        "TONR",
        # Counters
        "CTU",
        "CTD",
        "CTUD",
        # Triggers / edge detection
        "R_TRIG",
        "F_TRIG",
        "RF_TRIG",
        "RS",
        "SR",
        # Selectors / mux
        "SEL",
        "MAX",
        "MIN",
        "LIMIT",
        "MUX",
        # Comparators
        "GT",
        "GE",
        "EQ",
        "LE",
        "LT",
        "NE",
        # Math
        "ABS",
        "SQRT",
        "LN",
        "LOG",
        "EXP",
        "SIN",
        "COS",
        "TAN",
        "ASIN",
        "ACOS",
        "ATAN",
        # Conversions (common ones)
        "INT_TO_REAL",
        "REAL_TO_INT",
        "DWORD_TO_STRING",
        "STRING_TO_DWORD",
        "INT_TO_STRING",
        "STRING_TO_INT",
        "BOOL_TO_STRING",
        # String operations
        "LEN",
        "LEFT",
        "RIGHT",
        "MID",
        "CONCAT",
        "INSERT",
        "DELETE",
        "REPLACE",
        "FIND",
        # Bit operations
        "SHL",
        "SHR",
        "ROL",
        "ROR",
        "AND",
        "OR",
        "XOR",
        "NOT",
        # SysLib / 3S specific (common)
        "SysSockCreate",
        "SysSockBind",
        "SysSockListen",
        "SysSockAccept",
        "SysSockClose",
        "SysSockSend",
        "SysSockRecv",
    ]
)


def is_primitive(type_name):
    """Check if a type name is an IEC primitive / built-in."""
    return type_name.upper() in PRIMITIVE_TYPES


def is_standard_library(name):
    """Check if a name is a known standard library FB/function."""
    return name in STANDARD_LIBRARY_NAMES


# ---------------------------------------------------------------------------
# ST code extraction from XML
# ---------------------------------------------------------------------------


def extract_st_from_element(elem):
    """Extract ST code text from a <body><ST><xhtml>...</xhtml></ST></body> subtree.

    Returns the raw ST string, or None if not found.
    """
    body = elem.find("plc:body", NS)
    if body is None:
        return None
    st_elem = body.find("plc:ST", NS)
    if st_elem is None:
        return None
    xhtml = st_elem.find("{http://www.w3.org/1999/xhtml}xhtml")
    if xhtml is None:
        # Try with namespace prefix
        xhtml = st_elem.find("plc:xhtml", NS)
    if xhtml is None:
        # Try any child
        for child in st_elem:
            tag = child.tag
            if "xhtml" in tag.lower():
                xhtml = child
                break
    if xhtml is None:
        return None

    # Get text content — may include HTML entities
    text = xhtml.text or ""
    # Also collect text from child elements (e.g., <br/>)
    for child in xhtml:
        if child.text:
            text += child.text
        if child.tail:
            text += child.tail

    # Decode common HTML entities
    text = text.replace("&lt;", "<").replace("&gt;", ">").replace("&amp;", "&")
    text = text.replace("&quot;", '"').replace("&#10;", "\n").replace("&#13;", "\r")

    return text.strip() if text.strip() else None


def extract_all_st_bodies(pou_elem):
    """Extract all ST code bodies from a POU element.

    Returns a list of dicts:
      { "context": str, "code": str }
    where context is like "POU:operator", "Method:initialize", "Property:GetAccessor", etc.
    """
    bodies = []

    # Main POU body
    main_code = extract_st_from_element(pou_elem)
    if main_code:
        bodies.append({"context": "POU:body", "code": main_code})

    # Methods in addData
    add_data = pou_elem.find("plc:addData", NS)
    if add_data is not None:
        for data_elem in add_data.findall("plc:data", NS):
            data_name = data_elem.get("name", "")

            # Methods
            if "method" in data_name.lower():
                for method in data_elem.findall("plc:Method", NS):
                    method_name = method.get("name", "unknown")
                    code = extract_st_from_element(method)
                    if code:
                        bodies.append(
                            {"context": "Method:%s" % method_name, "code": code}
                        )

            # Properties
            elif "property" in data_name.lower():
                for prop in data_elem.findall("plc:Property", NS):
                    prop_name = prop.get("name", "unknown")
                    # SetAccessor
                    set_acc = prop.find("plc:SetAccessor", NS)
                    if set_acc is not None:
                        code = extract_st_from_element(set_acc)
                        if code:
                            bodies.append(
                                {
                                    "context": "Property:%s:SetAccessor" % prop_name,
                                    "code": code,
                                }
                            )
                    # GetAccessor
                    get_acc = prop.find("plc:GetAccessor", NS)
                    if get_acc is not None:
                        code = extract_st_from_element(get_acc)
                        if code:
                            bodies.append(
                                {
                                    "context": "Property:%s:GetAccessor" % prop_name,
                                    "code": code,
                                }
                            )

    return bodies


# ---------------------------------------------------------------------------
# ST code analysis — pattern-based reference extraction
# ---------------------------------------------------------------------------

# IEC identifier: starts with letter or underscore, followed by alphanumerics or underscores.
IEC_IDENT = r"[A-Za-z_][A-Za-z0-9_]*"

# Patterns for extracting references from ST code.
# Each pattern returns a list of (reference_name, category) tuples.


def find_fb_function_calls(st_code):
    """Find FB instantiation calls and function invocations.

    Pattern: identifier( ... )
    Excludes: known IEC keywords, primitives, and common control-flow constructs.
    """
    calls = []
    # Match identifier followed by ( — but not preceded by . (that's a method call)
    # and not one of the excluded keywords.
    excluded = frozenset(
        [
            "IF",
            "ELSE",
            "ELSIF",
            "THEN",
            "END_IF",
            "FOR",
            "TO",
            "DO",
            "END_FOR",
            "WHILE",
            "END_WHILE",
            "REPEAT",
            "UNTIL",
            "END_REPEAT",
            "CASE",
            "OF",
            "END_CASE",
            "RETURN",
            "EXIT",
            "CONTINUE",
            "VAR",
            "END_VAR",
            "TRUE",
            "FALSE",
            "AND",
            "OR",
            "NOT",
            "XOR",
            "MOD",
            # Common conversion functions that are built-in
            "INT_TO_UINT",
            "UINT_TO_INT",
            "INT_TO_DINT",
            "DINT_TO_INT",
            "INT_TO_REAL",
            "REAL_TO_INT",
            "INT_TO_STRING",
            "STRING_TO_INT",
            "BOOL_TO_STRING",
            "DWORD_TO_STRING",
            "STRING_TO_DWORD",
            "BYTE_TO_STRING",
            "WORD_TO_STRING",
            "LEN",
            "LEFT",
            "RIGHT",
            "MID",
            "CONCAT",
            "INSERT",
            "DELETE",
            "REPLACE",
            "FIND",
            "UPPER",
            "LOWER",
            "TRIM",
            "ABS",
            "SQRT",
            "LN",
            "LOG",
            "EXP",
            "SIN",
            "COS",
            "TAN",
            "SHL",
            "SHR",
            "ROL",
            "ROR",
            "SIZEOF",
            "ADR",
        ]
    )

    # Pattern: word boundary + identifier + (  but NOT preceded by . or ^
    pattern = r"(?<![.\^])\b(" + IEC_IDENT + r")\s*\("
    for m in re.finditer(pattern, st_code):
        name = m.group(1)
        if name.upper() not in excluded and not is_primitive(name):
            calls.append((name, "fb_call"))
    return calls


def find_method_calls(st_code):
    """Find method invocations on objects.

    Pattern: identifier.identifier( ... )
    The first identifier is the object, the second is the method name.
    """
    calls = []
    # Match: identifier.identifier(
    pattern = r"\b(" + IEC_IDENT + r")\.(" + IEC_IDENT + r")\s*\("
    for m in re.finditer(pattern, st_code):
        obj_name = m.group(1)
        method_name = m.group(2)
        # We record the object reference (the method is resolved via the object's type)
        calls.append((obj_name, "method_call"))
    return calls


def find_property_accesses(st_code):
    """Find property accesses on objects.

    Pattern: identifier.identifier (without parentheses — not a method call)
    We look for dotted accesses that are NOT followed by ( and NOT part of a
    larger dotted chain (to avoid double-counting).
    """
    accesses = []
    # Match: identifier.identifier NOT followed by (
    # Use negative lookahead for (
    pattern = r"\b(" + IEC_IDENT + r")\.(" + IEC_IDENT + r")(?!\s*\()"
    for m in re.finditer(pattern, st_code):
        obj_name = m.group(1)
        prop_name = m.group(2)
        accesses.append((obj_name, "property_access"))
    return accesses


def find_type_references_in_declarations(st_code):
    """Find type references in local variable declarations within ST code.

    In CODESYS, local variables can be declared inline in some contexts.
    We look for patterns like:
      VAR ... identifier : TypeName ... END_VAR
    But more commonly, we look for type casts and explicit type usage:
      TypeName(identifier)  — type conversion
      identifier : TypeName  — variable declaration (in method interfaces embedded in XML)
    """
    refs = []
    # Type conversion / cast: TypeName(expression)
    # This overlaps with FB calls, so we only capture ones that look like conversions
    cast_pattern = r"\b(" + IEC_IDENT + r")\s*\(\s*(" + IEC_IDENT + r")\s*\)"
    for m in re.finditer(cast_pattern, st_code):
        type_name = m.group(1)
        if not is_primitive(type_name) and not is_standard_library(type_name):
            refs.append((type_name, "type_cast"))
    return refs


def find_named_references(st_code, known_types):
    """Find all identifiers in ST code that match known project types.

    This is a broad scan: any identifier that matches a known POU/DUT name
    and is not a primitive or standard library item.

    Categories:
      - "impl_ref": appears in implementation code (could be a variable of that type,
        a FB call, a type reference, etc.)
    """
    refs = []
    # Build a regex that matches any known type name as a whole word
    # Sort by length descending to match longer names first (avoid partial matches)
    sorted_types = sorted(known_types, key=len, reverse=True)
    if not sorted_types:
        return refs

    # Escape special regex chars in type names
    escaped = [re.escape(t) for t in sorted_types]
    pattern = r"\b(" + "|".join(escaped) + r")\b"

    for m in re.finditer(pattern, st_code):
        name = m.group(1)
        refs.append((name, "impl_ref"))

    return refs


def analyze_st_body(st_code, known_types):
    """Analyze a single ST code body and extract all implementation-level references.

    Returns a dict:
      {
        "fb_calls": [name, ...],
        "method_calls": [(object_name, ...)],
        "property_accesses": [(object_name, ...)],
        "type_casts": [name, ...],
        "impl_refs": [name, ...],
      }
    All names are deduplicated and filtered against known_types.
    """
    if not st_code:
        return {
            "fb_calls": [],
            "method_calls": [],
            "property_accesses": [],
            "type_casts": [],
            "impl_refs": [],
        }

    fb_calls = find_fb_function_calls(st_code)
    method_calls = find_method_calls(st_code)
    prop_accesses = find_property_accesses(st_code)
    type_casts = find_type_references_in_declarations(st_code)
    impl_refs = find_named_references(st_code, known_types)

    # Deduplicate
    def dedup(pairs):
        seen = set()
        result = []
        for name, cat in pairs:
            key = (name, cat)
            if key not in seen:
                seen.add(key)
                result.append(name)
        return result

    return {
        "fb_calls": dedup(fb_calls),
        "method_calls": dedup(method_calls),
        "property_accesses": dedup(prop_accesses),
        "type_casts": dedup(type_casts),
        "impl_refs": dedup(impl_refs),
    }


# ---------------------------------------------------------------------------
# XML file parsing for implementation bodies
# ---------------------------------------------------------------------------


def parse_xml_for_impl_bodies(filepath):
    """Parse a single XML file and extract all POU implementation bodies.

    Returns a list of dicts:
      {
        "pou_name": str,
        "pou_type": str,
        "bodies": [ { "context": str, "code": str }, ... ],
      }
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    results = []
    types_elem = root.find("plc:types", NS)
    if types_elem is None:
        return results

    pous_elem = types_elem.find("plc:pous", NS)
    if pous_elem is None:
        return results

    for pou in pous_elem.findall("plc:pou", NS):
        name = pou.get("name", "")
        pou_type = pou.get("pouType", "")
        bodies = extract_all_st_bodies(pou)
        if bodies:
            results.append(
                {
                    "pou_name": name,
                    "pou_type": pou_type,
                    "bodies": bodies,
                }
            )

    return results


# ---------------------------------------------------------------------------
# Build implementation dependency data
# ---------------------------------------------------------------------------


def build_impl_deps(export_dir, pou_index):
    """Build the full implementation-level dependency data structure.

    Reads XML files from export_dir/xml/ and cross-references against
    the known type registry from pou_index.

    Returns a dict suitable for JSON serialization.
    """
    xml_dir = os.path.join(export_dir, "xml")
    if not os.path.isdir(xml_dir):
        print("ERROR: XML directory not found: %s" % xml_dir, file=sys.stderr)
        sys.exit(1)

    # Build known type registry from POU_INDEX.json
    known_types = set()
    type_to_file = {}
    type_to_kind = {}
    type_to_pou_type = {}

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

    # Parse all XML files for implementation bodies
    xml_files = sorted(f for f in os.listdir(xml_dir) if f.lower().endswith(".xml"))

    # Per-POU implementation dependency data
    impl_deps = {}  # key: "POU:Name"
    # Aggregate stats
    total_bodies_analyzed = 0
    total_impl_refs_found = 0
    total_fb_calls_found = 0
    total_method_calls_found = 0
    total_property_accesses_found = 0
    total_type_casts_found = 0

    # Reverse map: type -> list of POUs that reference it in implementation
    impl_used_by = defaultdict(list)

    # Track which types are referenced ONLY in implementation (not in interface)
    impl_only_types = set()

    for fname in xml_files:
        fpath = os.path.join(xml_dir, fname)
        try:
            pou_bodies = parse_xml_for_impl_bodies(fpath)
        except Exception as e:
            print("  WARNING: Error parsing %s: %s" % (fname, e), file=sys.stderr)
            continue

        for pou_info in pou_bodies:
            pou_name = pou_info["pou_name"]
            key = "POU:%s" % pou_name

            # Collect all references across all bodies of this POU
            all_fb_calls = set()
            all_method_calls = set()
            all_prop_accesses = set()
            all_type_casts = set()
            all_impl_refs = set()
            body_details = []

            for body in pou_info["bodies"]:
                total_bodies_analyzed += 1
                analysis = analyze_st_body(body["code"], known_types)

                fb = set(analysis["fb_calls"])
                mc = set(analysis["method_calls"])
                pa = set(analysis["property_accesses"])
                tc = set(analysis["type_casts"])
                ir = set(analysis["impl_refs"])

                all_fb_calls |= fb
                all_method_calls |= mc
                all_prop_accesses |= pa
                all_type_casts |= tc
                all_impl_refs |= ir

                # Record per-body detail (only if there are references)
                if fb or mc or pa or tc or ir:
                    body_details.append(
                        {
                            "context": body["context"],
                            "fb_calls": sorted(fb),
                            "method_calls": sorted(mc),
                            "property_accesses": sorted(pa),
                            "type_casts": sorted(tc),
                            "impl_refs": sorted(ir),
                        }
                    )

            # Only record POUs that have implementation-level references
            if (
                all_fb_calls
                or all_method_calls
                or all_prop_accesses
                or all_type_casts
                or all_impl_refs
            ):
                impl_deps[key] = {
                    "file": fname,
                    "kind": "POU",
                    "pou_type": pou_info["pou_type"],
                    "total_bodies": len(pou_info["bodies"]),
                    "fb_calls": sorted(all_fb_calls),
                    "method_calls": sorted(all_method_calls),
                    "property_accesses": sorted(all_prop_accesses),
                    "type_casts": sorted(all_type_casts),
                    "impl_refs": sorted(all_impl_refs),
                    "body_details": body_details,
                }

                # Update aggregate stats
                total_fb_calls_found += len(all_fb_calls)
                total_method_calls_found += len(all_method_calls)
                total_property_accesses_found += len(all_prop_accesses)
                total_type_casts_found += len(all_type_casts)
                total_impl_refs_found += len(all_impl_refs)

                # Update reverse map
                all_refs = (
                    all_fb_calls
                    | all_method_calls
                    | all_prop_accesses
                    | all_type_casts
                    | all_impl_refs
                )
                for ref_name in all_refs:
                    if ref_name in known_types:
                        impl_used_by[ref_name].append(
                            {
                                "object": key,
                                "file": fname,
                            }
                        )

    # Determine impl-only types (referenced in impl but NOT in interface)
    # We need the interface-derived uses from XREF.json if available
    xref_path = os.path.join(export_dir, "XREF.json")
    interface_types = set()
    if os.path.isfile(xref_path):
        with open(xref_path, "r", encoding="utf-8") as f:
            xref = json.load(f)
        for obj_key, obj_data in xref.get("uses", {}).items():
            for type_name in obj_data.get("types", {}):
                interface_types.add(type_name)

    all_impl_referenced = set()
    for refs in impl_used_by.values():
        for r in refs:
            # The type name is the key in impl_used_by
            pass
    for type_name in impl_used_by:
        all_impl_referenced.add(type_name)

    impl_only_types = all_impl_referenced - interface_types

    # Build summary
    summary = {
        "total_xml_files_scanned": len(xml_files),
        "total_bodies_analyzed": total_bodies_analyzed,
        "total_pous_with_impl_deps": len(impl_deps),
        "total_fb_calls_found": total_fb_calls_found,
        "total_method_calls_found": total_method_calls_found,
        "total_property_accesses_found": total_property_accesses_found,
        "total_type_casts_found": total_type_casts_found,
        "total_impl_refs_found": total_impl_refs_found,
        "total_impl_referenced_types": len(all_impl_referenced),
        "impl_only_types_count": len(impl_only_types),
    }

    # Build impl_used_by output (sorted, deduplicated)
    impl_used_by_output = {}
    for type_name in sorted(impl_used_by.keys()):
        users = impl_used_by[type_name]
        seen = set()
        unique_users = []
        for u in users:
            if u["object"] not in seen:
                seen.add(u["object"])
                unique_users.append(u)
        impl_used_by_output[type_name] = unique_users

    # Build impl-only types list with details
    impl_only_list = []
    for type_name in sorted(impl_only_types):
        users = impl_used_by.get(type_name, [])
        impl_only_list.append(
            {
                "type": type_name,
                "used_by_count": len(users),
                "defined_in": type_to_file.get(type_name, "unknown"),
                "kind": type_to_kind.get(type_name, "unknown"),
            }
        )
    impl_only_list.sort(key=lambda x: (-x["used_by_count"], x["type"]))

    # Top impl-referenced types (by fan-in)
    top_impl_types = []
    for type_name in sorted(impl_used_by.keys(), key=lambda t: -len(impl_used_by[t])):
        users = impl_used_by[type_name]
        top_impl_types.append(
            {
                "type": type_name,
                "impl_used_by_count": len(users),
                "defined_in": type_to_file.get(type_name, "unknown"),
                "kind": type_to_kind.get(type_name, "unknown"),
            }
        )
    top_impl_types = top_impl_types[:50]

    return {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": (
            "Implementation-level dependency data generated by "
            "scripts/extract_impl_deps.py from XML ST bodies and POU_INDEX.json."
        ),
        "summary": summary,
        "impl_deps": impl_deps,
        "impl_used_by": impl_used_by_output,
        "top_impl_referenced_types": top_impl_types,
        "impl_only_types": impl_only_list,
    }


# ---------------------------------------------------------------------------
# Human-readable IMPL_DEPENDENCY_MAP.md
# ---------------------------------------------------------------------------


def build_impl_dependency_map(impl_data, pou_index):
    """Generate a human-readable IMPL_DEPENDENCY_MAP.md from implementation dependency data."""
    lines = []
    lines.append("# IMPL_DEPENDENCY_MAP — Implementation-Level Dependency Analysis")
    lines.append("")
    lines.append(
        "> Auto-generated by `scripts/extract_impl_deps.py`. Do not edit manually."
    )
    lines.append("")
    lines.append(
        "This document captures dependencies discovered by scanning **ST (Structured Text)"
    )
    lines.append(
        "implementation bodies** — method bodies, property accessors, and POU bodies."
    )
    lines.append(
        "These are **behavioral** dependencies (how code actually uses other objects)"
    )
    lines.append(
        "as opposed to **structural** dependencies from interface declarations"
    )
    lines.append("(VAR_INPUT, VAR_OUTPUT, VAR, etc.) captured in Phase 3.")
    lines.append("")

    s = impl_data["summary"]
    lines.append("## Summary")
    lines.append("")
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| XML files scanned | %d |" % s["total_xml_files_scanned"])
    lines.append("| ST bodies analyzed | %d |" % s["total_bodies_analyzed"])
    lines.append("| POUs with impl-level deps | %d |" % s["total_pous_with_impl_deps"])
    lines.append("| FB/function calls found | %d |" % s["total_fb_calls_found"])
    lines.append("| Method calls found | %d |" % s["total_method_calls_found"])
    lines.append(
        "| Property accesses found | %d |" % s["total_property_accesses_found"]
    )
    lines.append("| Type casts found | %d |" % s["total_type_casts_found"])
    lines.append("| Implementation refs found | %d |" % s["total_impl_refs_found"])
    lines.append("| Types referenced in impl | %d |" % s["total_impl_referenced_types"])
    lines.append("| Types referenced ONLY in impl | %d |" % s["impl_only_types_count"])
    lines.append("")

    # Structural vs Behavioral explanation
    lines.append("## Structural vs Behavioral Dependencies")
    lines.append("")
    lines.append("| Aspect | Structural (Phase 3) | Behavioral (Phase 4) |")
    lines.append("|---|---|---|")
    lines.append(
        "| Source | Interface declarations (VAR_*) | ST implementation bodies |"
    )
    lines.append(
        "| Captures | Declared variable types | FB calls, method calls, property accesses, type casts |"
    )
    lines.append(
        "| Certainty | Definite (compiler-enforced) | Inferred (regex-based pattern matching) |"
    )
    lines.append(
        "| Scope | POU/DUT interface only | All code including methods and properties |"
    )
    lines.append("")

    # Top impl-referenced types
    lines.append("## Most-Referenced Types in Implementation (Behavioral Fan-In)")
    lines.append("")
    lines.append("These types are referenced most often in ST implementation code.")
    lines.append("This shows which types are actually *used* in behavior, not just")
    lines.append("declared as variable types.")
    lines.append("")
    lines.append("| Type | Kind | Defined In | Impl References |")
    lines.append("|---|---|---|---|")

    for entry in impl_data["top_impl_referenced_types"][:30]:
        lines.append(
            "| `%s` | %s | %s | %d |"
            % (
                entry["type"],
                entry["kind"],
                entry["defined_in"],
                entry["impl_used_by_count"],
            )
        )
    lines.append("")

    # Impl-only types
    if impl_data["impl_only_types"]:
        lines.append("## Types Referenced ONLY in Implementation (Not in Interface)")
        lines.append("")
        lines.append("These types are used in ST code bodies but are NOT declared as")
        lines.append("variable types in any POU interface. They may be:")
        lines.append("- Local variable types inside method bodies")
        lines.append("- FB instances created inline")
        lines.append("- Type casts or conversions")
        lines.append("- Helper types used only in implementation logic")
        lines.append("")
        lines.append("| Type | Kind | Defined In | Used By (Impl) |")
        lines.append("|---|---|---|---|")

        for entry in impl_data["impl_only_types"][:30]:
            lines.append(
                "| `%s` | %s | %s | %d |"
                % (
                    entry["type"],
                    entry["kind"],
                    entry["defined_in"],
                    entry["used_by_count"],
                )
            )
        lines.append("")

    # Per-POU implementation detail
    lines.append("## Implementation Dependency Detail by Object")
    lines.append("")

    # Group by file
    impl_deps = impl_data["impl_deps"]
    files_map = defaultdict(list)
    for key, entry in impl_deps.items():
        files_map[entry["file"]].append((key, entry))

    for filename in sorted(files_map.keys()):
        lines.append("### %s" % filename)
        lines.append("")

        entries = sorted(files_map[filename], key=lambda x: x[0])
        for key, entry in entries:
            name = key.split(":", 1)[1]
            pou_type = entry.get("pou_type", "")

            lines.append("#### `%s` (%s)" % (name, pou_type))
            lines.append("")
            lines.append("- **ST bodies analyzed:** %d" % entry["total_bodies"])

            if entry["fb_calls"]:
                lines.append(
                    "- **FB/function calls:** %s"
                    % ", ".join("`%s`" % t for t in entry["fb_calls"][:20])
                )
                if len(entry["fb_calls"]) > 20:
                    lines.append("  *(+%d more)*" % (len(entry["fb_calls"]) - 20))

            if entry["method_calls"]:
                lines.append(
                    "- **Method call targets:** %s"
                    % ", ".join("`%s`" % t for t in entry["method_calls"][:20])
                )
                if len(entry["method_calls"]) > 20:
                    lines.append("  *(+%d more)*" % (len(entry["method_calls"]) - 20))

            if entry["property_accesses"]:
                lines.append(
                    "- **Property access targets:** %s"
                    % ", ".join("`%s`" % t for t in entry["property_accesses"][:20])
                )
                if len(entry["property_accesses"]) > 20:
                    lines.append(
                        "  *(+%d more)*" % (len(entry["property_accesses"]) - 20)
                    )

            if entry["type_casts"]:
                lines.append(
                    "- **Type casts:** %s"
                    % ", ".join("`%s`" % t for t in entry["type_casts"][:20])
                )
                if len(entry["type_casts"]) > 20:
                    lines.append("  *(+%d more)*" % (len(entry["type_casts"]) - 20))

            if entry["impl_refs"]:
                lines.append(
                    "- **Implementation refs:** %s"
                    % ", ".join("`%s`" % t for t in entry["impl_refs"][:30])
                )
                if len(entry["impl_refs"]) > 30:
                    lines.append("  *(+%d more)*" % (len(entry["impl_refs"]) - 30))

            lines.append("")

            # Show body-level detail for the first few bodies with references
            if entry.get("body_details"):
                lines.append("<details>")
                lines.append(
                    "<summary>Body-level detail (%d bodies with refs)</summary>"
                    % len(entry["body_details"])
                )
                lines.append("")
                for bd in entry["body_details"][:10]:
                    lines.append("**%s:**" % bd["context"])
                    if bd["fb_calls"]:
                        lines.append(
                            "- FB calls: %s"
                            % ", ".join("`%s`" % t for t in bd["fb_calls"])
                        )
                    if bd["method_calls"]:
                        lines.append(
                            "- Method calls: %s"
                            % ", ".join("`%s`" % t for t in bd["method_calls"])
                        )
                    if bd["property_accesses"]:
                        lines.append(
                            "- Property accesses: %s"
                            % ", ".join("`%s`" % t for t in bd["property_accesses"])
                        )
                    if bd["type_casts"]:
                        lines.append(
                            "- Type casts: %s"
                            % ", ".join("`%s`" % t for t in bd["type_casts"])
                        )
                    if bd["impl_refs"]:
                        lines.append(
                            "- Impl refs: %s"
                            % ", ".join("`%s`" % t for t in bd["impl_refs"][:15])
                        )
                    lines.append("")
                if len(entry["body_details"]) > 10:
                    lines.append(
                        "*(+%d more bodies)*" % (len(entry["body_details"]) - 10)
                    )
                    lines.append("")
                lines.append("</details>")
                lines.append("")

        lines.append("---")
        lines.append("")

    # Impact analysis: what impl-level changes affect
    lines.append("## Implementation Impact Analysis")
    lines.append("")
    lines.append("If you change a type that is referenced in implementation code,")
    lines.append(
        "the following POUs may be affected (beyond their interface dependencies)."
    )
    lines.append("")

    # Show types with high impl fan-in
    high_impl_impact = [
        e
        for e in impl_data["top_impl_referenced_types"]
        if e["impl_used_by_count"] >= 5
    ]
    if high_impl_impact:
        for entry in high_impl_impact[:15]:
            type_name = entry["type"]
            users = impl_data["impl_used_by"].get(type_name, [])
            lines.append(
                "### `%s` (referenced in impl by %d POUs)"
                % (type_name, entry["impl_used_by_count"])
            )
            lines.append("")
            lines.append(
                "Kind: %s | Defined in: `%s`" % (entry["kind"], entry["defined_in"])
            )
            lines.append("")
            lines.append("POUs that reference this type in implementation:")
            lines.append("")
            for u in sorted(users, key=lambda x: x["object"]):
                obj_name = u["object"].split(":", 1)[1]
                lines.append("- `%s`" % obj_name)
            lines.append("")
    else:
        lines.append("No types are referenced in implementation by 5 or more POUs.")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Update INDEX.json
# ---------------------------------------------------------------------------


def update_index_with_phase4(index_path):
    """Update INDEX.json to reference Phase 4 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    idx["phase4_artifacts"] = {
        "IMPL_DEPS.json": (
            "Machine-readable implementation-level dependency data extracted from "
            "ST code bodies (FB calls, method calls, property accesses, type casts, "
            "and general implementation references)."
        ),
        "IMPL_DEPENDENCY_MAP.md": (
            "Human-readable implementation dependency analysis with structural vs "
            "behavioral comparison, impl-only types, per-POU detail, and impact analysis."
        ),
        "generated_by": "scripts/extract_impl_deps.py",
        "description": (
            "Phase 4: Implementation-level dependency extraction from ST code bodies. "
            "Distinguishes behavioral dependencies (from implementation) from structural "
            "dependencies (from interface declarations)."
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
            "Extract implementation-level dependencies from ST code bodies "
            "(Phase 4)."
        )
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 4 artifact references.",
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

    print("Extracting implementation-level dependencies ...")
    impl_data = build_impl_deps(export_dir, pou_index)

    # Write IMPL_DEPS.json
    impl_deps_path = os.path.join(export_dir, "IMPL_DEPS.json")
    with open(impl_deps_path, "w", encoding="utf-8") as f:
        json.dump(impl_data, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("Implementation dependencies written to: %s" % impl_deps_path)

    # Build and write IMPL_DEPENDENCY_MAP.md
    print("Generating IMPL_DEPENDENCY_MAP.md ...")
    impl_map = build_impl_dependency_map(impl_data, pou_index)
    impl_map_path = os.path.join(export_dir, "IMPL_DEPENDENCY_MAP.md")
    with open(impl_map_path, "w", encoding="utf-8") as f:
        f.write(impl_map)
    print("Implementation dependency map written to: %s" % impl_map_path)

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_phase4(index_path)
        print("INDEX.json updated with Phase 4 artifact references.")

    # Print summary
    s = impl_data["summary"]
    print("\nPhase 4 Summary:")
    print("  XML files scanned: %d" % s["total_xml_files_scanned"])
    print("  ST bodies analyzed: %d" % s["total_bodies_analyzed"])
    print("  POUs with impl-level deps: %d" % s["total_pous_with_impl_deps"])
    print("  FB/function calls found: %d" % s["total_fb_calls_found"])
    print("  Method calls found: %d" % s["total_method_calls_found"])
    print("  Property accesses found: %d" % s["total_property_accesses_found"])
    print("  Type casts found: %d" % s["total_type_casts_found"])
    print("  Implementation refs found: %d" % s["total_impl_refs_found"])
    print("  Types referenced in impl: %d" % s["total_impl_referenced_types"])
    print("  Types referenced ONLY in impl: %d" % s["impl_only_types_count"])

    if impl_data["top_impl_referenced_types"]:
        print("\n  Top 10 most-referenced types in implementation:")
        for entry in impl_data["top_impl_referenced_types"][:10]:
            print(
                "    %-45s  %d POUs  (%s)"
                % (entry["type"], entry["impl_used_by_count"], entry["kind"])
            )

    if impl_data["impl_only_types"]:
        print("\n  Top 10 types referenced ONLY in implementation (not in interface):")
        for entry in impl_data["impl_only_types"][:10]:
            print(
                "    %-45s  %d POUs  (%s in %s)"
                % (
                    entry["type"],
                    entry["used_by_count"],
                    entry["kind"],
                    entry["defined_in"],
                )
            )


if __name__ == "__main__":
    main()

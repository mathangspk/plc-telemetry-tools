"""
index_xml.py — Lightweight XML POU/DUT indexer for CODESYS PLCopenXML export snapshots.

Parses all .xml files under exports/<version>/xml/ and produces:
  - POU_INDEX.json  — structured JSON index of every POU, DUT, and library reference
  - PROJECT_MAP.md  — human-readable markdown map of the codebase structure
  - Updates MANIFEST.json with accurate total_pou_count and total_dut_count

Phase 2.5 adds POU interface/variable extraction (VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT,
VAR, VAR_GLOBAL, and function return types).

Usage:
    python scripts/index_xml.py exports/v1

Example:
    python scripts/index_xml.py exports/v1
"""

import argparse
import json
import os
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# PLCopenXML namespace
NS = {"plc": "http://www.plcopen.org/xml/tc6_0200"}

# Mapping from PLCopenXML interface element names to IEC variable categories
INTERFACE_SECTION_MAP = {
    "inputVars": "VAR_INPUT",
    "outputVars": "VAR_OUTPUT",
    "inOutVars": "VAR_IN_OUT",
    "localVars": "VAR",
    "globalVars": "VAR_GLOBAL",
    "tempVars": "VAR_TEMP",
    "externalVars": "VAR_EXTERNAL",
    "accessVars": "VAR_ACCESS",
}


def parse_xml_file(filepath):
    """Parse a single PLCopenXML file and extract POU/DUT/library info."""
    tree = ET.parse(filepath)
    root = tree.getroot()

    filename = os.path.basename(filepath)
    result = {
        "filename": filename,
        "content_header": {},
        "pous": [],
        "duts": [],
        "libraries": [],
    }

    # Content header
    ch = root.find("plc:contentHeader", NS)
    if ch is not None:
        result["content_header"] = {
            "name": ch.get("name", ""),
            "version": ch.get("version", ""),
            "modificationDateTime": ch.get("modificationDateTime", ""),
            "organization": ch.get("organization", ""),
        }

    # File header
    fh = root.find("plc:fileHeader", NS)
    if fh is not None:
        result["content_header"]["productVersion"] = fh.get("productVersion", "")
        result["content_header"]["creationDateTime"] = fh.get("creationDateTime", "")

    # DUTs (dataTypes)
    types_elem = root.find("plc:types", NS)
    if types_elem is not None:
        dtypes = types_elem.find("plc:dataTypes", NS)
        if dtypes is not None:
            for dt in dtypes.findall("plc:dataType", NS):
                name = dt.get("name", "")
                base_type = _extract_base_type(dt)
                result["duts"].append({
                    "name": name,
                    "base_type": base_type,
                })

    # POUs
    if types_elem is not None:
        pous_elem = types_elem.find("plc:pous", NS)
        if pous_elem is not None:
            for pou in pous_elem.findall("plc:pou", NS):
                name = pou.get("name", "")
                pou_type = pou.get("pouType", "")
                methods = []
                properties = []

                # Methods
                for method in pou.findall("plc:method", NS):
                    methods.append(method.get("name", ""))

                # Properties
                for prop in pou.findall("plc:property", NS):
                    properties.append(prop.get("name", ""))

                pou_info = {
                    "name": name,
                    "pou_type": pou_type,
                }
                if methods:
                    pou_info["methods"] = methods
                if properties:
                    pou_info["properties"] = properties

                # Phase 2.5: Extract interface/variable information
                interface = _extract_interface(pou)
                if interface is not None:
                    pou_info["interface"] = interface

                result["pous"].append(pou_info)

    # Library references — search in two locations:
    # 1. project/addData/data (library exports)
    # 2. project/instances/configurations/configuration/resource/addData/data (main project)
    def _extract_libs_from_add_data(add_data_elem):
        """Extract libraries from an addData element."""
        libs_found = []
        if add_data_elem is None:
            return libs_found
        for data_elem in add_data_elem.findall("plc:data", NS):
            if data_elem.get("name", "").endswith("libraries"):
                libs = data_elem.find("plc:Libraries", NS)
                if libs is not None:
                    for lib in libs.findall("plc:Library", NS):
                        libs_found.append(_extract_library(lib))
        return libs_found

    # Location 1: root-level addData
    add_data = root.find("plc:addData", NS)
    result["libraries"] = _extract_libs_from_add_data(add_data)

    # Location 2: instances/configurations/configuration/resource/addData
    instances = root.find("plc:instances", NS)
    if instances is not None:
        configs = instances.find("plc:configurations", NS)
        if configs is not None:
            config = configs.find("plc:configuration", NS)
            if config is not None:
                resource = config.find("plc:resource", NS)
                if resource is not None:
                    res_add_data = resource.find("plc:addData", NS)
                    result["libraries"].extend(_extract_libs_from_add_data(res_add_data))

    return result


def _extract_base_type(dataType_elem):
    """Extract a human-readable base type from a dataType element."""
    base = dataType_elem.find("plc:baseType", NS)
    if base is None:
        return "unknown"

    # Check for derived type
    derived = base.find("plc:derived", NS)
    if derived is not None:
        return derived.get("name", "derived")

    # Check for enum
    if base.find("plc:enum", NS) is not None:
        enum_elem = base.find("plc:enum", NS)
        values = enum_elem.find("plc:values", NS)
        count = len(values.findall("plc:value", NS)) if values is not None else 0
        return "enum (%d values)" % count

    # Check for array
    if base.find("plc:array", NS) is not None:
        arr = base.find("plc:array", NS)
        dim = arr.find("plc:dimension", NS)
        if dim is not None:
            lower = dim.get("lower", "?")
            upper = dim.get("upper", "?")
            inner = _extract_base_type_from_element(arr)
            return "array [%s..%s] of %s" % (lower, upper, inner)
        return "array"

    # Check for struct
    if base.find("plc:struct", NS) is not None:
        members = base.find("plc:struct", NS).findall("plc:variable", NS)
        return "struct (%d members)" % len(members)

    # Check for pointer
    if base.find("plc:pointer", NS) is not None:
        ptr = base.find("plc:pointer", NS)
        inner = _extract_base_type_from_element(ptr)
        return "pointer to %s" % inner

    # Check for string
    string_elem = base.find("plc:string", NS)
    if string_elem is not None:
        length = string_elem.get("length", "")
        return "STRING(%s)" % length if length else "STRING"

    # Check for wstring
    wstring_elem = base.find("plc:wstring", NS)
    if wstring_elem is not None:
        length = wstring_elem.get("length", "")
        return "WSTRING(%s)" % length if length else "WSTRING"

    # Primitive type (BOOL, INT, REAL, TIME, etc.)
    for child in base:
        tag = child.tag
        # Strip namespace
        if "}" in tag:
            tag = tag.split("}")[1]
        if tag and tag[0].isupper():
            return tag

    return "unknown"


def _extract_base_type_from_element(parent_elem):
    """Recursively extract base type from nested elements (array, pointer, etc.)."""
    base = parent_elem.find("plc:baseType", NS)
    if base is not None:
        return _extract_base_type_from_element(base)

    derived = parent_elem.find("plc:derived", NS)
    if derived is not None:
        return derived.get("name", "derived")

    for child in parent_elem:
        tag = child.tag
        if "}" in tag:
            tag = tag.split("}")[1]
        if tag and tag[0].isupper():
            return tag

    return "unknown"


def _extract_library(lib_elem):
    """Extract library reference info."""
    return {
        "name": lib_elem.get("Name", ""),
        "namespace": lib_elem.get("Namespace", ""),
        "system_library": lib_elem.get("SystemLibrary", "false") == "true",
        "link_all": lib_elem.get("LinkAllContent", "false") == "true",
    }


def _type_to_string(type_elem):
    """Convert a PLCopenXML <type> element to a human-readable type string.

    Handles: primitives (BOOL, INT, ...), derived types, arrays, pointers,
    strings, wstrings, and references.
    """
    if type_elem is None:
        return "unknown"

    for child in type_elem:
        tag = child.tag
        if "}" in tag:
            tag = tag.split("}")[1]

        if tag == "derived":
            return child.get("name", "derived")

        if tag == "array":
            dims = child.findall("plc:dimension", NS)
            dim_strs = []
            for d in dims:
                dim_strs.append("%s..%s" % (d.get("lower", "?"), d.get("upper", "?")))
            inner_base = child.find("plc:baseType", NS)
            inner = _type_to_string(inner_base)
            return "ARRAY [%s] OF %s" % (", ".join(dim_strs), inner)

        if tag == "pointer":
            inner_base = child.find("plc:baseType", NS)
            inner = _type_to_string(inner_base)
            return "POINTER TO %s" % inner

        if tag == "string":
            length = child.get("length", "")
            return "STRING(%s)" % length if length else "STRING"

        if tag == "wstring":
            length = child.get("length", "")
            return "WSTRING(%s)" % length if length else "WSTRING"

        # Primitive type (BOOL, INT, REAL, TIME, etc.)
        if tag and tag[0].isupper():
            return tag

    return "unknown"


def _extract_initial_value(variable_elem):
    """Extract the initial value from a variable element, if present."""
    init = variable_elem.find("plc:initialValue", NS)
    if init is None:
        return None
    sv = init.find("plc:simpleValue", NS)
    if sv is not None:
        return sv.get("value", "")
    return None


def _extract_interface(pou_elem):
    """Extract POU interface information (variables by category + return type).

    Returns a dict with keys matching IEC variable categories (VAR_INPUT,
    VAR_OUTPUT, etc.) and optionally 'returnType' for Function POUs.
    Each variable entry contains: name, type, and optionally initial_value.
    """
    iface = pou_elem.find("plc:interface", NS)
    if iface is None:
        return None

    result = {}

    # Variable sections
    for xml_tag, iec_category in INTERFACE_SECTION_MAP.items():
        section = iface.find("plc:%s" % xml_tag, NS)
        if section is None:
            continue
        variables = []
        for var in section.findall("plc:variable", NS):
            var_name = var.get("name", "")
            type_elem = var.find("plc:type", NS)
            var_type = _type_to_string(type_elem)
            var_info = {"name": var_name, "type": var_type}
            init_val = _extract_initial_value(var)
            if init_val is not None:
                var_info["initial_value"] = init_val
            variables.append(var_info)
        if variables:
            result[iec_category] = variables

    # Function return type
    ret_type = iface.find("plc:returnType", NS)
    if ret_type is not None:
        result["returnType"] = _type_to_string(ret_type)

    return result if result else None


def build_pou_index(file_results):
    """Build the full POU_INDEX.json structure."""
    index = {
        "generated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "description": "POU/DUT index generated by scripts/index_xml.py from PLCopenXML export files.",
        "summary": {
            "total_files": len(file_results),
            "total_pous": 0,
            "total_duts": 0,
            "total_libraries": 0,
            "pou_types": {},
            "dut_base_types": {},
            "pous_with_interface": 0,
            "total_interface_variables": 0,
            "interface_variable_categories": {},
        },
        "files": [],
    }

    all_libraries = set()

    for fr in file_results:
        file_entry = {
            "filename": fr["filename"],
            "name": fr["content_header"].get("name", ""),
            "version": fr["content_header"].get("version", ""),
            "organization": fr["content_header"].get("organization", ""),
            "pou_count": len(fr["pous"]),
            "dut_count": len(fr["duts"]),
            "library_count": len(fr["libraries"]),
            "pous": fr["pous"],
            "duts": fr["duts"],
            "libraries": fr["libraries"],
        }
        index["files"].append(file_entry)

        index["summary"]["total_pous"] += len(fr["pous"])
        index["summary"]["total_duts"] += len(fr["duts"])

        # Count POU types
        for pou in fr["pous"]:
            pt = pou["pou_type"]
            index["summary"]["pou_types"][pt] = index["summary"]["pou_types"].get(pt, 0) + 1

            # Phase 2.5: Count interface variables
            iface = pou.get("interface")
            if iface is not None:
                index["summary"]["pous_with_interface"] += 1
                for cat, vars_list in iface.items():
                    if cat == "returnType":
                        continue
                    count = len(vars_list)
                    index["summary"]["total_interface_variables"] += count
                    index["summary"]["interface_variable_categories"][cat] = (
                        index["summary"]["interface_variable_categories"].get(cat, 0) + count
                    )

        # Count DUT base types
        for dut in fr["duts"]:
            bt = dut["base_type"]
            # Normalize: strip parenthetical details for grouping
            base_category = bt.split(" (")[0] if " (" in bt else bt
            index["summary"]["dut_base_types"][base_category] = (
                index["summary"]["dut_base_types"].get(base_category, 0) + 1
            )

        # Collect unique libraries
        for lib in fr["libraries"]:
            all_libraries.add(lib["name"])

    index["summary"]["total_libraries"] = len(all_libraries)
    index["unique_libraries"] = sorted(all_libraries)

    return index


def build_project_map(index):
    """Generate a human-readable PROJECT_MAP.md from the POU index."""
    lines = []
    lines.append("# PROJECT_MAP — CODESYS PLC Codebase Structure")
    lines.append("")
    lines.append("> Auto-generated by `scripts/index_xml.py`. Do not edit manually.")
    lines.append("")
    lines.append("## Summary")
    lines.append("")
    s = index["summary"]
    lines.append("| Metric | Count |")
    lines.append("|---|---|")
    lines.append("| XML files | %d |" % s["total_files"])
    lines.append("| Total POUs | %d |" % s["total_pous"])
    lines.append("| Total DUTs | %d |" % s["total_duts"])
    lines.append("| Unique library references | %d |" % s["total_libraries"])
    if s.get("pous_with_interface"):
        lines.append("| POUs with interface info | %d |" % s["pous_with_interface"])
        lines.append("| Total interface variables | %d |" % s["total_interface_variables"])
    lines.append("")

    # POU type breakdown
    lines.append("### POU Types")
    lines.append("")
    lines.append("| Type | Count |")
    lines.append("|---|---|")
    for pt, count in sorted(s["pou_types"].items(), key=lambda x: -x[1]):
        lines.append("| %s | %d |" % (pt, count))
    lines.append("")

    # DUT base type breakdown
    lines.append("### DUT Base Types")
    lines.append("")
    lines.append("| Base Type | Count |")
    lines.append("|---|---|")
    for bt, count in sorted(s["dut_base_types"].items(), key=lambda x: -x[1]):
        lines.append("| %s | %d |" % (bt, count))
    lines.append("")

    # Phase 2.5: Interface variable category breakdown
    if s.get("interface_variable_categories"):
        lines.append("### Interface Variable Categories")
        lines.append("")
        lines.append("| Category | Variables |")
        lines.append("|---|---|")
        for cat, count in sorted(s["interface_variable_categories"].items(), key=lambda x: -x[1]):
            lines.append("| %s | %d |" % (cat, count))
        lines.append("")

    # Unique libraries
    lines.append("### Unique Library References")
    lines.append("")
    for lib in index["unique_libraries"]:
        lines.append("- `%s`" % lib)
    lines.append("")

    # Per-file detail
    lines.append("## File Detail")
    lines.append("")

    for f in index["files"]:
        lines.append("### %s" % f["filename"])
        lines.append("")
        lines.append("- **Name:** %s" % f["name"])
        if f["version"]:
            lines.append("- **Version:** %s" % f["version"])
        if f["organization"]:
            lines.append("- **Organization:** %s" % f["organization"])
        lines.append("- **POUs:** %d" % f["pou_count"])
        lines.append("- **DUTs:** %d" % f["dut_count"])
        lines.append("- **Library refs:** %d" % f["library_count"])
        lines.append("")

        if f["pous"]:
            lines.append("#### POUs")
            lines.append("")
            lines.append("| Name | Type | Interface | Methods | Properties |")
            lines.append("|---|---|---|---|---|")
            for pou in f["pous"]:
                methods = ", ".join(pou.get("methods", []))
                properties = ", ".join(pou.get("properties", []))
                methods_display = methods if methods else "—"
                properties_display = properties if properties else "—"

                # Phase 2.5: Interface summary
                iface = pou.get("interface")
                iface_display = "—"
                if iface is not None:
                    parts = []
                    for cat in ["VAR_INPUT", "VAR_OUTPUT", "VAR_IN_OUT", "VAR", "VAR_GLOBAL"]:
                        if cat in iface:
                            parts.append("%s=%d" % (cat, len(iface[cat])))
                    if "returnType" in iface:
                        parts.append("-> %s" % iface["returnType"])
                    iface_display = ", ".join(parts) if parts else "—"

                lines.append(
                    "| `%s` | %s | %s | %s | %s |"
                    % (pou["name"], pou["pou_type"], iface_display, methods_display, properties_display)
                )
            lines.append("")

        if f["duts"]:
            lines.append("#### DUTs")
            lines.append("")
            lines.append("| Name | Base Type |")
            lines.append("|---|---|")
            for dut in f["duts"]:
                lines.append("| `%s` | %s |" % (dut["name"], dut["base_type"]))
            lines.append("")

        if f["libraries"]:
            lines.append("#### Library References")
            lines.append("")
            lines.append("| Name | Namespace | System | Link All |")
            lines.append("|---|---|---|---|")
            for lib in f["libraries"]:
                sys_flag = "yes" if lib["system_library"] else "no"
                link_flag = "yes" if lib["link_all"] else "no"
                lines.append(
                    "| `%s` | `%s` | %s | %s |"
                    % (lib["name"], lib["namespace"], sys_flag, link_flag)
                )
            lines.append("")

        lines.append("---")
        lines.append("")

    return "\n".join(lines)


def update_manifest_with_counts(manifest_path, pou_count, dut_count):
    """Update MANIFEST.json with accurate POU/DUT counts from the XML indexer."""
    if not os.path.isfile(manifest_path):
        return

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    manifest["total_pou_count"] = pou_count
    manifest["total_dut_count"] = dut_count

    # Update notes to reflect XML-derived counts
    notes = manifest.get("notes", [])
    indexer_note = "POU/DUT counts derived from XML parsing (scripts/index_xml.py)."
    if indexer_note not in notes:
        notes.append(indexer_note)
    manifest["notes"] = notes

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)
        f.write("\n")


def update_index_with_refs(index_path, export_id):
    """Update INDEX.json to reference the Phase 2 / 2.5 artifacts."""
    if not os.path.isfile(index_path):
        return

    with open(index_path, "r", encoding="utf-8") as f:
        idx = json.load(f)

    # Add Phase 2 + 2.5 artifact references
    idx["phase2_artifacts"] = {
        "POU_INDEX.json": "Structured index of all POUs, DUTs, and library references parsed from XML files.",
        "PROJECT_MAP.md": "Human-readable markdown map of the codebase structure.",
        "generated_by": "scripts/index_xml.py",
        "phase2_5": "POU interface/variable extraction (VAR_INPUT, VAR_OUTPUT, VAR_IN_OUT, VAR, VAR_GLOBAL, return types).",
    }

    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(idx, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main():
    parser = argparse.ArgumentParser(
        description="Index CODESYS PLCopenXML export files and generate POU_INDEX.json + PROJECT_MAP.md."
    )
    parser.add_argument(
        "export_dir",
        help="Path to the export directory (e.g., exports/v1)",
    )
    parser.add_argument(
        "--no-manifest-update",
        action="store_true",
        help="Skip updating MANIFEST.json with POU/DUT counts.",
    )
    parser.add_argument(
        "--no-index-update",
        action="store_true",
        help="Skip updating INDEX.json with Phase 2 artifact references.",
    )
    args = parser.parse_args()

    export_dir = os.path.normpath(args.export_dir)
    xml_dir = os.path.join(export_dir, "xml")

    if not os.path.isdir(export_dir):
        print("ERROR: Export directory not found: %s" % export_dir, file=sys.stderr)
        sys.exit(1)

    if not os.path.isdir(xml_dir):
        print("ERROR: XML directory not found: %s" % xml_dir, file=sys.stderr)
        sys.exit(1)

    # Find and parse all XML files
    xml_files = sorted(
        f for f in os.listdir(xml_dir) if f.lower().endswith(".xml")
    )

    if not xml_files:
        print("WARNING: No .xml files found in %s" % xml_dir, file=sys.stderr)
        sys.exit(0)

    print("Indexing %d XML files from %s ..." % (len(xml_files), xml_dir))

    file_results = []
    for fname in xml_files:
        fpath = os.path.join(xml_dir, fname)
        try:
            result = parse_xml_file(fpath)
            file_results.append(result)
            print(
                "  %-50s  %3d POUs  %3d DUTs  %2d libs"
                % (fname, len(result["pous"]), len(result["duts"]), len(result["libraries"]))
            )
        except Exception as e:
            print("  ERROR parsing %s: %s" % (fname, e), file=sys.stderr)

    # Build POU index
    pou_index = build_pou_index(file_results)

    # Write POU_INDEX.json
    pou_index_path = os.path.join(export_dir, "POU_INDEX.json")
    with open(pou_index_path, "w", encoding="utf-8") as f:
        json.dump(pou_index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print("\nPOU index written to: %s" % pou_index_path)

    # Build and write PROJECT_MAP.md
    project_map = build_project_map(pou_index)
    project_map_path = os.path.join(export_dir, "PROJECT_MAP.md")
    with open(project_map_path, "w", encoding="utf-8") as f:
        f.write(project_map)
    print("Project map written to: %s" % project_map_path)

    # Update MANIFEST.json
    if not args.no_manifest_update:
        manifest_path = os.path.join(export_dir, "MANIFEST.json")
        update_manifest_with_counts(
            manifest_path,
            pou_index["summary"]["total_pous"],
            pou_index["summary"]["total_duts"],
        )
        print("MANIFEST.json updated with POU/DUT counts.")

    # Update INDEX.json
    if not args.no_index_update:
        index_path = os.path.join(export_dir, "INDEX.json")
        update_index_with_refs(index_path, os.path.basename(export_dir))
        print("INDEX.json updated with Phase 2 artifact references.")

    # Print summary
    s = pou_index["summary"]
    print("\nSummary:")
    print("  Total POUs: %d" % s["total_pous"])
    print("  Total DUTs: %d" % s["total_duts"])
    print("  Unique libraries: %d" % s["total_libraries"])
    print("  POU types: %s" % ", ".join("%s=%d" % (k, v) for k, v in sorted(s["pou_types"].items())))
    if s.get("pous_with_interface"):
        print("\nPhase 2.5 — Interface Variables:")
        print("  POUs with interface info: %d" % s["pous_with_interface"])
        print("  Total interface variables: %d" % s["total_interface_variables"])
        for cat, count in sorted(s["interface_variable_categories"].items(), key=lambda x: -x[1]):
            print("  %s: %d" % (cat, count))


if __name__ == "__main__":
    main()

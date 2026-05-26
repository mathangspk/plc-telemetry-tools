#!/usr/bin/env python3
"""Orchestration stub for processing a new measuring-profile template (MP-NN).

This script does NOT connect to the PLC. It provides:
  1. A checklist of the MP processing workflow.
  2. A skeleton verified-signals JSON generator.
  3. A packaging helper to copy artifacts into export-src/measuring-profiles/.

Usage:
  python scripts/process_mp.py MP-07              # show checklist + generate skeleton
  python scripts/process_mp.py MP-07 --skeleton    # generate skeleton JSON only
  python scripts/process_mp.py MP-07 --package     # package existing artifacts
  python scripts/process_mp.py MP-07 --all         # skeleton + package

Prerequisites:
  - Python 3.7+ (stdlib only).
  - For --package: the MP-NN.xlsx and MP-NN-verified-signals.json must exist
    in templates/ or the current directory.
"""

import argparse
import json
import os
import shutil
import sys
import time

# ---------------------------------------------------------------------------
# Paths (resolved relative to project root or script directory)
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
EXPORT_DIR = os.path.join(PROJECT_ROOT, "export-src", "measuring-profiles")

# ---------------------------------------------------------------------------
# Checklist
# ---------------------------------------------------------------------------
CHECKLIST = """
Measuring Profile Processing Checklist for {profile}
=====================================================

[ ] 1. INSPECT TEMPLATE
       - Open templates/{profile}.xlsx
       - Review existing signal rows (Signal Name, Description, Hardware Source, Note)
       - Note any placeholder or guessed signal names

[ ] 2. MAP SIGNALS TO RUNTIME CANDIDATES
       - For each signal, identify 1+ candidate PLC runtime paths
       - Use conventions:
         * CANOpen drives: CANBusDrive/c<Device>/<SignalName>
         * System signals: System/<Subsystem>/<SignalName>
         * Lift/hoist:     Lift/<SignalName> or System/iLift<Axis>Pos
         * Steering:       System/iSteer<Letter>Pos
       - Reference existing profiles (MP-01..MP-06) for patterns

[ ] 3. LIVE VALIDATE SIGNALS (conservative)
       - Run validation against PLC port 49870 (RW)
       - Use scripts/validate_mp01_signals.py as a template
       - For each candidate: send "<path> describe"
       - Record: present / no present / not validated
       - Explore parent nodes: "<parent> describe -children"
       - Save results to scripts/{profile_lower}_validation_results.json

[ ] 4. UPDATE WORKBOOK FIELDS
       - Signal Name: use live-confirmed name
       - Description: refine based on live response
       - Hardware Source: confirmed runtime path or N/A
       - Note: present | no present | manual-only | not validated
       - Use scripts/update_mp02_06.py as a pattern for batch updates

[ ] 5. CAPTURE EXACT IDENTITY
       - Run identity capture against PLC port 49880 (RO)
       - Use scripts/capture_identity.py as a template
       - For each confirmed path: extract "identity" field from describe response
       - Also capture a sample value for documentation
       - Save to scripts/identity_capture_results.json

[ ] 6. GENERATE VERIFIED SIGNALS JSON
       - Create {profile}-verified-signals.json
       - Include ONLY signals with status "present"
       - Follow the schema in export-src/measuring-profiles/README.md
       - Use --skeleton flag on this script to generate a starter file

[ ] 7. PACKAGE OUTPUTS
       - Copy {profile}.xlsx and {profile}-verified-signals.json to:
         export-src/measuring-profiles/
       - Use --package flag on this script to automate copying

[ ] 8. UPDATE DOCUMENTATION
       - Add profile to export-src/measuring-profiles/README.md summary table
       - Update HANDOFF.md if significant new signals were discovered

Key Reminders:
  - Signal names are often abbreviated on the PLC (BattVoltage, not BatteryVoltage)
  - Path separator is / (forward slash), not . (dot)
  - PrimaryPLC. namespace prefix is optional but may appear in identity fields
  - Only mark "present" if describe returns a non-error response
  - When in doubt, mark "not validated" rather than guessing
"""


# ---------------------------------------------------------------------------
# Skeleton generator
# ---------------------------------------------------------------------------
def generate_skeleton(profile):
    """Generate a skeleton verified-signals JSON file."""
    skeleton = {
        "_note": "This file is the reusable baseline for {} live-verified signals. "
        "Signals listed here do not need re-verification unless the PLC project "
        "or export changes. Any signal NOT in this file was either not present, "
        "had wrong semantics, was speculative, or was only statically inferred.".format(
            profile
        ),
        "profile": profile,
        "verified_at": time.strftime("%Y-%m-%d"),
        "source_endpoint": {"rw": "10.2.3.4:49870", "ro": "10.2.3.4:49880"},
        "verification_policy": "live-confirmed only",
        "signals": [
            {
                "template_signal": "<signal_name_from_template>",
                "signal_name": "<live_confirmed_name>",
                "runtime_path": "<confirmed_plc_path_with_slash_separators>",
                "identity": "<exact_identity_from_describe>",
                "sample_value": None,
                "status": "present",
                "evidence": "Live-read confirmed; identity resolved to <identity>",
            }
        ],
    }

    out_path = os.path.join(TEMPLATES_DIR, "{}-verified-signals.json".format(profile))
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(skeleton, f, indent=2, ensure_ascii=False)

    print("[+] Skeleton written to: {}".format(out_path))
    print('    Edit the "signals" array with live-validated data.')
    print("    Remove the example entry and add one entry per confirmed signal.")
    return out_path


# ---------------------------------------------------------------------------
# Packaging helper
# ---------------------------------------------------------------------------
def package_artifacts(profile):
    """Copy MP artifacts into export-src/measuring-profiles/."""
    xlsx_name = "{}.xlsx".format(profile)
    json_name = "{}-verified-signals.json".format(profile)

    if not os.path.isdir(EXPORT_DIR):
        os.makedirs(EXPORT_DIR)

    copied = []

    # Try templates/ first, then current directory
    for src_dir in [TEMPLATES_DIR, os.getcwd()]:
        xlsx_src = os.path.join(src_dir, xlsx_name)
        json_src = os.path.join(src_dir, json_name)

        if os.path.isfile(xlsx_src):
            dst = os.path.join(EXPORT_DIR, xlsx_name)
            shutil.copy2(xlsx_src, dst)
            copied.append(xlsx_name)
            print("[+] Copied {} -> {}".format(xlsx_src, dst))

        if os.path.isfile(json_src):
            dst = os.path.join(EXPORT_DIR, json_name)
            shutil.copy2(json_src, dst)
            copied.append(json_name)
            print("[+] Copied {} -> {}".format(json_src, dst))

    if not copied:
        print(
            "[!] No artifacts found for {} in templates/ or current directory.".format(
                profile
            )
        )
        print(
            "    Expected: {}.xlsx and/or {}-verified-signals.json".format(
                profile, profile
            )
        )
        return False

    print("[+] Packaged {} artifact(s) into {}".format(len(copied), EXPORT_DIR))
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Orchestration stub for processing a new measuring-profile template."
    )
    parser.add_argument("profile", help="Profile identifier (e.g., MP-07)")
    parser.add_argument(
        "--skeleton",
        action="store_true",
        help="Generate a skeleton verified-signals JSON file",
    )
    parser.add_argument(
        "--package",
        action="store_true",
        help="Copy artifacts into export-src/measuring-profiles/",
    )
    parser.add_argument("--all", action="store_true", help="Run skeleton + package")
    parser.add_argument(
        "--checklist", action="store_true", help="Print the processing checklist"
    )

    args = parser.parse_args()

    profile = args.profile
    profile_lower = profile.lower().replace("-", "_")

    # Default: show checklist if no action specified
    if not any([args.skeleton, args.package, args.all, args.checklist]):
        args.checklist = True

    if args.checklist or args.all:
        print(CHECKLIST.format(profile=profile, profile_lower=profile_lower))

    if args.skeleton or args.all:
        generate_skeleton(profile)

    if args.package or args.all:
        package_artifacts(profile)


if __name__ == "__main__":
    main()

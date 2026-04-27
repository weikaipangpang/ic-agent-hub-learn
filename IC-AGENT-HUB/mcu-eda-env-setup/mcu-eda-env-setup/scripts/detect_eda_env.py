#!/usr/bin/env python3
"""Detect available EDA tools, PDK, and libraries by probing the current environment.

Usage:
    python3 detect_eda_env.py [--json] [--project-dir <path>]

Probes:
  1. which <binary> for each known EDA tool
  2. module avail (if module system exists)
  3. EDA environment variables ($SYNOPSYS, $CDS_INST_DIR, $PDK_HOME, etc.)
  4. Existing project files (.synopsys_dc.setup, Makefile, *.tcl, *.sdc)

This script only reads the environment. It does not install or modify anything.
"""

import glob
import json
import os
import re
import subprocess
import sys
from datetime import datetime

# ── Tool definitions ──────────────────────────────────────────────
# Only binary names and version commands. These are tool-standard.
TOOLS = [
    {"name": "vcs",       "binary": "vcs",       "version_cmd": "vcs -ID 2>&1 | grep -i version | head -1",  "role": "simulator",    "vendor": "Synopsys"},
    {"name": "xcelium",   "binary": "xrun",      "version_cmd": "xrun -version 2>&1 | head -1",              "role": "simulator",    "vendor": "Cadence"},
    {"name": "verdi",     "binary": "verdi",      "version_cmd": "verdi -version 2>&1 | head -1",             "role": "waveform",     "vendor": "Synopsys"},
    {"name": "simvision", "binary": "simvision",  "version_cmd": "simvision -version 2>&1 | head -1",         "role": "waveform",     "vendor": "Cadence"},
    {"name": "dve",       "binary": "dve",        "version_cmd": "dve -version 2>&1 | head -1",               "role": "waveform",     "vendor": "Synopsys"},
    {"name": "spyglass",  "binary": "spyglass",   "version_cmd": "spyglass -version 2>&1 | head -1",          "role": "lint",         "vendor": "Synopsys"},
    {"name": "ascent",    "binary": "hal",        "version_cmd": "hal -version 2>&1 | head -1",               "role": "lint",         "vendor": "Cadence"},
    {"name": "dc_shell",  "binary": "dc_shell",   "version_cmd": "dc_shell -version 2>&1 | head -1",          "role": "synthesizer",  "vendor": "Synopsys"},
    {"name": "genus",     "binary": "genus",      "version_cmd": "genus -version 2>&1 | head -1",             "role": "synthesizer",  "vendor": "Cadence"},
    {"name": "innovus",   "binary": "innovus",    "version_cmd": "innovus -version 2>&1 | head -1",           "role": "pnr",          "vendor": "Cadence"},
    {"name": "icc2",      "binary": "icc2_shell", "version_cmd": "icc2_shell -version 2>&1 | head -1",        "role": "pnr",          "vendor": "Synopsys"},
    {"name": "formality", "binary": "fm_shell",   "version_cmd": "fm_shell -version 2>&1 | head -1",          "role": "equivalence",  "vendor": "Synopsys"},
    {"name": "conformal", "binary": "lec",        "version_cmd": "lec -version 2>&1 | head -1",               "role": "equivalence",  "vendor": "Cadence"},
    {"name": "primetime", "binary": "pt_shell",   "version_cmd": "pt_shell -version 2>&1 | head -1",          "role": "sta",          "vendor": "Synopsys"},
    {"name": "tempus",    "binary": "tempus",     "version_cmd": "tempus -version 2>&1 | head -1",            "role": "sta",          "vendor": "Cadence"},
    {"name": "starrc",    "binary": "StarXtract", "version_cmd": "StarXtract -version 2>&1 | head -1",        "role": "extraction",   "vendor": "Synopsys"},
    {"name": "qrc",       "binary": "qrc",        "version_cmd": "qrc -version 2>&1 | head -1",               "role": "extraction",   "vendor": "Cadence"},
    {"name": "calibre",   "binary": "calibre",    "version_cmd": "calibre -version 2>&1 | head -1",           "role": "physical_ver", "vendor": "Siemens"},
    {"name": "icv",       "binary": "icv_comp",   "version_cmd": "icv_comp -version 2>&1 | head -1",          "role": "physical_ver", "vendor": "Synopsys"},
    {"name": "pegasus",   "binary": "pegasus",    "version_cmd": "pegasus -version 2>&1 | head -1",           "role": "physical_ver", "vendor": "Cadence"},
]

ROLES = ["simulator", "lint", "synthesizer", "pnr", "equivalence", "sta", "extraction", "physical_ver", "waveform"]

# Known EDA environment variables
EDA_ENV_VARS = [
    ("SYNOPSYS",       "Synopsys tool root"),
    ("CDS_INST_DIR",   "Cadence tool root"),
    ("MGC_HOME",       "Siemens/Mentor tool root"),
    ("VCS_HOME",       "VCS install path"),
    ("VERDI_HOME",     "Verdi install path"),
    ("DC_HOME",        "Design Compiler install path"),
    ("INNOVUS_HOME",   "Innovus install path"),
    ("PT_HOME",        "PrimeTime install path"),
    ("PDK_HOME",       "PDK root"),
    ("PDK_DIR",        "PDK directory"),
    ("TECH_DIR",       "Technology directory"),
    ("STD_CELL_DIR",   "Standard cell library root"),
    ("STDLIB",         "Standard cell library root"),
    ("MEM_IP_DIR",     "Memory macro root"),
    ("SRAM_DIR",       "SRAM macro root"),
]

# Module name patterns to match in module avail output
MODULE_PATTERNS = {
    "vcs":       r"vcs/",
    "xcelium":   r"xcelium/|xrun/",
    "verdi":     r"verdi/",
    "spyglass":  r"spyglass/",
    "dc_shell":  r"syn/|dc_shell/|dc/",
    "genus":     r"genus/",
    "innovus":   r"innovus/",
    "icc2":      r"icc2/",
    "formality": r"syn/|fm/|formality/",
    "conformal": r"conformal/|lec/",
    "primetime": r"pts/|pt/|primetime/",
    "tempus":    r"tempus/",
    "starrc":    r"starrc/",
    "qrc":       r"qrc/",
    "calibre":   r"calibre/",
    "icv":       r"icv/",
    "pegasus":   r"pegasus/",
}


def run_cmd(cmd):
    """Run a command safely (shell=False). If cmd is a string, split it.
    Pipe operations (2>&1, | head) are handled in Python, not via shell."""
    try:
        if isinstance(cmd, str):
            # Strip shell pipe/redirect suffixes — handle in Python
            clean = re.sub(r"\s*2>&1.*", "", cmd).strip()
            args = clean.split()
        else:
            args = list(cmd)
        r = subprocess.run(args, shell=False, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, timeout=15)
        out = (r.stdout.decode(errors="replace") + "\n" + r.stderr.decode(errors="replace")).strip()
        # Equivalent of "| head -1": take first non-empty line
        first_line = ""
        for line in out.split("\n"):
            line = line.strip()
            if line:
                first_line = line
                break
        return r.returncode == 0, first_line if first_line else out[:200]
    except (subprocess.TimeoutExpired, OSError):
        return False, ""


# ── 1. Tool detection ─────────────────────────────────────────────

def detect_tools():
    inventory = []
    for t in TOOLS:
        found, path = run_cmd(f"which {t['binary']}")
        entry = {
            "name": t["name"], "binary": t["binary"], "role": t["role"],
            "vendor": t["vendor"], "available": found,
            "path": path.split("\n")[0] if found else None,
            "version": None, "module": None, "source": "PATH" if found else None,
        }
        if found:
            _, ver = run_cmd(t["version_cmd"])
            entry["version"] = ver or "detected"
        inventory.append(entry)
    return inventory


# ── 2. Module system scan ─────────────────────────────────────────

def scan_modules():
    ok, out = run_cmd("module avail 2>&1")
    if not out:
        return {"available": False, "modules": {}}

    discovered = {}
    for tool_name, pattern in MODULE_PATTERNS.items():
        matches = re.findall(rf"({pattern}\S+)", out)
        if matches:
            # Keep all versions found
            discovered[tool_name] = sorted(set(matches))

    return {"available": True, "modules": discovered}


# ── 3. Environment variables ──────────────────────────────────────

def scan_env_vars():
    found = {}
    for var, desc in EDA_ENV_VARS:
        val = os.environ.get(var)
        if val and os.path.exists(val):
            found[var] = {"value": val, "description": desc, "exists": True}
        elif val:
            found[var] = {"value": val, "description": desc, "exists": False}
    return found


# ── 4. Project file scan ──────────────────────────────────────────

def scan_project_files(project_dir):
    """Scan existing project files to discover tool preferences and library paths."""
    findings = {
        "setup_files": [],
        "library_paths": [],
        "design_info": {},
    }
    if not project_dir or not os.path.isdir(project_dir):
        return findings

    # .synopsys_dc.setup
    for dc_setup in glob.glob(os.path.join(project_dir, "**/.synopsys_dc.setup"), recursive=True):
        findings["setup_files"].append(dc_setup)
        try:
            content = open(dc_setup).read()
            # Extract search_path
            sp = re.findall(r"set\s+search_path\s+.*?{(.*?)}", content, re.DOTALL)
            for paths_str in sp:
                for p in paths_str.split():
                    p = p.strip().strip('"').strip("'")
                    if p and p != ".":
                        findings["library_paths"].append({"source": dc_setup, "path": p, "type": "search_path"})
            # Extract target_library
            tl = re.findall(r"set\s+target_library\s+.*?{?(.*?)}?\s*$", content, re.MULTILINE)
            for libs_str in tl:
                for lib in libs_str.split():
                    lib = lib.strip().strip('"')
                    if lib and lib != "*":
                        findings["library_paths"].append({"source": dc_setup, "path": lib, "type": "target_library"})
        except OSError:
            pass

    # Makefile — detect simulator choice
    for mk in glob.glob(os.path.join(project_dir, "**/Makefile"), recursive=True):
        try:
            content = open(mk).read(4096)
            if "vcs" in content.lower():
                findings["design_info"]["makefile_simulator"] = "vcs"
            elif "xrun" in content.lower() or "xcelium" in content.lower():
                findings["design_info"]["makefile_simulator"] = "xcelium"
            findings["setup_files"].append(mk)
        except OSError:
            pass

    # SDC — extract clock definitions
    for sdc in glob.glob(os.path.join(project_dir, "**/*.sdc"), recursive=True):
        try:
            content = open(sdc).read(4096)
            clocks = re.findall(r"create_clock.*?-name\s+(\S+).*?-period\s+([\d.]+)", content)
            if clocks:
                findings["design_info"]["clocks"] = [{"name": c[0], "period_ns": float(c[1])} for c in clocks]
            findings["setup_files"].append(sdc)
        except OSError:
            pass

    # filelist
    for flist in glob.glob(os.path.join(project_dir, "**/*.f"), recursive=True):
        findings["setup_files"].append(flist)

    # TCL scripts — look for library paths
    for tcl in glob.glob(os.path.join(project_dir, "scripts/*.tcl"), recursive=False):
        try:
            content = open(tcl).read(8192)
            # Look for set_db / read_libs / read_lib patterns
            lib_refs = re.findall(r"(?:read_lib|read_db|set\s+target_library)\s+.*?(\S+\.(?:db|lib))", content)
            for lib in lib_refs:
                findings["library_paths"].append({"source": tcl, "path": lib, "type": "tcl_reference"})
            findings["setup_files"].append(tcl)
        except OSError:
            pass

    return findings


# ── 5. PDK/Library path discovery ─────────────────────────────────

def discover_pdk_libs(env_vars, project_findings):
    """Try to find PDK and library files from discovered paths."""
    pdk = {}
    libraries = {"std_cell": {}, "sram": []}

    # Collect candidate root paths
    roots = []
    for var in ("PDK_HOME", "PDK_DIR", "TECH_DIR"):
        if var in env_vars and env_vars[var]["exists"]:
            roots.append(env_vars[var]["value"])
    for var in ("STD_CELL_DIR", "STDLIB"):
        if var in env_vars and env_vars[var]["exists"]:
            roots.append(env_vars[var]["value"])

    # Also use library paths found in project files
    for lp in project_findings.get("library_paths", []):
        p = lp["path"]
        if os.path.isabs(p):
            # Go up a few dirs to find library root
            for _ in range(3):
                p = os.path.dirname(p)
                if p and os.path.isdir(p):
                    roots.append(p)

    roots = list(set(roots))

    # Scan for common PDK file patterns
    for root in roots:
        if not os.path.isdir(root):
            continue

        # Tech file
        for tf in glob.glob(os.path.join(root, "**/*.tf"), recursive=True):
            pdk.setdefault("tech_file", tf)
        # TLU+
        for tlu in glob.glob(os.path.join(root, "**/*max*.tluplus"), recursive=True):
            pdk.setdefault("tlu_plus_max", tlu)
        for tlu in glob.glob(os.path.join(root, "**/*min*.tluplus"), recursive=True):
            pdk.setdefault("tlu_plus_min", tlu)
        for tlu in glob.glob(os.path.join(root, "**/*.tluplus"), recursive=True):
            if "max" not in tlu and "min" not in tlu:
                pdk.setdefault("tlu_plus_nom", tlu)
        # Tech LEF
        for lef in glob.glob(os.path.join(root, "**/*tech*.lef"), recursive=True):
            pdk.setdefault("tech_lef", lef)
        # DRC/LVS rules
        for rul in glob.glob(os.path.join(root, "**/*drc*.rul"), recursive=True):
            pdk.setdefault("drc_rules", rul)
        for rul in glob.glob(os.path.join(root, "**/*lvs*.rul"), recursive=True):
            pdk.setdefault("lvs_rules", rul)
        # Calibre rules alternative patterns
        for rul in glob.glob(os.path.join(root, "**/calibre/drc/**/*.rul"), recursive=True):
            pdk.setdefault("drc_rules", rul)
        for rul in glob.glob(os.path.join(root, "**/calibre/lvs/**/*.rul"), recursive=True):
            pdk.setdefault("lvs_rules", rul)

        # Standard cell .db / .lib discovery — infer corners
        for db in glob.glob(os.path.join(root, "**/*.db"), recursive=True):
            path_lower = db.lower()
            corner = None
            if "ss" in path_lower or "slow" in path_lower:
                corner = "ss"
            elif "ff" in path_lower or "fast" in path_lower:
                corner = "ff"
            elif "tt" in path_lower or "typ" in path_lower:
                corner = "tt"
            if corner:
                libraries["std_cell"].setdefault(corner, {"db": [], "lib": [], "lef": ""})
                if db not in libraries["std_cell"][corner]["db"]:
                    libraries["std_cell"][corner]["db"].append(db)

        # LEF for std cells
        for lef in glob.glob(os.path.join(root, "**/*.lef"), recursive=True):
            if "tech" not in lef.lower():
                for corner_data in libraries["std_cell"].values():
                    if not corner_data["lef"]:
                        corner_data["lef"] = lef

    return pdk, libraries


# ── 6. LSF check ──────────────────────────────────────────────────

def check_lsf():
    found, path = run_cmd("which bsub")
    if found:
        return {"available": True, "mode": "local", "path": path.split("\n")[0]}
    return {"available": False, "mode": "none", "path": None}


# ── 7. Tool selection ─────────────────────────────────────────────

def select_tools(inventory, project_findings=None):
    priority = {
        "simulator":    ["vcs", "xcelium"],
        "lint":         ["spyglass", "ascent"],
        "synthesizer":  ["dc_shell", "genus"],
        "pnr":          ["innovus", "icc2"],
        "equivalence":  ["formality", "conformal"],
        "sta":          ["primetime", "tempus"],
        "extraction":   ["starrc", "qrc"],
        "physical_ver": ["calibre", "icv", "pegasus"],
        "waveform":     ["verdi", "simvision", "dve"],
    }

    available_by_role = {}
    for t in inventory:
        if t["available"]:
            available_by_role.setdefault(t["role"], []).append(t["name"])

    # Check if project files hint at a preference
    hints = {}
    if project_findings:
        mk_sim = project_findings.get("design_info", {}).get("makefile_simulator")
        if mk_sim:
            hints["simulator"] = mk_sim

    selected = {}
    for role in ROLES:
        candidates = available_by_role.get(role, [])
        if not candidates:
            selected[role] = None
            continue

        # Hint from project files
        if role in hints and hints[role] in candidates:
            selected[role] = hints[role]
            continue

        # Priority order
        for p in priority.get(role, []):
            if p in candidates:
                selected[role] = p
                break
        if role not in selected:
            selected[role] = candidates[0]

    return selected


# ── Main ──────────────────────────────────────────────────────────

def main():
    args = sys.argv[1:]
    json_mode = "--json" in args
    project_dir = None
    for i, a in enumerate(args):
        if a == "--project-dir" and i + 1 < len(args):
            project_dir = args[i + 1]
    if not project_dir:
        project_dir = os.getcwd()

    # Probe
    inventory = detect_tools()
    modules = scan_modules()
    env_vars = scan_env_vars()
    project_findings = scan_project_files(project_dir)
    pdk, libraries = discover_pdk_libs(env_vars, project_findings)
    lsf = check_lsf()

    # Enrich inventory with module info
    for t in inventory:
        if not t["available"] and t["name"] in modules.get("modules", {}):
            t["module"] = modules["modules"][t["name"]]
            t["source"] = "module_avail (not loaded)"

    selected = select_tools(inventory, project_findings)

    available = [t for t in inventory if t["available"]]
    unavailable = [t for t in inventory if not t["available"]]
    module_only = [t for t in unavailable if t.get("module")]

    result = {
        "timestamp": datetime.now().isoformat(),
        "project_dir": project_dir,
        "available_tools": available,
        "module_available_tools": module_only,
        "unavailable_tools": [t["name"] for t in unavailable if not t.get("module")],
        "selected_tools": selected,
        "env_vars": env_vars,
        "pdk": pdk,
        "libraries": libraries,
        "lsf": lsf,
        "project_files": project_findings.get("setup_files", []),
        "design_info": project_findings.get("design_info", {}),
        "summary": {role: [t["name"] for t in available if t["role"] == role] for role in ROLES},
    }

    if json_mode:
        print(json.dumps(result, indent=2, default=str))
    else:
        print(f"EDA Environment Detection — {result['timestamp']}")
        print(f"Project: {project_dir}")
        print("=" * 60)

        print("\nTools in PATH:")
        for role in ROLES:
            tools_for_role = [t for t in available if t["role"] == role]
            sel = selected.get(role)
            if tools_for_role:
                parts = []
                for t in tools_for_role:
                    mark = " *" if t["name"] == sel else ""
                    parts.append(f"{t['name']}{mark} ({t.get('version', '?')})")
                print(f"  {role:14s}: {', '.join(parts)}")
            else:
                print(f"  {role:14s}: (none)")

        if module_only:
            print("\nAvailable via module load (not currently loaded):")
            for t in module_only:
                mods = t["module"] if isinstance(t["module"], list) else [t["module"]]
                print(f"  {t['name']:14s}: {', '.join(mods)}")

        if env_vars:
            print("\nEDA environment variables:")
            for var, info in env_vars.items():
                status = "OK" if info["exists"] else "path missing"
                print(f"  ${var}: {info['value']} [{status}]")

        if pdk:
            print("\nPDK files discovered:")
            for key, val in pdk.items():
                print(f"  {key}: {val}")

        if any(libraries["std_cell"].values()):
            print("\nStandard cell corners discovered:")
            for corner, data in libraries["std_cell"].items():
                n_db = len(data.get("db", []))
                print(f"  {corner}: {n_db} .db files, lef: {'yes' if data.get('lef') else 'no'}")

        print(f"\nLSF: {'available (' + lsf['mode'] + ')' if lsf['available'] else 'not available'}")

        if project_findings.get("setup_files"):
            print(f"\nProject files found: {len(project_findings['setup_files'])}")
            for f in project_findings["setup_files"][:10]:
                print(f"  {f}")

        print(f"\n  (* = selected tool)")


if __name__ == "__main__":
    main()

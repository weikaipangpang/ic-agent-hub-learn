#!/usr/bin/env python3
"""Detect available EDA tools dynamically and verify they can execute.

Usage:
    python3 detect_eda_env.py                          # human-readable report
    python3 detect_eda_env.py --json                    # JSON to stdout
    python3 detect_eda_env.py --output <file.json>      # JSON to file + exec log
    python3 detect_eda_env.py --registry <tools.json>   # custom tool registry
    python3 detect_eda_env.py --smoke                   # also run smoke tests (optional)

Detection:
  1. Load tool registry (default: references/simulators/tools_registry.json)
  2. Scan 'module avail' for additional EDA modules not in registry
  3. For each tool: PATH check + version query (default), + smoke test (if --smoke)
  4. Output structured JSON with execution log

Security: all subprocess calls use shell=False with explicit argument lists.
This script only reads the environment. It does not install or modify anything.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
from datetime import datetime


EXEC_LOG = []
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DEFAULT_REGISTRY = os.path.join(SCRIPT_DIR, "..", "references", "simulators", "tools_registry.json")


def run_cmd(args, timeout=30):
    """Run a command with explicit argument list (no shell). Logs every invocation."""
    entry = {
        "cmd": " ".join(args) if isinstance(args, list) else str(args),
        "timestamp": datetime.now().isoformat(),
    }
    try:
        result = subprocess.run(
            args,
            shell=False,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
        )
        stdout = result.stdout.decode(errors="replace").strip()
        stderr = result.stderr.decode(errors="replace").strip()
        entry["returncode"] = result.returncode
        entry["stdout"] = stdout[:500]
        entry["stderr"] = stderr[:500]
        entry["success"] = True
        EXEC_LOG.append(entry)
        return True, stdout, stderr
    except subprocess.TimeoutExpired:
        entry["returncode"] = -1
        entry["stdout"] = ""
        entry["stderr"] = "timeout after %ds" % timeout
        entry["success"] = False
        EXEC_LOG.append(entry)
        return False, "", "timeout"
    except OSError as e:
        entry["returncode"] = -1
        entry["stdout"] = ""
        entry["stderr"] = str(e)
        entry["success"] = False
        EXEC_LOG.append(entry)
        return False, "", str(e)


def load_registry(registry_path):
    """Load tool definitions from JSON registry file."""
    path = os.path.normpath(registry_path)
    if not os.path.exists(path):
        print("Warning: registry file not found: %s" % path, file=sys.stderr)
        return []
    with open(path) as f:
        return json.load(f)


def scan_module_avail():
    """Scan 'module avail' for EDA-related modules not in registry.
    Returns list of discovered module names grouped by vendor directory."""
    ok, stdout, stderr = run_cmd(["modulecmd", "python", "avail"], timeout=10)
    # module avail often outputs to stderr
    combined = stdout + "\n" + stderr
    if not combined.strip():
        # Try alternative
        ok, stdout, stderr = run_cmd(["bash", "-c", "module avail 2>&1"], timeout=10)
        combined = stdout + "\n" + stderr

    modules = []
    for line in combined.split("\n"):
        line = line.strip()
        # Skip header lines
        if line.startswith("---") or not line:
            continue
        # Extract module names (e.g., "vcs/V-2023.12-SP1")
        for token in line.split():
            token = token.strip()
            if "/" in token and not token.startswith("-"):
                modules.append(token)
    return modules


def which(binary):
    """Find binary in PATH without shell."""
    ok, stdout, _ = run_cmd(["which", binary])
    return ok, stdout


def get_version(tool):
    """Get tool version using explicit command + regex extraction."""
    ok, stdout, stderr = run_cmd(tool["version_cmd"])
    combined = stdout + "\n" + stderr
    match = re.search(tool["version_regex"], combined, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    for line in combined.split("\n"):
        line = line.strip()
        if line and "error" not in line.lower() and "warning" not in line.lower():
            return line[:80]
    return "unknown"


def smoke_test(tool, tmpdir):
    """Run a smoke test to verify the tool actually works."""
    smoke_type = tool.get("smoke_type", "version_only")

    if smoke_type == "compile_sv":
        sv_file = os.path.join(tmpdir, "smoke_%s.sv" % tool["name"])
        log_file = os.path.join(tmpdir, "smoke_%s.log" % tool["name"])
        with open(sv_file, "w") as f:
            f.write("module smoke_test_%s; endmodule\n" % tool["name"])
        cmd = list(tool["smoke_cmd"]) + [sv_file, "-l", log_file]
        if tool["name"] == "vcs":
            out_file = os.path.join(tmpdir, "smoke_%s_simv" % tool["name"])
            cmd += ["-o", out_file]
        ok, stdout, stderr = run_cmd(cmd, timeout=60)
        if os.path.exists(log_file):
            with open(log_file) as f:
                log_content = f.read()
            has_error = bool(re.search(r"\bError\b", log_content)) and "0 errors" not in log_content.lower()
            return not has_error, "log: %d bytes, errors: %s" % (len(log_content), "yes" if has_error else "no")
        return ok, (stdout or stderr)[:200]

    elif smoke_type == "stdin_quit":
        ok, stdout, stderr = run_cmd(tool["smoke_cmd"], timeout=30)
        return ok or bool(stdout), (stdout or stderr)[:200]

    elif smoke_type == "version_only":
        ok, stdout, stderr = run_cmd(tool["smoke_cmd"])
        return ok or bool(stdout) or bool(stderr), (stdout or stderr)[:200]

    return False, "unknown smoke_type: %s" % smoke_type


def detect_tools(registry, run_smoke=False):
    """Detect tools from registry. PATH + version by default, + smoke test if requested."""
    inventory = []
    tmpdir = tempfile.mkdtemp(prefix="eda_detect_") if run_smoke else None

    for tool in registry:
        entry = {
            "name": tool["name"],
            "role": tool.get("role", "unknown"),
            "vendor": tool.get("vendor", "unknown"),
            "path_check": {"found": False, "path": ""},
            "version_check": {"found": False, "version": ""},
            "smoke_test": {"passed": "skipped", "output": "not requested"},
            "available": False,
        }

        found, path = which(tool["binary"])
        entry["path_check"]["found"] = found
        entry["path_check"]["path"] = path

        if not found:
            inventory.append(entry)
            continue

        version = get_version(tool)
        entry["version_check"]["found"] = version != "unknown"
        entry["version_check"]["version"] = version

        if run_smoke and tmpdir:
            passed, output = smoke_test(tool, tmpdir)
            entry["smoke_test"]["passed"] = passed
            entry["smoke_test"]["output"] = output
            entry["available"] = entry["path_check"]["found"] and passed
        else:
            entry["smoke_test"]["passed"] = "skipped"
            entry["available"] = entry["path_check"]["found"]

        inventory.append(entry)

    # Cleanup
    if tmpdir and os.path.exists(tmpdir):
        for f in os.listdir(tmpdir):
            fpath = os.path.join(tmpdir, f)
            if os.path.isfile(fpath):
                try:
                    os.remove(fpath)
                except OSError:
                    pass
        try:
            os.rmdir(tmpdir)
        except OSError:
            pass

    return inventory


def build_result(inventory, registry_path, module_scan, run_smoke=False):
    """Build structured result dict."""
    available = [t for t in inventory if t["available"]]
    unavailable = [t for t in inventory if not t["available"]]
    method = "PATH check + version query (shell=False)"
    if run_smoke:
        method += " + smoke test"
    return {
        "timestamp": datetime.now().isoformat(),
        "detection_method": method,
        "registry_file": registry_path,
        "module_scan": module_scan,
        "available_tools": available,
        "unavailable_tools": [
            {"name": t["name"], "reason": get_failure_reason(t)}
            for t in unavailable
        ],
        "summary": {
            "simulators": [t["name"] for t in available if t["role"] == "simulator"],
            "lint": [t["name"] for t in available if t["role"] == "lint"],
            "synthesis": [t["name"] for t in available if t["role"] == "synthesis"],
            "waveform": [t["name"] for t in available if t["role"] == "waveform"],
        },
        "execution_log": EXEC_LOG,
        "total_commands_executed": len(EXEC_LOG),
    }


def get_failure_reason(tool_entry):
    if not tool_entry["path_check"]["found"]:
        return "not in PATH"
    if not tool_entry["smoke_test"]["passed"]:
        return "smoke test failed: %s" % tool_entry["smoke_test"]["output"][:100]
    return "unknown"


def print_human(result):
    print("EDA Environment Detection - %s" % result["timestamp"])
    print("Method: %s" % result["detection_method"])
    print("Registry: %s" % result["registry_file"])
    print("Commands executed: %d" % result["total_commands_executed"])
    print("=" * 70)
    for tool in result["available_tools"]:
        print("  [OK] %-12s %-12s ver=%-30s smoke=%s" % (
            tool["name"], tool["role"],
            tool["version_check"]["version"][:30],
            "PASS" if tool["smoke_test"]["passed"] else "FAIL",
        ))
    if result["unavailable_tools"]:
        print("\nUnavailable:")
        for t in result["unavailable_tools"]:
            print("  [--] %-12s reason: %s" % (t["name"], t["reason"]))
    if result["module_scan"]:
        print("\nModule avail scan: %d modules found" % len(result["module_scan"]))
    s = result["summary"]
    print("\nSimulators: %s" % (", ".join(s["simulators"]) or "none"))
    print("Lint:       %s" % (", ".join(s["lint"]) or "none"))
    print("Synthesis:  %s" % (", ".join(s["synthesis"]) or "none"))
    print("Waveform:   %s" % (", ".join(s["waveform"]) or "none"))


def main():
    registry_path = DEFAULT_REGISTRY
    output_file = None
    json_mode = False
    run_smoke = False

    args = sys.argv[1:]
    i = 0
    while i < len(args):
        if args[i] == "--output" and i + 1 < len(args):
            output_file = args[i + 1]
            i += 2
        elif args[i] == "--json":
            json_mode = True
            i += 1
        elif args[i] == "--registry" and i + 1 < len(args):
            registry_path = args[i + 1]
            i += 2
        elif args[i] == "--smoke":
            run_smoke = True
            i += 1
        else:
            i += 1

    # Load registry
    registry = load_registry(registry_path)
    if not registry:
        print("Error: empty or missing tool registry", file=sys.stderr)
        sys.exit(1)

    # Scan module avail
    module_scan = scan_module_avail()

    # Detect tools
    inventory = detect_tools(registry, run_smoke=run_smoke)
    result = build_result(inventory, registry_path, module_scan, run_smoke)

    if output_file:
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)
        log_file = output_file.replace(".json", "_exec_log.txt")
        with open(log_file, "w") as f:
            f.write("EDA Tool Detection Execution Log\n")
            f.write("Generated: %s\n" % result["timestamp"])
            f.write("Registry: %s\n" % registry_path)
            f.write("Total commands: %d (all shell=False)\n" % len(EXEC_LOG))
            f.write("=" * 70 + "\n\n")
            for idx, entry in enumerate(EXEC_LOG, 1):
                f.write("[%d] %s\n" % (idx, entry["timestamp"]))
                f.write("    CMD: %s\n" % entry["cmd"])
                f.write("    RC:  %s\n" % entry["returncode"])
                f.write("    OK:  %s\n" % entry["success"])
                if entry.get("stdout"):
                    f.write("    OUT: %s\n" % entry["stdout"][:200])
                if entry.get("stderr"):
                    f.write("    ERR: %s\n" % entry["stderr"][:200])
                f.write("\n")
        print("EDA detection result written to: %s" % output_file)
        print("Execution log written to: %s" % log_file)
        print_human(result)
    elif json_mode:
        print(json.dumps(result, indent=2))
    else:
        print_human(result)


if __name__ == "__main__":
    main()

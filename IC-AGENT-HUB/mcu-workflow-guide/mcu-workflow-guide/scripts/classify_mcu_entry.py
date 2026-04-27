import json
import sys


KEYWORDS = {
    "mcu-eda-env-setup": ["environment", "eda", "tool setup", "pdk", "library path", "module load", "eda_env"],
    "mcu-spec-architecture-planning": ["spec", "architecture", "memory map", "interrupt", "clock", "reset", "peripheral list"],
    "mcu-rtl-development": ["rtl", "wrapper", "top module", "filelist", "interconnect", "integration", "verilog"],
    "mcu-tb-development": ["testbench", "testcase", "checker", "uvm", "stimulus", "test plan", "directed test", "sequence"],
    "mcu-compile-sim-run": ["compile", "simulate", "simulation", "vcs", "xcelium", "sim log", "compile log"],
    "mcu-verification-triage": ["triage", "debug", "failing", "error", "lint", "cdc", "waveform", "diagnose"],
    "mcu-regression-and-coverage": ["regression", "coverage", "gap", "exclusion", "rerun", "cluster", "failure rate"],
    "mcu-formal-and-assertion": ["assertion", "property", "formal", "fsm", "assumption", "sva", "prove"],
    "mcu-synthesis-planning": ["synthesis", "qor", "area", "timing", "constraint", "sdc", "netlist", "dc_shell", "genus"],
    "mcu-equivalence-review": ["equivalence", "formality", "conformal", "compare point", "svf", "lec", "match"],
    "mcu-pnr-implementation": ["pnr", "floorplan", "cts", "route", "congestion", "placement", "innovus", "icc2"],
    "mcu-signoff-review": ["starrc", "primetime", "drc", "lvs", "signoff", "gds", "spef", "extraction", "calibre"],
    "mcu-report-and-handoff": ["handoff", "report", "summary", "milestone", "deliverable", "inventory"],
}


def classify(text: str) -> str:
    lowered = text.lower()
    scores = {
        stage: sum(1 for keyword in keywords if keyword in lowered)
        for stage, keywords in KEYWORDS.items()
    }
    stage, score = max(scores.items(), key=lambda item: item[1])
    return stage if score > 0 else "cortex-m3-mcu-workflow-guide"


def main() -> int:
    text = sys.stdin.read()
    result = {"recommended_skill": classify(text)}
    json.dump(result, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

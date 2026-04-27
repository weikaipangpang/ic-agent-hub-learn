import json
import sys
from pathlib import Path
from typing import Any


# Stage priority: higher number = later in flow = takes routing precedence
# When multiple artifacts match, route to the latest-stage skill.
ROUTES = {
    "spec":                       ("frontend-spec-extraction",             1),
    "interface_view":             ("frontend-spec-review",                 2),
    "register_view":              ("frontend-spec-review",                 2),
    "clock_reset_view":           ("frontend-spec-review",                 2),
    "review_summary":             ("frontend-spec-review",                 2),
    "microarchitecture_question": ("frontend-microarchitecture-analysis",  3),
    "rtl_plan":                   ("frontend-rtl-architecture",            4),
    "rtl_code":                   ("frontend-rtl-gen",                     5),
    "tb_code":                    ("frontend-tb-gen",                      6),
    "filelist":                   ("frontend-integration-and-bringup",     7),
    "eda_env":                    ("frontend-eda-env-setup",               8),
    "makefile":                   ("frontend-eda-env-setup",               8),
    "compile_ready":              ("frontend-compile-sim-run",             9),
    "compile_log":                ("frontend-debug-triage",               10),
    "sim_log":                    ("frontend-debug-triage",               10),
    "waveform":                   ("frontend-wave-debug",                 11),
}


def ensure_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    return [value]


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: classify_frontend_entry.py <artifact_inventory.json>", file=sys.stderr)
        return 1

    payload = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    artifacts = [str(x).lower() for x in ensure_list(payload.get("artifacts"))]
    problem_focus = str(payload.get("problem_focus", "")).lower()

    matched = []
    for artifact in artifacts:
        if artifact in ROUTES:
            skill, priority = ROUTES[artifact]
            matched.append((artifact, skill, priority))

    if not matched:
        if "rtl" in problem_focus or "architecture" in problem_focus:
            matched.append(("problem_focus", "frontend-rtl-architecture", 4))
        elif "bringup" in problem_focus or "integration" in problem_focus:
            matched.append(("problem_focus", "frontend-integration-and-bringup", 7))
        elif "debug" in problem_focus or "compile" in problem_focus or "sim" in problem_focus:
            matched.append(("problem_focus", "frontend-debug-triage", 10))
        else:
            matched.append(("default", "frontend-workflow-guide", 0))

    # Route to the highest-stage skill (latest in pipeline takes precedence)
    matched.sort(key=lambda x: x[2])
    primary = matched[-1][1]
    fallback = ""
    if primary == "frontend-rtl-architecture" and not any(
        a in {"review_summary", "interface_view", "register_view", "clock_reset_view"} for a in artifacts
    ):
        fallback = "frontend-spec-review"
    elif primary == "frontend-integration-and-bringup" and "rtl_plan" not in artifacts:
        fallback = "frontend-rtl-architecture"
    elif primary == "frontend-debug-triage" and not any(a in {"compile_log", "sim_log"} for a in artifacts):
        fallback = "frontend-integration-and-bringup"

    result = {
        "artifacts": artifacts,
        "problem_focus": problem_focus,
        "primary_recommended_skill": primary,
        "fallback_skill": fallback,
        "matched_signals": [{"signal": signal, "skill": skill, "stage": stage} for signal, skill, stage in matched],
    }
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

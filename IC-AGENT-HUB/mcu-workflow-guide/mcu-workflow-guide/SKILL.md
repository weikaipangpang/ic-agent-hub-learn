---
name: mcu-workflow-guide
description: Orchestrate the complete Cortex-M3 MCU design flow from specification to GDS handoff. Defines stage order, dependencies, entry and completion criteria for each stage, and guides the user through the full engineering pipeline. Use as the entry point for any MCU project — whether starting fresh, resuming mid-flow, or diagnosing where to pick up after a break.
license: PolyForm-Noncommercial-1.0.0
metadata:
  author: 中科麒芯
  organization: 中科麒芯智能技术（南京）有限公司
  homepage: https://www.ickylin.com/
  contact: info@ickylin.com
---

# MCU Workflow Guide

This skill defines the complete engineering pipeline for a Cortex-M3 MCU SoC project. It serves as the master reference for stage ordering, dependencies, and progression rules.

## Boundaries

- This skill defines flow structure and routing. It does **not** execute EDA tools directly.
- Each stage skill owns its own execution logic, tool templates, and result parsing.
- This skill does **not** generate RTL, scripts, or reports — it tells the user which skill does.

## Use this skill to:

- understand the full Spec-to-GDS flow and what each stage produces
- determine the current project state and which stage to run next
- resume a project after a break by scanning existing artifacts
- understand what must be re-run when upstream changes occur

## Full Flow Overview

```
Stage 0:  mcu-eda-env-setup              Detect tools, validate PDK/libs
    |
Stage 1:  mcu-spec-architecture-planning  Generate spec.md + architecture.md
    |
Stage 2:  mcu-rtl-development             Generate RTL + integration review
    |
Stage 3:  mcu-tb-development              Plan tests + generate TB/UVM code
    |
Stage 4:  mcu-compile-sim-run             Compile + sim + lint + CDC
    |         |
    |         ↓ fail
    |     mcu-verification-triage          Diagnose (log + waveform)
    |         |
    |         ↓ fix
    |     mcu-rtl-development              Incremental RTL fix
    |     or mcu-tb-development            Incremental TB fix
    |         |
    |         ↓ back to Stage 4 recompile
    |
Stage 5:  mcu-compile-sim-run (regression) + mcu-regression-and-coverage
    |         Regression run → failure clustering → coverage closure
    |         |
    |         ↓ gaps found
    |     mcu-tb-development               Add tests → back to Stage 5
    |
Stage 6:  mcu-formal-and-assertion         SVA generation + formal review
    |     (can run in parallel with Stages 4-5)
    |     Note: CDC analysis is executed in Stage 4 (mcu-compile-sim-run)
    |
Stage 7:  mcu-synthesis-planning           SDC generation + synthesis execution
    |
Stage 8:  mcu-equivalence-review           RTL vs netlist equivalence
    |
Stage 9:  mcu-pnr-implementation           Floorplan + P&R + GDS export
    |
Stage 10: mcu-signoff-review              Extraction + STA + Power + DRC + LVS
    |
Stage 11: mcu-report-and-handoff           Final report + deliverable inventory
```

### Fix Loop

When Stage 4 (compile/sim) fails:

1. `mcu-verification-triage` diagnoses the failure (log analysis + waveform if needed)
2. Diagnostic routes to `mcu-rtl-development` (RTL bug) or `mcu-tb-development` (TB bug)
3. The target skill applies incremental fix (only modify diagnosed files)
4. Back to Stage 4 recompile

Rules:
- Only files identified in the diagnostic are modified
- Change manifest tracks what was modified
- RTL internal fix → recompile only
- RTL interface change → recompile + re-lint + downstream cascade
- TB fix → recompile only, never affects synthesis/PnR
- **Max 3 fix-triage iterations** per failure cluster. If the same test still fails after 3 cycles, stop and escalate to the user with a summary of what was tried. Do not continue looping.

## Stage Definitions

### Stage 0 — EDA Environment Setup

| | |
|---|---|
| **Skill** | `mcu-eda-env-setup` |
| **Purpose** | Detect available EDA tools, validate PDK/library paths, check LSF, produce `eda_env.json` |
| **Entry** | Project directory exists |
| **Completion** | `eda_env.json` written, all required tool roles have a selected tool, no path blockers |
| **Outputs** | `eda_env.json`, path validation report |
| **Depends on** | Nothing — this is the first stage |

### Stage 1 — Specification & Architecture

| | |
|---|---|
| **Skill** | `mcu-spec-architecture-planning` |
| **Purpose** | Generate spec.md and architecture.md from product intent and CPU interface |
| **Entry** | Product requirements, CPU core datasheet or RTL header |
| **Completion** | `doc/spec.md` and `doc/architecture.md` with all 8 required sections |
| **Outputs** | spec.md, architecture.md, project directory structure |
| **Depends on** | Stage 0 |

### Stage 2 — RTL Development

| | |
|---|---|
| **Skill** | `mcu-rtl-development` |
| **Purpose** | Generate RTL modules, wire top-level, review integration, or incrementally fix from diagnostic |
| **Entry** | Stage 1 complete (full gen), or diagnostic from Stage 4 triage (incremental fix) |
| **Completion** | All modules have .v files, top-level wired, filelist.f complete |
| **Outputs** | RTL .v files, filelist.f, change manifest |
| **Depends on** | Stage 1 |

### Stage 3 — TB Development

| | |
|---|---|
| **Skill** | `mcu-tb-development` |
| **Purpose** | Plan test structure, generate TB/UVM code, or incrementally fix from diagnostic |
| **Entry** | Stage 2 complete (RTL exists), spec stable |
| **Completion** | TB compiles with DUT, directed tests exist, self-checking in place, test_list.json written |
| **Outputs** | TB .sv files, UVM infrastructure, sim filelist, test_list.json |
| **Depends on** | Stage 1 (spec for expected values), Stage 2 (RTL for DUT) |

### Stage 4 — Compile & Simulation

| | |
|---|---|
| **Skill** | `mcu-compile-sim-run` + `mcu-verification-triage` (on failure) |
| **Purpose** | Compile + simulate + lint + CDC. On failure: diagnose → incremental fix → recompile |
| **Entry** | filelist.f and filelist_sim.f exist, eda_env.json exists |
| **Completion** | Compile clean, simulation passes, lint 0 fatals |
| **Outputs** | compile.log, sim.log, waveform, run_record.json |
| **Depends on** | Stage 2 (RTL), Stage 3 (TB), Stage 0 (tools) |
| **Tools needed** | simulator, lint |
| **Fix loop** | fail → triage → rtl-development or tb-development (fix) → recompile |

### Stage 5 — Regression & Coverage

| | |
|---|---|
| **Skill** | `mcu-compile-sim-run` (regression mode) + `mcu-regression-and-coverage` |
| **Purpose** | Run multi-test regression with coverage, cluster failures, merge coverage, close gaps |
| **Entry** | Stage 4 passes, test_list.json from Stage 3 |
| **Completion** | Failures clustered, coverage at target, continue/stop decision made |
| **Outputs** | regression_record.json, merged coverage DB, coverage_gaps.json |
| **Depends on** | Stage 4 |
| **Tools needed** | simulator (coverage merge: urg/imc) |

### Stage 6 — Formal & Assertion

| | |
|---|---|
| **Skill** | `mcu-formal-and-assertion` |
| **Purpose** | Plan assertions, generate SVA code, review formal tool results |
| **Entry** | Protocol intent and reset rules clear from spec, RTL signal names available |
| **Completion** | SVA files generated in tb/sva/, bind file created |
| **Outputs** | property_plan.md, SVA .sv files, sva_bind.sv |
| **Depends on** | Stage 1 (spec), Stage 2 (RTL signal names) |
| **Note** | Can run in parallel with Stages 4-5 since it only depends on spec and RTL, not on simulation results |

### Stage 7 — Synthesis

| | |
|---|---|
| **Skill** | `mcu-synthesis-planning` |
| **Purpose** | Generate SDC constraints, run synthesis (DC/Genus), analyze QoR |
| **Entry** | Stage 4 passes at minimum, Stage 5 completion preferred |
| **Completion** | Netlist generated, WNS >= 0, power < budget |
| **Outputs** | SDC, netlist, SVF (DC only), timing/area/power reports |
| **Depends on** | Stage 4-5 (verification), Stage 0 (tools) |
| **Tools needed** | synthesizer |

### Stage 8 — Equivalence Review

| | |
|---|---|
| **Skill** | `mcu-equivalence-review` |
| **Purpose** | Verify RTL-to-netlist logical equivalence |
| **Entry** | Synthesis netlist exists |
| **Completion** | Equivalence PASS, all compare points matched |
| **Outputs** | fm_status.rpt, match statistics |
| **Depends on** | Stage 7 |
| **Tools needed** | equivalence |

### Stage 9 — Place & Route

| | |
|---|---|
| **Skill** | `mcu-pnr-implementation` |
| **Purpose** | Floorplan, placement, CTS, routing, GDS export |
| **Entry** | Equivalence PASS, PDK/LEF available |
| **Completion** | Timing closure, 0 DRC, netlist/DEF/SDC/GDS exported |
| **Outputs** | Final netlist, DEF, SDC, GDS, PnR reports |
| **Depends on** | Stage 8 |
| **Tools needed** | pnr |

### Stage 10 — Signoff Review

| | |
|---|---|
| **Skill** | `mcu-signoff-review` |
| **Purpose** | Parasitic extraction, STA, power, DRC, LVS |
| **Entry** | Routed design with GDS |
| **Completion** | STA timing met, power < budget, 0 DRC, LVS CORRECT |
| **Outputs** | SPEF, STA/power/DRC/LVS reports |
| **Depends on** | Stage 9 |
| **Tools needed** | extraction, sta, physical_ver |

### Stage 11 — Report & Handoff

| | |
|---|---|
| **Skill** | `mcu-report-and-handoff` |
| **Purpose** | Generate final_report.md and deliverable inventory |
| **Entry** | Relevant stages completed |
| **Completion** | Report generated, inventory complete, blockers documented |
| **Outputs** | final_report.md, deliverable_inventory.json |
| **Depends on** | All prior stages |

## Flow Progression Rules

### Forward Progression

1. Each stage should only start when its entry criteria are met.
2. Stages 3-5 (verification block) can have internal iteration — triage finds issues, fix RTL, re-triage.
3. Stages 4-5 are sequential within verification. Stage 6 (formal) can run in parallel with Stages 4-5 since it only depends on spec and RTL.
4. Do not start Stage 7 (synthesis) without at least Stage 4 (compile/sim) passing. Stage 5 (regression/coverage) completion is preferred.
5. Stages 7-10 form a strict pipeline: synthesis → equivalence → PnR → signoff.

### Rollback Rules

When a later stage fails, use [rollback-signal-patterns.md](references/rollback-signal-patterns.md) to decide where to go back:

| Failure at | Likely rollback to | Condition |
|---|---|---|
| Signoff (STA) | Synthesis (Stage 7) | Constraint issues, unrealistic timing targets |
| Signoff (DRC/LVS) | PnR (Stage 9) | Physical violations, missing connections |
| PnR (congestion) | Synthesis (Stage 7) or RTL (Stage 2) | Architecture-level area pressure |
| Equivalence | Synthesis (Stage 7) | Stale SVF, wrong black-box list |
| Verification | RTL (Stage 2) | Interface contract drift |

### Dependency Cascade

When upstream artifacts change, downstream stages must be reconsidered. See [dependency-cascade-rules.md](references/dependency-cascade-rules.md):

- **RTL change** → re-run Stages 4, 5, 6, 7, 8, 9, 10, 11
- **Constraint (SDC) change** → re-run Stages 7, 8, 9, 10, 11
- **Netlist change** → re-run Stages 8, 9, 10, 11
- **DEF/physical change** → re-run Stages 10, 11

## Resuming a Project

When entering a project mid-flow:

1. **Scan artifacts**: Check which stage outputs exist (spec.md? filelist.f? netlist? GDS?)
2. **Check freshness**: Are outputs newer than their inputs? (e.g. is the netlist newer than the RTL?)
3. **Identify current stage**: The earliest stage with missing or stale outputs is the current stage.
4. **Validate environment**: Run Stage 0 (`mcu-eda-env-setup`) if `eda_env.json` is missing or stale.
5. **Route to stage skill**: Use the stage definitions above to pick the right skill.

Use [artifact-entry-patterns.md](references/artifact-entry-patterns.md) when the user starts from a partial artifact.

## Bundled References

- [stage-selection-map.md](references/stage-selection-map.md) — artifact-to-stage routing table
- [artifact-entry-patterns.md](references/artifact-entry-patterns.md) — partial artifact routing rules
- [rollback-signal-patterns.md](references/rollback-signal-patterns.md) — when to go back to an earlier stage
- [dependency-cascade-rules.md](references/dependency-cascade-rules.md) — what to re-run after changes
- [flow-stage-checklist.md](references/flow-stage-checklist.md) — per-stage artifact checklist for project scanning
- [backup-and-safety-policy.md](references/backup-and-safety-policy.md) — mandatory backup rules, prohibited operations, protected directories

Use the bundled scripts and assets for structured output:

- [classify_mcu_entry.py](scripts/classify_mcu_entry.py)
- [flow-status-template.md](assets/flow-status-template.md)
- [route-decision-template.md](assets/route-decision-template.md)

## Completion Gate

This skill's job is done when:

- the user understands the full flow and their current position in it
- a specific stage skill is recommended with clear entry criteria met
- any rollback or dependency cascade is identified
- the recommended next step is actionable

## Decision Rules

- Always check Stage 0 (environment) before recommending execution stages (4, 5, 7-10).
- If the user is starting fresh, walk through Stages 0 → 1 → 2 → 3 sequentially.
- If the user has partial progress, scan artifacts to find the right re-entry point.
- Prefer the narrowest stage skill that matches the current need.
- Do not route forward when required upstream outputs are missing or stale.
- If a later-stage failure has an obvious upstream cause, recommend rollback first.
- If a recommended stage skill is not installed in the project, describe that stage's purpose and expected inputs/outputs so the user can perform the work manually or install the skill.

## Template Coverage Status

Not all stage skills have equal tool coverage. Bundled script templates primarily target the Synopsys + Calibre toolchain. The table below summarizes where Cadence or alternative tool templates are **not** bundled — users selecting those tools must supply equivalent scripts.

| Stage | Skill | Bundled templates | Not bundled (user-supplied) |
|-------|-------|-------------------|----------------------------|
| 0 | mcu-eda-env-setup | Detection covers all tools | — |
| 1 | mcu-spec-architecture-planning | Tool-agnostic | — |
| 2 | mcu-rtl-development | Tool-agnostic | — |
| 3 | mcu-tb-development | Tool-agnostic | — |
| 4 | mcu-compile-sim-run | VCS, Xcelium, SpyGlass | Ascent CDC |
| 5 | mcu-regression-and-coverage | Tool-agnostic | — |
| 6 | mcu-verification-triage | Tool-agnostic | — |
| 6a | mcu-formal-and-assertion | Tool-agnostic (SVA only) | — |
| 7 | mcu-synthesis-planning | DC, Genus | — |
| 8 | mcu-equivalence-review | Formality (template + parser) | Conformal (template only, no parser) |
| 9 | mcu-pnr-implementation | Innovus | ICC2 |
| 10 | mcu-signoff-review | StarRC, PrimeTime, Calibre | QRC, Tempus, ICV, Pegasus |
| 11 | mcu-report-and-handoff | Tool-agnostic | — |

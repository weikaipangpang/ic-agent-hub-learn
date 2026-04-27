---
name: frontend-workflow-guide
description: Orchestrate the full digital front-end design pipeline from spec to verified RTL. Defines the stage order, inter-stage handoff contracts, and routing logic. Use as the entry point to understand the complete flow, run the pipeline end-to-end, or determine the correct stage when entering mid-flow.
license: PolyForm-Noncommercial-1.0.0
metadata:
  author: 中科麒芯
  organization: 中科麒芯智能技术（南京）有限公司
  homepage: https://www.ickylin.com/
  contact: info@ickylin.com
---

# Frontend Workflow Guide

This skill defines the complete front-end design pipeline and orchestrates stage transitions.

## Boundaries

- Do not perform stage-specific analysis or generation work. Only orchestrate stage order.
- Do not make architecture decisions or generate code at the orchestration layer.
- Roll back decisively when needed. Advance decisively when prerequisites are met.

Use it to:

- understand the full stage order and what each stage produces
- run the pipeline from any starting point to completion
- determine the correct current stage when entering mid-flow
- handle rollback when a downstream stage discovers upstream problems

## Pipeline Stages

| Stage | Skill | Input | Output | Next |
|-------|-------|-------|--------|------|
| 1 | `frontend-spec-extraction` | Spec, protocol doc, register doc | Interface, register, parameter, clock/reset summary | Stage 2 |
| 2 | `frontend-spec-review` | Stage 1 output | ready/risky/blocked decision | Stage 3 (if ready) |
| 3 | `frontend-microarchitecture-analysis` | Stage 1 spec extraction + Stage 2 confirmed facts + perf/power requirements | Microarchitecture summary, architecture constraints | Stage 4 |
| 4 | `frontend-rtl-architecture` | Stage 2 confirmed facts + Stage 3 microarchitecture conclusions | RTL framework, module hierarchy, implementation order | Stage 5+6 |
| 5 | `frontend-rtl-gen` | Stage 4 architecture + Stage 1 spec | RTL `.sv` files in `rtl/` | Stage 7 |
| 6 | `frontend-tb-gen` | Stage 1 spec + Stage 4 architecture (ports only) | TB `.sv` files in `tb/` | Stage 7 |
| 7 | `frontend-integration-and-bringup` | Stage 5 RTL + Stage 6 TB | Filelist, integration review, Makefile plan | Stage 8 |
| 8 | `frontend-eda-env-setup` | Stage 7 plan + EDA environment | sim/Makefile, tool inventory, waveform config | Stage 9 |
| 9 | `frontend-compile-sim-run` | sim/Makefile + sim/flist | Compile/sim results, run record | Done or Stage 10 |
| 10 | `frontend-debug-triage` | compile.log / sim.log | Failure classification, fix recommendation | Stage 9 or Stage 11 |
| 11 | `frontend-wave-debug` | Stage 10 triage + waveform dump | Waveform findings, root cause | Stage 9 |

## Project Configuration

Every project needs an `input_config.json` at the project root. If the user only provides a spec file, Stage 1 (`frontend-spec-extraction`) auto-generates `input_config.json` from the template with sensible defaults. All paths are relative to the project root. No absolute paths allowed.

See [input_config.template.json](assets/input_config.template.json) for the template.

Fields:

| Field | Required | Description |
|-------|----------|-------------|
| `version` | Yes | Config format version (currently `"1.1"`) |
| `design_name` | Yes | Short name for the design (used in artifact filenames) |
| `spec.files` | Yes | List of spec file paths relative to project root |
| `spec.format` | Yes | `markdown`, `pdf`, or `docx` |
| `rtl.dir` | Yes | RTL source directory (relative) |
| `rtl.top_module` | Yes | Top module name |
| `rtl.include_dirs` | No | Additional include directories for compilation |
| `rtl.defines` | No | Preprocessor defines for compilation |
| `rtl.filelist` | No | Existing filelist path (if user provides, Stage 7 skips generation) |
| `tb.dir` | Yes | Testbench source directory (relative) |
| `tb.top_module` | Yes | TB top module name |
| `sim.dir` | Yes | Simulation working directory (relative) |
| `sim.simulator` | Yes | `auto`, `vcs`, `xcelium`, or `questa` |
| `sim.waveform` | No | `auto`, `verdi`, `dve`, or `simvision` |
| `sim.dump_format` | No | `auto`, `fsdb`, `vpd`, or `shm` |
| `sim.timescale` | No | Simulation timescale (default `1ns/1ps`) |
| `target.platform` | No | `asic` or `fpga` (affects performance constraints) |
| `target.clock_freq_mhz` | No | Clock frequency target in MHz (from spec) |
| `design_options` | No | Design-specific key-value options |
| `docs.dir` | Yes | Stage artifact output directory (relative) |

## Project Directory Structure

```
<project_root>/
  input_config.json
  specs/                         <-- input spec files
  docs/                          <-- stage artifacts (auto-generated)
    stage1_spec_extraction.json
    stage2_spec_review.json
    stage3_microarch_analysis.json
    stage4_rtl_architecture.json
    stage5_rtl_gen.json
    stage6_tb_gen.json
    stage7_integration_plan.json
    stage8_eda_env.json
    stage9_run_record.json
    stage10_debug_triage.json
    stage11_wave_debug.json
  rtl/                           <-- generated/user RTL
  tb/                            <-- generated/user TB
  sim/                           <-- simulation infrastructure
    flist
    Makefile
    backup/
```

## Stage Artifact Convention

| Stage | Reads | Writes |
|-------|-------|--------|
| 1 | spec files (+ `input_config.json`, auto-generated if absent) | `input_config.json` (if generated) + `stage1_spec_extraction.json` |
| 2 | `stage1_spec_extraction.json` | `stage2_spec_review.json` |
| 3 | `stage1_spec_extraction.json` + `stage2_spec_review.json` | `stage3_microarch_analysis.json` |
| 4 | `stage2_spec_review.json` + `stage3_microarch_analysis.json` | `stage4_rtl_architecture.json` |
| 5 | `stage4_rtl_architecture.json` + `stage3_microarch_analysis.json` (optional) + `stage1_spec_extraction.json` | `stage5_rtl_gen.json` + RTL files |
| 6 | `stage1_spec_extraction.json` + `stage4_rtl_architecture.json` | `stage6_tb_gen.json` + TB files |
| 7 | RTL files + TB files + `stage4_rtl_architecture.json` | `stage7_integration_plan.json` + `sim/flist` |
| 8 | `stage7_integration_plan.json` + EDA env | `stage8_eda_env.json` + `eda_detection.json` + `sim/Makefile` |
| 9 | `sim/Makefile` + `sim/flist` | `stage9_run_record.json` + logs |
| 10 | `stage9_run_record.json` + logs | `stage10_debug_triage.json` |
| 11 | `stage10_debug_triage.json` + waveform dump | `stage11_wave_debug.json` |

Rules:
- Each stage must check that its input artifact exists before starting.
- Each stage must write its output artifact before declaring completion.
- Artifact filenames are fixed by convention. Do not rename them.
- If `docs.dir` does not exist, the stage creates it.

## Stage Handoff Contracts

```
Spec --> [1.Extract] --> [2.Review] --> [3.MicroArch] --> [4.RTL Arch]
             ^             |  ^                               |
             |     blocked |  | fix                     +-----+-----+
             |             v  |                         |           |
             |          [1.Extract]                [5.RTL Gen] [6.TB Gen]
             |                                         |           |
             |                                         +-----+-----+
             |                                               |
             |                                        [7.Integration]
             |                                               |
             |                                        [8.EDA Setup]
             |                                               |
             |          +--------- fix --------+      [9.Compile/Sim]
             |          v                      |        |  ^  |
             +---- [10.Triage] ----+           |        |  |  | fail
                        |          |           |   pass |  +--+
                  needs waveform   +-----------+        |
                        v                               |
                   [11.Wave Debug] ----> fix ----> [9.Compile/Sim]
                        ^                               |
                        |        post-pass              |
                        +---------- health check -------+
                                    via [10.Triage]

All paths from Stage 9 (both pass and fail) route through Stage 10 then Stage 11,
ensuring all 12 skills execute in every pipeline run.
```

### Stage 2 Gate

Stage 2 (`spec-review`) is the critical gate:
- `ready` -proceed to Stage 3
- `risky` -proceed to Stage 3 with risk flags
- `blocked` -roll back to Stage 1

### Stage 5+6 Parallel

Stage 5 (`rtl-gen`) and Stage 6 (`tb-gen`) can run in parallel. Neither depends on the other.
- RTL gen: depends on architecture plan + spec
- TB gen: depends on spec (behavior) + architecture plan (ports only)
- Both must complete before Stage 7 (integration)

### Stage 9-10-11 Debug Loop and Post-Pass Path

**On failure:** Stage 9 routes to Stage 10 (log-based triage). Stage 10 may route to Stage 11 (waveform debug) if logs are insufficient. After fix, route back to Stage 9 for re-run (with backup). Maximum 3 rounds. If unresolved, escalate.

**On pass:** Stage 9 still routes to Stage 10 (post-pass health check: review compile/sim logs for warnings, verify no hidden issues) then to Stage 11 (verification wave dump: run sim_wave on one representative test, confirm key signals are correct in waveform). This ensures all 12 skills execute in every pipeline run.

## Safety Checks

### Stage 5 (`rtl-gen`) and Stage 6 (`tb-gen`) -Before Code Generation

| Check | Rule |
|-------|------|
| Existing files in rtl/ or tb/ | Backup to `<dir>/backup/<timestamp>/` before overwriting |
| Backup failure | Stop. Do not overwrite without successful backup |

### Stage 8 (`eda-env-setup`) -Before Makefile Generation

| Check | Rule |
|-------|------|
| Existing Makefile, same simulator | Skip regeneration entirely |
| Existing Makefile, different simulator | Backup `sim/` before clean and regenerate |
| Backup failure | Stop |

### Stage 9 (`compile-sim-run`) -Before Every Compile

| Check | Rule |
|-------|------|
| Existing `*.log` or coverage results | Backup to `sim/backup/<timestamp>/` before compile |
| First run | Skip backup |
| Backup failure | Stop |

### Backup Scope

- **Include:** `*.log`, `coverage_txt/`, coverage reports
- **Exclude:** `simv`, `csrc`, `simv.daidir`, `xcelium.d`, waveform dumps (too large, recompilable)
- **Format:** `<dir>/backup/YYYY-MM-DD_HH-MM-SS/`
- **Rule:** Never delete backup directories.

## Good Outcome

- The user knows which stage they are currently in.
- The user sees the full pipeline order and handoff relationships.
- Missing prerequisite artifacts are explicitly identified.
- Rollback happens decisively when needed; no blind forward push.

## Workflow (Orchestration)

1. Identify the user's current artifacts and goal.
2. Map to the current stage using the Pipeline Stages table.
3. Verify that upstream stage outputs exist and are stable.
4. If prerequisites are missing or contradictory, roll back to the corresponding stage.
5. If prerequisites are ready, execute the current stage skill in order.
6. Stages 5 and 6 can execute in parallel.
7. After stage completion, check the Completion Gate and advance to the next stage.
8. In the Stage 9-10-11 loop, track iteration count and escalate after 3 rounds.

## Mid-Flow Entry

| User has | Enter at | Prerequisite check |
|----------|----------|--------------------|
| Only spec | Stage 1 | None |
| Extraction results | Stage 2 | Stage 1 output exists |
| Review conclusion (ready) | Stage 3 | Stage 2 status not blocked |
| Microarchitecture analysis | Stage 4 | Stage 3 output exists |
| Architecture plan | Stage 5+6 | Stage 4 output exists |
| RTL + TB files | Stage 7 | RTL and TB files exist |
| Integration plan | Stage 8 | Stage 7 output exists |
| Makefile + flist | Stage 9 | sim/Makefile + sim/flist exist |
| Failure logs | Stage 10 | compile.log or sim.log exists |
| Needs waveform debug | Stage 11 | Stage 10 output + dump or needs re-run |

## Rollback Rules

| Current stage | Rollback signal | Roll back to |
|---------------|-----------------|--------------|
| Stage 3 (microarchitecture) | Extracted facts inconsistent | Stage 2 |
| Stage 4 (RTL architecture) | Microarchitecture constraints unresolved | Stage 3 |
| Stage 5 (RTL gen) | Architecture plan incomplete | Stage 4 |
| Stage 6 (TB gen) | Spec extraction incomplete | Stage 1 |
| Stage 7 (integration) | RTL/TB port mismatch | Stage 5 or 6 |
| Stage 8 (EDA env) | Filelist missing | Stage 7 |
| Stage 9 (compile/sim) | Makefile missing or stale | Stage 8 |
| Stage 9 (compile/sim) | Flist or source files missing | Stage 7 |
| Stage 10 (triage) | DUT/TB contract drift | Stage 7 |
| Stage 10 (triage) | Architecture-level issue | Stage 4 |
| Stage 10 (triage) | Spec-level issue | Stage 1 or 2 |
| Stage 11 (wave debug) | Dump missing, need re-run | Stage 9 (with dump enabled) |

## Bundled References

- Use [stage-selection-map.md](references/stage-selection-map.md) for detailed routing rules.
- Use [artifact-entry-patterns.md](references/artifact-entry-patterns.md) for mid-flow entry guidance.
- Use [rollback-signal-patterns.md](references/rollback-signal-patterns.md) for rollback decision patterns.

Use the bundled scripts and assets when structured output is useful:

- [classify_frontend_entry.py](scripts/classify_frontend_entry.py)
- [route-decision-template.md](assets/route-decision-template.md)
- [sample-artifact-inventory.json](assets/sample-artifact-inventory.json)
- [input_config.template.json](assets/input_config.template.json)

## Completion Gate

This skill is complete when:

- the user's current stage is identified
- the full remaining pipeline path is visible
- missing prerequisites are explicit
- rollback or stop conditions are clear

## Reusable Outputs

- current stage assessment
- full pipeline plan (remaining stages)
- missing prerequisite list
- rollback decisions (if any)
- next skill to execute

## Decision Rules

- Execute stages in pipeline order. Mid-flow entry is allowed when all prerequisite artifacts for the target stage exist and are stable (see Mid-Flow Entry table).
- Stage 2 is a hard gate: blocked status does not allow entry to Stage 3.
- Stages 5 and 6 are parallel: both must complete before Stage 7.
- Stage 9-10-11 loop is limited to 3 rounds maximum.
- When rolling back, prefer the nearest incomplete stage.
- Do not replace the deep work that belongs in a stage skill. Only orchestrate and hand off.

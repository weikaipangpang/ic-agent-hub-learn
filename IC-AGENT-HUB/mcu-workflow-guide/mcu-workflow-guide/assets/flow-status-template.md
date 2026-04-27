# Flow Status Report

## Project

- Design:
- Process:
- Date:

## Stage Status

| Stage | Skill | Status | Key Artifact | Notes |
|-------|-------|--------|-------------|-------|
| 0. EDA Env Setup | mcu-eda-env-setup | | eda_env.json | |
| 1. Spec & Architecture | mcu-spec-architecture-planning | | spec.md, architecture.md | |
| 2. RTL Development | mcu-rtl-development | | filelist.f, top module | |
| 3. TB Development | mcu-tb-development | | TB files, test_list.json | |
| 4. Compile & Simulation | mcu-compile-sim-run | | compile.log, sim.log | |
| 4t. Verification Triage | mcu-verification-triage | | diagnostic result | Sub-step of Stage 4 fix loop |
| 5. Regression & Coverage | mcu-regression-and-coverage | | regression_record.json, coverage report | |
| 6. Formal & Assertion | mcu-formal-and-assertion | | property_plan.md, SVA files | Can run parallel with 4-5 |
| 7. Synthesis | mcu-synthesis-planning | | netlist, timing rpt | |
| 8. Equivalence Review | mcu-equivalence-review | | fm_status.rpt | |
| 9. Place & Route | mcu-pnr-implementation | | final DEF, GDS | |
| 10. Signoff Review | mcu-signoff-review | | STA, DRC, LVS rpts | |
| 11. Report & Handoff | mcu-report-and-handoff | | final_report.md | |

Status values: not-started | in-progress | complete | blocked | needs-rerun

## Current Position

- Active stage:
- Reason:
- Blockers:

## Recommended Next Step


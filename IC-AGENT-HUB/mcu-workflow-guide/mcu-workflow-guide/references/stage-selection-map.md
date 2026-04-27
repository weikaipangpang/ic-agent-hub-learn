# Stage Selection Map

Use this table to map the user's current artifact to the most likely stage skill.

| Current artifact or problem | Primary skill | Fallback skill |
| --- | --- | --- |
| new project, no environment, tool issues, path errors | `mcu-eda-env-setup` | `cortex-m3-mcu-workflow-guide` |
| product intent, CPU interface notes, memory-map draft | `mcu-spec-architecture-planning` | `mcu-eda-env-setup` |
| architecture spec ready, need RTL source files | `mcu-rtl-development` | `mcu-spec-architecture-planning` |
| module list, interface definitions, partial top-level RTL | `mcu-rtl-development` | `mcu-rtl-development` |
| RTL ready, need testbench and verification infrastructure | `mcu-tb-development` | `mcu-rtl-development` |
| RTL and TB ready, need to compile and simulate | `mcu-compile-sim-run` | `mcu-tb-development` |
| compile log, sim log, lint errors, CDC report | `mcu-verification-triage` | `mcu-compile-sim-run` |
| triage says RTL bug, need incremental RTL fix | `mcu-rtl-development` (incremental fix mode) | `mcu-verification-triage` |
| triage says TB issue, need testbench fix | `mcu-tb-development` (incremental fix mode) | `mcu-verification-triage` |
| testcase outline, scenario list, sequence planning problem | `mcu-tb-development` | `mcu-verification-triage` |
| multiple test results, recurring failures, rerun decision problem | `mcu-regression-and-coverage` | `mcu-verification-triage` |
| coverage report, gap list, exclusion question | `mcu-regression-and-coverage` | `mcu-regression-and-coverage` |
| protocol checks, reset properties, FSM rules, safety conditions | `mcu-formal-and-assertion` | `mcu-verification-triage` |
| Formality result, compare-point failures, SVF, black-box mismatch | `mcu-equivalence-review` | `mcu-formal-and-assertion` |
| synthesis constraints, area/timing reports, QoR concerns | `mcu-synthesis-planning` | `mcu-rtl-development` |
| floorplan notes, congestion evidence, CTS or route issues | `mcu-pnr-implementation` | `mcu-synthesis-planning` |
| STA, power, DRC, LVS, extraction, GDS export concerns | `mcu-signoff-review` | `mcu-pnr-implementation` |
| milestone summary, customer update, stage handoff package | `mcu-report-and-handoff` | `cortex-m3-mcu-workflow-guide` |

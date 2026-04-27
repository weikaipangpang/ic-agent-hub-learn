# Frontend Stage Selection Map

Use this map to route the user to the right stage skill.

## If the user mainly has...

- a raw spec, interface description, register description, parameter list, or clock/reset notes
  - route to `frontend-spec-extraction`
- extracted views and needs a consistency check before deeper analysis
  - route to `frontend-spec-review`
- reviewed and confirmed facts, needs behavior or microarchitecture interpretation
  - route to `frontend-microarchitecture-analysis`
- a coherent design picture and needs RTL framework or module partitioning
  - route to `frontend-rtl-architecture`
- an architecture plan and needs RTL source code generated
  - route to `frontend-rtl-gen`
- spec extraction and architecture plan, needs testbench code generated
  - route to `frontend-tb-gen`
- RTL and TB files, needs integration review and filelist
  - route to `frontend-integration-and-bringup`
- needs to detect EDA tools, set up simulator, or generate Makefile
  - route to `frontend-eda-env-setup`
- needs to compile or simulate with safe backup
  - route to `frontend-compile-sim-run`
- compile or simulation logs with failures to diagnose
  - route to `frontend-debug-triage`
- log analysis insufficient, needs waveform inspection
  - route to `frontend-wave-debug`

## Rollback Rules

- If microarchitecture analysis depends on unreviewed or inconsistent facts, step back to `frontend-spec-review`.
- If RTL architecture depends on unresolved microarchitecture constraints, step back to `frontend-microarchitecture-analysis`.
- If RTL gen finds architecture plan incomplete, step back to `frontend-rtl-architecture`.
- If TB gen finds spec extraction incomplete, step back to `frontend-spec-extraction`.
- If integration finds RTL/TB port mismatch, step back to `frontend-rtl-gen` or `frontend-tb-gen`.
- If integration and bring-up depend on unclear module ownership or reset/clock/CDC ownership, step back to `frontend-rtl-architecture`.
- If compile-sim-run cannot find Makefile, step back to `frontend-eda-env-setup`.
- If compile-sim-run cannot find flist or source files, step back to `frontend-integration-and-bringup`.
- If debug evidence shows a shared DUT/TB contract drift, step back to `frontend-integration-and-bringup`.
- If debug evidence shows spec-level issue, step back to `frontend-spec-extraction` or `frontend-spec-review`.
- If wave debug finds dump missing, route back to `frontend-compile-sim-run` with dump enabled.

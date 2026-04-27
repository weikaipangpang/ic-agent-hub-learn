# Rollback Signal Patterns

Use these signals when the user appears to be late in the flow, but the real problem is upstream.

## Roll back to `frontend-spec-extraction`

- extracted facts still depend on major speculation
- interface or register meaning is still unstable
- debug triage reveals spec-level register or interface definition error

## Roll back to `frontend-spec-review`

- microarchitecture analysis depends on unreviewed or inconsistent extraction facts
- software-visible behavior and internal control assumptions still disagree

## Roll back to `frontend-microarchitecture-analysis`

- RTL architecture depends on unresolved microarchitecture constraints or behavior assumptions

## Roll back to `frontend-rtl-architecture`

- RTL gen finds architecture plan incomplete or contradictory
- bring-up or integration problems are really caused by unstable ownership, reset/clock/CDC boundaries, or parameter propagation
- debug triage reveals architecture-level issue

## Roll back to `frontend-rtl-gen` or `frontend-tb-gen`

- integration review finds RTL/TB port mismatch
- generated code has structural issues that need regeneration

## Roll back to `frontend-integration-and-bringup`

- compile-sim-run finds flist or source files missing
- debug evidence shows DUT/TB contract drift rather than a purely local compile or sim issue

## Roll back to `frontend-eda-env-setup`

- compile-sim-run finds no Makefile or Makefile is stale
- user wants to switch simulator

## Roll back to `frontend-compile-sim-run`

- debug triage fix applied, need to re-run with backup
- wave debug finds dump missing, need to re-run with dump enabled
- wave debug root cause fixed, need to verify with re-run

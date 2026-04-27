# Artifact Entry Patterns

Use these patterns when the user starts from mixed-stage evidence.

## Spec-first entry

- If the user only has a spec or partial requirement text, start at `frontend-spec-extraction`.
- Do not force microarchitecture or RTL planning before the engineering facts are stable enough.

## Extraction-first entry

- If the user already has extracted interface/register/parameter views but no review, start at `frontend-spec-review`.
- If the user already has reviewed and confirmed facts, start at `frontend-microarchitecture-analysis`.

## Architecture-first entry

- If the user has an architecture plan but no RTL code, start at `frontend-rtl-gen` and `frontend-tb-gen` in parallel.

## Code-first entry

- If the user already has RTL and TB files but no integration review, start at `frontend-integration-and-bringup`.

## Build-first entry

- If the user needs to set up a build environment or generate a Makefile, start at `frontend-eda-env-setup`.
- If the user already has a Makefile and wants to compile or simulate, start at `frontend-compile-sim-run`.

## Debug-first entry

- If the user starts from compile or sim logs, start at `frontend-debug-triage`.
- If log analysis is insufficient, proceed to `frontend-wave-debug`.
- Step back only when the logs or waveform reveal a more structural top, contract, or architecture contradiction.

# Artifact Entry Patterns

- If the user starts with only a CPU core datasheet or top-level intent, route to `mcu-spec-architecture-planning`.
- If the user has a design split but no stable integration contract, route to `mcu-rtl-development`.
- If the user starts with a failing tool log, route to `mcu-verification-triage` even if they mention later stages.
- If the user already has testcase intent but no clean case structure, route to `mcu-tb-development`.
- If the user has many failing tests rather than one failing test, route to `mcu-regression-and-coverage`.
- If the user starts from coverage evidence, route to `mcu-regression-and-coverage`.
- If the user starts from Formality output, route to `mcu-equivalence-review`.
- If the user has both a later-stage report and an obvious upstream contradiction, route to the upstream contradiction first.
- If the user asks for a customer-facing summary, route to `mcu-report-and-handoff`.

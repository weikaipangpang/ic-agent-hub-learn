# Rollback Signal Patterns

- Signoff failure caused by missing or unstable constraints should roll back to `mcu-synthesis-planning`.
- PnR trouble caused by unrealistic hierarchy or clock intent should roll back to `mcu-rtl-development` or `mcu-spec-architecture-planning`.
- Repeated verification failures caused by interface ambiguity should roll back to `mcu-spec-architecture-planning`.
- Coverage plateau caused by stale checker behavior should roll back to `mcu-verification-triage` or `mcu-tb-development`.
- Equivalence failure caused by stale synthesis guidance should roll back to `mcu-synthesis-planning`.
- Formal effort that depends on unstable reset behavior should roll back to `mcu-rtl-development`.

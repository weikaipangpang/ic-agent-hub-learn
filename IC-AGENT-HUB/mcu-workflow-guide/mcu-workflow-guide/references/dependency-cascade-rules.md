# Dependency Cascade Rules

Use these rules when deciding whether a change is local or whether downstream stages must be revisited.

- RTL changes usually force verification (compile/sim, regression, formal), synthesis, implementation, and signoff evidence to be reconsidered. Cascade: Stages 4, 5, 6, 7, 8, 9, 10, 11.
- Constraint changes usually force synthesis, implementation, and signoff evidence to be reconsidered. Cascade: Stages 7, 8, 9, 10, 11.
- Netlist changes usually invalidate equivalence, implementation, and signoff evidence. Cascade: Stages 8, 9, 10, 11.
- DEF or physical database changes usually invalidate at least the signoff timing and physical checks. Cascade: Stages 10, 11.

Do not recommend skipping dependency stages just because the local edit feels small.

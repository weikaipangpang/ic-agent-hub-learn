# Tool Selection Rules

When multiple tools are available for the same role, use these rules.

## Selection Priority

| Role | Priority 1 | Priority 2 | Priority 3 |
|------|-----------|-----------|-----------|
| simulator | VCS | Xcelium | — |
| lint | SpyGlass | Ascent | — |
| synthesizer | DC Shell | Genus | — |
| pnr | Innovus | ICC2 | — |
| equivalence | Formality | Conformal | — |
| sta | PrimeTime | Tempus | — |
| extraction | StarRC | QRC | — |
| physical_ver | Calibre | ICV | Pegasus |

## Override Rules

1. If `config/project.json → tools.<role>.name` specifies a tool, use it if available.
2. If the specified tool is unavailable, fallback to the next priority and warn.
3. If `auto` or omitted, use the priority order above.
4. If no tool is available for a role, report as blocker for stages that need it.

## Cross-Vendor Consistency

Some tool combinations work better together:

- Synopsys chain: VCS + DC + Formality + StarRC + PrimeTime + SpyGlass
- Cadence chain: Xcelium + Genus + Conformal + QRC + Tempus + Innovus
- Mixed is fine but note: Formality reads DC's SVF guidance; Conformal does not.

If the user has no preference and both vendors are fully available, prefer the chain that matches the synthesizer choice (since synthesis is the most path-dependent stage).

## Module Load

- If a tool is not in PATH, attempt `module load <module_name>` from the tool template.
- Use the site's environment init script (from `config.env.env_init_script`) before module load, if configured.
- If module load succeeds, re-check the tool and proceed.
- If module load fails, report the tool as unavailable. Do not modify shell config files.

## Roles and Stage Dependencies

| Role | Required by stages |
|------|-------------------|
| simulator | verification-triage, testcase-development, regression-management, coverage-closure |
| lint | verification-triage |
| synthesizer | synthesis-planning |
| pnr | pnr-implementation |
| equivalence | equivalence-review |
| sta | signoff-review |
| extraction | signoff-review |
| physical_ver | signoff-review |

If a role has no available tool, only the stages listed above are blocked. Other stages can proceed.

# Backup and Safety Policy

This document defines the mandatory backup and file safety rules for all stage skills in the MCU design flow.

## Prohibited Operations

The following operations are **strictly prohibited** at all times:

- `rm -rf` on any project directory
- `rm -rf *` or wildcard deletion without explicit path scoping
- `git clean -fdx` without user confirmation
- Deleting any directory that may contain source files, IP, or PDK
- Overwriting files without backup
- Force-removing lock files without investigating the owning process

## Protected Directories

The following directories must **never** be deleted or cleaned by any stage skill:

| Directory | Reason |
|-----------|--------|
| `rtl/` | RTL source files (design IP) |
| `tb/` | Testbench source files |
| `sdc/` | Timing constraint files |
| `doc/` | Specifications, architecture docs, reports |
| `config/` | Project configuration |
| PDK directory | Foundry process design kit (read-only) |
| Standard cell library directory | Vendor IP (read-only) |
| SRAM/IP macro directory | Third-party IP (read-only) |
| `.git/` | Version control history |
| `.claude/` | Claude Code configuration |
| `backup/` | Previous backup directories |

## Cleanable Directories

The following directories contain **regenerable outputs** and may be cleaned before a re-run, but only with backup:

| Directory | Stage | What it contains |
|-----------|-------|-----------------|
| `sim/simv`, `sim/csrc/`, `sim/simv.daidir/` | compile-sim-run | Compiled simulation binary (large, regenerable) |
| `sim/xcelium.d/` | compile-sim-run | Xcelium compile database (large, regenerable) |
| `output/syn/` | synthesis | Netlist, SDC, SVF, DDC |
| `output/pnr/` | pnr | DEF, netlist, database |
| `output/gds/` | pnr/signoff | GDS layout |
| `output/starrc/` | signoff | SPEF parasitic files |
| `output/pv/` | signoff | DRC/LVS results |
| `rpt/` | all stages | Tool reports |

## Backup Rules

### Before overwriting source files (RTL, TB, SDC)

```
backup/<YYYY-MM-DD_HH-MM-SS>/<original_path>
```

Example: before modifying `rtl/peripheral/gpio.v`:
```
cp rtl/peripheral/gpio.v backup/2026-04-11_14-30-00/rtl/peripheral/gpio.v
```

### Before re-running a stage

Back up the previous stage outputs (logs, reports) to:
```
sim/backup/<YYYY-MM-DD_HH-MM-SS>/
  compile.log
  sim.log
```

Do NOT back up large regenerable artifacts (simv, xcelium.d, waveform dumps). These are too large and can be recompiled.

### Before cleaning a stage

If a stage needs to be re-run from scratch:

1. Back up logs and reports to `backup/<timestamp>/`
2. Only delete the specific stage's output directory
3. Never use `rm -rf` with wildcards
4. Use explicit paths: `rm -rf output/syn/` is acceptable, `rm -rf output/` is NOT

## Stage-Specific Clean Scope

Each stage may only clean its own outputs. Cross-stage cleaning is prohibited.

| Skill | May clean | Must NOT touch |
|-------|-----------|---------------|
| `mcu-compile-sim-run` | `sim/simv`, `sim/csrc/`, `sim/simv.daidir/`, `sim/xcelium.d/` | `sim/*.log` (back up first), RTL, TB |
| `mcu-synthesis-planning` | `output/syn/`, `scripts/syn_*.tcl` | RTL, SDC source, PnR outputs |
| `mcu-pnr-implementation` | `output/pnr/`, `output/db/`, `scripts/pnr_*.tcl` | Synthesis outputs, RTL |
| `mcu-signoff-review` | `output/starrc/`, `output/pv/`, `output/gds/` | PnR outputs, synthesis outputs |
| `mcu-equivalence-review` | `rpt/fm_*` | Netlist, RTL |

## Backup Directory Rules

- Never delete backup directories
- Timestamp format: `YYYY-MM-DD_HH-MM-SS`
- If backup fails (disk full, permission error), stop the entire operation. Do not proceed without successful backup.
- Backup directories accumulate. Cleanup is a manual user decision, never automatic.

## Re-run Safety Protocol

When a stage needs to be re-run after upstream changes:

1. **Check** what upstream changed (read change manifest)
2. **Back up** current stage outputs (logs, reports)
3. **Clean** only the affected stage's regenerable outputs
4. **Re-run** the stage
5. **Verify** outputs are newer than inputs
6. **Record** the re-run in the change manifest

Never silently skip backup. Never assume the user wants outputs deleted.

## Waveform and Coverage Data

- Waveform dumps (`.fsdb`, `.shm`, `.vpd`) are large and regenerable. Do not back up.
- Coverage databases (`.vdb`, `cov_work/`) may contain multi-run merged data. Back up before re-running if coverage closure is in progress.

## Version Control Recommendation

If the project uses git:
- Commit source files (RTL, TB, SDC, config) before major re-runs
- Do not commit regenerable outputs (simv, netlist, GDS)
- Use `.gitignore` for output directories

# Flow Stage Checklist

Use this checklist to scan a project directory and determine which stages have been completed.

## Stage 0 — EDA Environment Setup

- [ ] `doc/eda_env.json` exists
- [ ] `config/project.json` exists

## Stage 1 — Specification & Architecture Planning

- [ ] `doc/spec.md` exists
- [ ] `doc/architecture.md` exists
- [ ] Project directories created (rtl/, tb/, sim/, scripts/, sdc/, output/, rpt/)

## Stage 2 — RTL Development

- [ ] `rtl/filelist.f` exists
- [ ] Top-level module file exists (e.g. `rtl/top/mcu_top.v`)
- [ ] At least one peripheral module exists

## Stage 3 — TB Development

- [ ] Testcase source files exist in `tb/`
- [ ] Testcase matrix or plan document exists
- [ ] `sim/filelist_sim.f` exists
- [ ] `doc/test_list.json` exists

## Stage 4 — Compile & Simulation

- [ ] `sim/compile.log` exists and shows clean compile
- [ ] `sim/sim.log` exists and contains SIM_PASS or TEST_PASSED
- [ ] `rpt/spyglass_lint.log` exists (0 fatals)

## Stage 5 — Regression & Coverage

- [ ] Multiple test logs exist in `sim/logs/`
- [ ] Regression summary exists (`doc/regression_record.json`)
- [ ] Coverage report exists (e.g. `sim/coverage/report/` or coverage database)
- [ ] Coverage gap analysis document exists (`doc/coverage_gaps.json`)

## Stage 6 — Formal & Assertion

- [ ] Property plan or assertion files exist (`tb/sva/`)
- [ ] Bind file exists (`tb/sva/sva_bind.sv`)
- [ ] Formal run logs exist (if formal was executed)

## Stage 7 — Synthesis

- [ ] `output/syn/<design>_syn.v` exists (netlist)
- [ ] `output/syn/<design>_syn.sdc` exists
- [ ] `rpt/syn_timing.rpt` exists
- [ ] WNS >= 0 in timing report

## Stage 8 — Equivalence Review

- [ ] `rpt/fm_status.rpt` exists (or equivalent tool report)
- [ ] Report shows PASS / Verification SUCCEEDED

## Stage 9 — Place & Route

- [ ] `output/pnr/<design>_final.v` exists
- [ ] `output/pnr/<design>_final.def` exists
- [ ] `output/gds/<design>.gds` exists
- [ ] PnR timing report shows WNS >= 0 and WHS >= 0

## Stage 10 — Signoff Review

- [ ] `output/starrc/<design>.spef` exists (or QRC equivalent)
- [ ] `rpt/pt_timing_setup.rpt` exists — WNS >= 0
- [ ] `rpt/pt_timing_hold.rpt` exists — WHS >= 0
- [ ] `rpt/pt_power.rpt` exists — total power < budget
- [ ] DRC results show 0 violations
- [ ] LVS result shows CORRECT

## Stage 11 — Report & Handoff

- [ ] `doc/final_report.md` exists
- [ ] Deliverable inventory is complete

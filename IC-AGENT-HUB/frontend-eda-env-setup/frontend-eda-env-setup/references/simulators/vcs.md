# VCS Simulator Template

name: vcs
role: simulator
vendor: Synopsys
check_command: which vcs
module_name: vcs/V-2023.12-SP1
waveform_tool: verdi

## Commands

compile: vcs -sverilog -full64 -Mupdate -f flist -debug_access+all -l compile.log
compile_cov: vcs -sverilog -full64 -Mupdate -f flist -debug_access+all -cm line+cond+fsm+tgl+branch -l compile.log
elaborate: (included in compile for VCS)
run: ./simv -l sim.log
run_cov: ./simv -cm line+cond+fsm+tgl+branch -l sim.log
wave: verdi -sverilog -f flist -ssf novas.fsdb &

## Incremental Compile

incremental_flag: -Mupdate
behavior: VCS tracks source file changes internally. Only recompiles modified modules.
benefit: Faster recompile when only a few files changed. Safe — if parameter/define changes, VCS detects and recompiles affected modules.

## Flags

testname_flag: +testname=
seed_flag: +ntb_random_seed=
log_flag: -l
timescale_flag: -timescale=1ns/1ps
define_flag: +define+

## Coverage

cov_report: urg -dir simv.vdb -format text -report coverage_txt
cov_merge: urg -dir *.vdb -dbname merged.vdb

## Waveform Dump

dump_format: fsdb
dump_compile_flags: -kdb -debug_access+all
dump_define: +define+DUMP_WAVES
dump_runtime_flags: +fsdb+autoflush
dump_tcl: TB uses `ifdef DUMP_WAVES to guard $fsdbDumpfile/$fsdbDumpvars (compile-time control)
dump_extension: .fsdb
wave_open: verdi -ssf dump.fsdb &

Note: sim_wave requires compile_wave (with dump_define). Do NOT put +define+ in runtime flags.

## Clean

clean: rm -rf simv csrc simv.daidir *.log *.fsdb novas.* *.vdb coverage_txt ucli.key

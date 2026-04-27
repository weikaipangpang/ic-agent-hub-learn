# VCS Detection Template

name: vcs
vendor: Synopsys
role: simulator
check_command: which vcs
version_command: vcs -ID 2>&1 | grep -i version | head -1
module_name: (site-specific, e.g. vcs/<version> — read from project config modules.vcs)
binary: vcs
waveform_tool: verdi

## Execution Pattern

compile: vcs -full64 -sverilog -debug_access+all -f <filelist> -o <simdir>/simv -l <simdir>/compile.log +lint=all,noVCDE -timescale=1ns/1ps
simulate: ./simv <plusargs> +fsdbfile+<fsdb_path> -l <sim_log>
script_format: command-line (no TCL)
execution_mode: sync

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

## Waveform

dump_tool: verdi
dump_format: fsdb
dump_compile_flags: -kdb -debug_access+all
dump_runtime_flags: -fsdb +fsdb+autoflush
dump_tcl: $fsdbDumpfile("dump.fsdb"); $fsdbDumpvars(0, tb_top);
dump_extension: .fsdb
wave_open: verdi -ssf dump.fsdb &

## Coverage

cov_compile: vcs ... -cm line+cond+fsm+tgl+branch
cov_run: ./simv -cm line+cond+fsm+tgl+branch
cov_report: urg -dir simv.vdb -format text -report coverage_txt
cov_merge: urg -dir *.vdb -dbname merged.vdb

## Success Detection

compile_success: simv executable exists
simulate_pass: log contains TEST_PASSED or SIM_PASS
simulate_fail: log contains TEST_FAILED or SIM_FAIL or UVM_FATAL

## Auto-Diagnosis Patterns

- VCS cache corruption → clean csrc/ and recompile
- SV keyword conflict → rename identifier
- Illegal rand type → remove rand qualifier
- ASLR re-execution → retry with -no_save

## Clean

clean: rm -rf simv csrc simv.daidir *.log *.fsdb novas.* *.vdb coverage_txt ucli.key

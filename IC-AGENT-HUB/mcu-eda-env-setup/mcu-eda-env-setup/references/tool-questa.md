# Questa Detection Template

name: questa
vendor: Siemens
role: simulator
check_command: which vsim
version_command: vsim -version 2>&1 | head -1
module_name: (site-specific, e.g. questa/<version> — read from project config modules.questa)
binary: vsim
waveform_tool: visualizer

## Execution Pattern

compile: vlog -sv -incr -f flist -l compile.log && vopt -incr +acc tb_top -o opt_tb -l elab.log
elaborate: (included in compile via vopt)
simulate: vsim -c opt_tb -do "run -all; quit" -l sim.log
script_format: command-line + TCL do-file
execution_mode: sync

## Incremental Compile

incremental_flag: -incr (for both vlog and vopt)
behavior: Questa tracks source file changes in work library. vlog -incr only recompiles modified files. vopt -incr only re-optimizes affected modules.
benefit: Faster recompile when only a few files changed. Safe — detects parameter/define/include changes via dependency tracking in work library.

## Flags

testname_flag: +UVM_TESTNAME=
seed_flag: -sv_seed
log_flag: -l
timescale_flag: -timescale 1ns/1ps
define_flag: +define+

## Waveform

dump_tool: visualizer
dump_format: wlf
dump_compile_flags: +acc
dump_runtime_flags: -wlf vsim.wlf
dump_tcl: log -r /*;
dump_extension: .wlf
wave_open: vsim -view vsim.wlf &

## Coverage

cov_compile: vlog -sv -incr -f flist && vopt -incr +acc +cover=bcesxf tb_top -o opt_tb
cov_run: vsim -c -coverage opt_tb -do "run -all; quit" -l sim.log
cov_report: vcover report -details -output coverage_txt merged.ucdb
cov_merge: vcover merge merged.ucdb *.ucdb

## Success Detection

compile_success: no Error in compile.log
simulate_pass: log contains TEST_PASSED or SIM_PASS
simulate_fail: log contains TEST_FAILED or SIM_FAIL or UVM_FATAL

## Clean

clean: rm -rf work transcript *.log *.wlf *.ucdb coverage_txt modelsim.ini

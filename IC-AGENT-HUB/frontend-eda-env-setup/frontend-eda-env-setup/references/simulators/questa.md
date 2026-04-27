# Questa Simulator Template

name: questa
role: simulator
vendor: Siemens
check_command: which vsim
module_name: questa/latest
waveform_tool: visualizer

## Commands

compile: vlog -sv -incr -f flist -l compile.log && vopt -incr +acc tb_top -o opt_tb -l elab.log
compile_cov: vlog -sv -incr -f flist -l compile.log && vopt -incr +acc +cover=bcesxf tb_top -o opt_tb -l elab.log
elaborate: (included in compile via vopt)
run: vsim -c opt_tb -do "run -all; quit" -l sim.log
run_cov: vsim -c -coverage opt_tb -do "run -all; quit" -l sim.log
wave: vsim -view vsim.wlf &

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

## Coverage

cov_report: vcover report -details -output coverage_txt merged.ucdb
cov_merge: vcover merge merged.ucdb *.ucdb

## Waveform Dump

dump_format: wlf
dump_compile_flags: +acc
dump_runtime_flags: -wlf vsim.wlf
dump_tcl: log -r /*;
dump_extension: .wlf
wave_open: vsim -view vsim.wlf &

## Clean

clean: rm -rf work transcript *.log *.wlf *.ucdb coverage_txt modelsim.ini

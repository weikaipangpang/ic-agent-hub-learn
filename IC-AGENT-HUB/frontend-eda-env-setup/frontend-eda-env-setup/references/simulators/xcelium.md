# Xcelium Simulator Template

name: xcelium
role: simulator
vendor: Cadence
check_command: which xrun
module_name: xcelium/23.09
waveform_tool: simvision

## Commands

compile: xrun -compile -sv -update -f flist -l compile.log
compile_cov: xrun -compile -sv -update -f flist -coverage all -l compile.log
elaborate: xrun -elaborate -sv -f flist -l elab.log
run: xrun -R -l sim.log
run_cov: xrun -R -coverage all -l sim.log
wave: simvision waves.shm &

## Incremental Compile

incremental_flag: -update
behavior: Xcelium tracks source file changes in xcelium.d snapshot. Only recompiles modified files.
benefit: Faster recompile when only a few files changed. Safe — detects parameter/define/include changes.

## Flags

testname_flag: +testname=
seed_flag: -svseed
log_flag: -l
timescale_flag: -timescale 1ns/1ps
define_flag: +define+

## Coverage

cov_report: imc -load cov_work/scope/test -report -metrics all -out coverage_txt
cov_merge: imc -load cov_work -merge -out merged_cov

## Waveform Dump

dump_format: shm
dump_compile_flags: -access +rwc
dump_define: +define+DUMP_WAVES
dump_runtime_flags: (none, use tcl probe)
dump_tcl: TB uses `ifdef DUMP_WAVES to guard dump calls (compile-time control)
dump_extension: .shm
wave_open: simvision waves.shm &

Note: sim_wave requires compile_wave (with dump_define). Do NOT put +define+ in runtime flags.

## Clean

clean: rm -rf xcelium.d xrun.* *.log waves.shm cov_work coverage_txt .simvision

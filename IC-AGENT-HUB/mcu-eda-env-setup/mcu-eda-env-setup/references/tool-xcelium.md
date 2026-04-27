# Xcelium Detection Template

name: xcelium
vendor: Cadence
role: simulator
check_command: which xrun
version_command: xrun -version 2>&1 | head -1
module_name: (site-specific, e.g. xcelium/<version> — read from project config modules.xcelium)
binary: xrun
waveform_tool: simvision

## Execution Pattern

compile: xrun -compile -sv -f <filelist> -l compile.log
elaborate: xrun -elaborate -sv -f <filelist> -l elab.log
simulate: xrun -R -l sim.log
script_format: command-line (no TCL)
execution_mode: sync

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

## Waveform

dump_tool: simvision
dump_format: shm
dump_compile_flags: -access +rwc
dump_runtime_flags: (use tcl probe)
dump_tcl: database -open waves.shm -default; probe -all -depth all; run;
dump_extension: .shm
wave_open: simvision waves.shm &

## Coverage

cov_compile: xrun -compile -sv -f <filelist> -coverage all
cov_run: xrun -R -coverage all
cov_report: imc -load cov_work/scope/test -report -metrics all -out coverage_txt
cov_merge: imc -load cov_work -merge -out merged_cov

## Success Detection

compile_success: no FATAL errors in compile.log
simulate_pass: log contains TEST_PASSED or SIM_PASS
simulate_fail: log contains TEST_FAILED or SIM_FAIL or UVM_FATAL

## Clean

clean: rm -rf xcelium.d xrun.* *.log waves.shm cov_work coverage_txt .simvision

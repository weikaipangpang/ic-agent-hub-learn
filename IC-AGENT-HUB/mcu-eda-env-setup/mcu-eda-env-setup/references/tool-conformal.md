# Conformal Detection Template

name: conformal
vendor: Cadence
role: equivalence
check_command: which lec
version_command: lec -version 2>&1 | head -1
module_name: (site-specific, e.g. conformal/<version> — read from project config modules.conformal)
binary: lec

## Execution Pattern

verify: lec -dofile <do_file> -log <log_path>
script_format: dofile (Conformal command syntax)
execution_mode: sync

## Dofile Structure

1. read_library -liberty <.lib files>
2. read_design -golden <rtl_files> -top <top>
3. read_design -revised <netlist> -top <top>
4. set_black_box <module>
5. set_flatten_model -golden / -revised
6. add_compared_points -all
7. compare
8. report_compare_data

## Key Differences from Formality

- Does not use SVF guidance (pairs naturally with Genus)
- Uses dofile format instead of TCL
- Different command names (read_design vs read_verilog)
- Better suited when synthesizer is Genus

## Success Detection

Log shows "Equivalent" result.

## Clean

rm -rf lec_* *.log

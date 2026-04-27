# Tempus Detection Template

name: tempus
vendor: Cadence
role: sta
check_command: which tempus
version_command: tempus -version 2>&1 | head -1
module_name: (site-specific, e.g. tempus/<version> — read from project config modules.tempus)
binary: tempus

## Execution Pattern

sta: tempus -batch -files <tcl_script> -log <log_prefix>
script_format: TCL
execution_mode: sync

## TCL Script Structure

1. read_lib <.lib files>
2. read_verilog <netlist>
3. read_def <def> (optional, for physical-aware STA)
4. read_spef <spef_file>
5. read_sdc <sdc>
6. set_analysis_view (MMMC-style)
7. report_timing -setup / -hold
8. report_power

## Key Differences from PrimeTime

- Uses .lib instead of .db for timing libraries
- Can read DEF for physical-aware analysis
- MMMC analysis view setup similar to Innovus
- TCL command syntax differs (read_lib vs set target_library)
- Better suited when PnR tool is Innovus (shared view setup)

## Success Detection

Timing reports generated and log shows completion.

## Clean

rm -rf tempus.* *.log reports

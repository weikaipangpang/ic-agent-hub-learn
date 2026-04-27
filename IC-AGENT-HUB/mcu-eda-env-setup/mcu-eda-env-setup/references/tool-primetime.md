# PrimeTime Detection Template

name: primetime
vendor: Synopsys
role: sta
check_command: which pt_shell
version_command: pt_shell -version 2>&1 | head -1
module_name: (site-specific, e.g. pts/<version> — read from project config modules.primetime)
binary: pt_shell

## Execution Pattern

sta: pt_shell -f <tcl_script> -output_log_file <log_path>
power: pt_shell -f <tcl_script> -output_log_file <log_path>
script_format: TCL
execution_mode: sync

## TCL Script Structure — STA

1. set_app_var target_library / link_library
2. read_verilog <netlist>
3. link_design
4. read_parasitics -format spef <spef_file>
5. source <sdc_file>
6. check_timing
7. report_timing -setup / -hold
8. report_constraint -all_violators

## TCL Script Structure — Power

1. Same library/netlist/parasitic setup
2. read_saif / read_vcd (activity source, optional)
3. set_switching_activity (default toggle if no activity file)
4. report_power

## Key Inputs

netlist: gate-level (from synthesis or post-PnR)
sdc: timing constraints
spef: parasitics (from StarRC or QRC)
activity: SAIF or VCD file (optional, for power)
libraries: .db files for the analysis corner

## Key Outputs — STA

setup_timing: <rpt_dir>/pt_timing_setup.rpt
hold_timing: <rpt_dir>/pt_timing_hold.rpt
violations: <rpt_dir>/pt_violations.rpt
check_timing: <rpt_dir>/pt_check_timing.rpt
qor: <rpt_dir>/pt_qor.rpt

## Key Outputs — Power

power: <rpt_dir>/pt_power.rpt
power_hier: <rpt_dir>/pt_power_hier.rpt

## Success Detection — STA

Parses: SETUP_WNS, HOLD_WHS, SETUP_VIOLATIONS, HOLD_VIOLATIONS
Timing met: WNS >= 0 AND WHS >= 0

## Success Detection — Power

Parses: POWER_DYNAMIC_MW, POWER_LEAKAGE_MW, POWER_TOTAL_MW
Power met: total power < budget from config

## Clean

rm -rf pt_work *.log <rpt_dir>/pt_*

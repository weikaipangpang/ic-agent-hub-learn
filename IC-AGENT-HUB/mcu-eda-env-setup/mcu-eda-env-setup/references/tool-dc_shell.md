# DC Shell Detection Template

name: dc_shell
vendor: Synopsys
role: synthesizer
check_command: which dc_shell
version_command: dc_shell -version 2>&1 | head -1
module_name: (site-specific, e.g. syn/<version> — read from project config modules.dc_shell)
binary: dc_shell

## Execution Pattern

synthesize: dc_shell -f <tcl_script> | tee <log_path>
script_format: TCL
execution_mode: async (via LSF)

## TCL Script Structure

1. Library setup (target_library, link_library, search_path)
2. Read design (read_file -format verilog for each RTL file from filelist)
3. Set current_design
4. Source SDC constraints
5. compile_ultra -no_autoungroup (or compile_ultra with effort setting)
6. Report: timing, area, power, qor
7. Write outputs: netlist (.v), constraints (.sdc), guidance (.svf), database (.ddc)

## Key Outputs

netlist: <output_dir>/<design>_syn.v
sdc: <output_dir>/<design>_syn.sdc
svf: <output_dir>/<design>.svf (for Formality)
ddc: <output_dir>/<design>.ddc

## Reports

timing: <rpt_dir>/syn_timing.rpt
area: <rpt_dir>/syn_area.rpt
power: <rpt_dir>/syn_power.rpt
qor: <rpt_dir>/syn_qor.rpt

## Library Requirements

- target_library: corner-specific .db files (e.g. ss corner for setup)
- link_library: target_library + SRAM .db files + "*" (designware)
- search_path: directories containing .db files

## Success Detection

Log contains synthesis completion marker and output netlist exists.

## Clean

rm -rf work alib-52 *.log reports *.svf command.log default.svf

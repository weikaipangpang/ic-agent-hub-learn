# Genus Detection Template

name: genus
vendor: Cadence
role: synthesizer
check_command: which genus
version_command: genus -version 2>&1 | head -1
module_name: (site-specific, e.g. genus/<version> — read from project config modules.genus)
binary: genus

## Execution Pattern

synthesize: genus -f <tcl_script> -log <log_path>
script_format: TCL
execution_mode: async (via LSF)

## TCL Script Structure

1. set_db init_lib_search_path <paths>
2. read_libs <.lib files>
3. read_hdl -sv -f <filelist>
4. elaborate <top_module>
5. read_sdc <sdc_file>
6. syn_generic / syn_map / syn_opt
7. report_timing / report_area / report_power
8. write_hdl > <netlist>
9. write_sdc > <sdc>

## Key Outputs

netlist: <output_dir>/<design>_syn.v
sdc: <output_dir>/<design>_syn.sdc

## Reports

timing: <rpt_dir>/syn_timing.rpt
area: <rpt_dir>/syn_area.rpt
power: <rpt_dir>/syn_power.rpt
qor: <rpt_dir>/syn_qor.rpt

## Library Requirements

- .lib files (Liberty text format, not .db)
- LEF files for physical-aware synthesis (optional)

## Differences from DC

- Uses .lib instead of .db for timing libraries
- Three-phase synthesis (generic → map → opt) vs compile_ultra
- Does not produce SVF guidance file (use Conformal for equivalence)
- TCL command syntax differs significantly

## Success Detection

Log shows synthesis completion and output netlist exists.

## Clean

rm -rf fv genus.* *.log reports

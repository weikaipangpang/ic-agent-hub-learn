# ICC2 Detection Template

name: icc2
vendor: Synopsys
role: pnr
check_command: which icc2_shell
version_command: icc2_shell -version 2>&1 | head -1
module_name: (site-specific, e.g. icc2/<version> — read from project config modules.icc2)
binary: icc2_shell

## Execution Pattern

run: icc2_shell -f <tcl_script> | tee <log_path>
script_format: TCL
execution_mode: async (via LSF)

## TCL Script Structure

1. create_lib / open_lib (NDM library)
2. read_verilog / link_block
3. read_def (floorplan)
4. create_placement
5. clock_opt
6. route_auto
7. route_opt
8. report_timing / report_area / report_power
9. save_lib / write_gds

## Key Differences from Innovus

- Uses NDM (New Data Model) library format instead of LEF/DEF directly
- Requires .ndm files for standard cells and macros
- TCL command namespace differs (create_placement vs place_opt_design)
- MCMM setup through set_scenario/create_scenario
- Power planning through create_pg_* commands

## Library Requirements

- NDM libraries for standard cells
- NDM libraries for macros
- Tech file
- TLU+ files

## Success Detection

Library saved and output netlist/GDS exists.

## Clean

rm -rf <lib_dir> *.log reports

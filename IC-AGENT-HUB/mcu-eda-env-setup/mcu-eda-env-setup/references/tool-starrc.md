# StarRC Detection Template

name: starrc
vendor: Synopsys
role: extraction
check_command: which StarXtract
version_command: StarXtract -version 2>&1 | head -1
module_name: (site-specific, e.g. starrc/<version> — read from project config modules.starrc)
binary: StarXtract

## Execution Pattern

extract: StarXtract <cmd_file>
script_format: command file (NOT TCL, proprietary format)
execution_mode: async (via LSF)

## Command File Structure

```
BLOCK: <design>
STAR_DIRECTORY: <work_dir>
GDS_FILE: <gds_path>
TOP_DEF_FILE: <def_path>
LEF_FILE: <lef_files>
TCAD_GRD_FILE: <nxtgrd_path>
MAPPING_FILE: <layer_map>
EXTRACTION: RC
COUPLE_TO_GROUND: NO
NETS: *
OPERATING_TEMPERATURE: <temp>
NETLIST_FORMAT: SPEF
NETLIST_FILE: <output_spef>
```

## Key Inputs

gds: layout GDS (from Innovus export)
def: design DEF (from Innovus)
lef: tech LEF + cell LEF + macro LEF
nxtgrd: StarRC technology file per corner
layer_map: GDS layer mapping

## Key Outputs

spef: <output_dir>/<design>_<corner>.spef

## Corner Mapping

cworst (ss): high-temperature worst-case RC
cbest (ff): low-temperature best-case RC

## Success Detection

SPEF file exists and log shows completion.

## Clean

rm -rf star_* *.log <output_dir>/*.spef

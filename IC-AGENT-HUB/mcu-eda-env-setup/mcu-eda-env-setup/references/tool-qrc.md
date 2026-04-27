# QRC Detection Template

name: qrc
vendor: Cadence
role: extraction
check_command: which qrc
version_command: qrc -version 2>&1 | head -1
module_name: (site-specific, e.g. qrc/<version> — read from project config modules.qrc)
binary: qrc

## Execution Pattern

extract: qrc -cmd <cmd_file>
script_format: command file
execution_mode: async (via LSF)

## Command File Structure

```
extract -selection all
output_setup -file_type SPEF -net_name_space VERILOG
```

Typically invoked from within Innovus (setExtractRCMode + extractRC) rather than standalone.

## Key Differences from StarRC

- Native integration with Innovus (can extract in-design)
- Uses QRC tech file instead of nxtgrd
- Different command file syntax
- Better suited when PnR tool is Innovus

## Key Inputs

def: design DEF
lef: tech + cell + macro LEF
qrc_tech: QRC technology file per corner

## Key Outputs

spef: <output_dir>/<design>_<corner>.spef

## Success Detection

SPEF file exists.

## Clean

rm -rf qrc_* *.log <output_dir>/*.spef

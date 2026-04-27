# Pegasus Detection Template

name: pegasus
vendor: Cadence
role: physical_ver
check_command: which pegasus
version_command: pegasus -version 2>&1 | head -1
module_name: (site-specific, e.g. pegasus/<version> — read from project config modules.pegasus)
binary: pegasus

## Execution Pattern

drc: pegasus -drc <rule_file> -gds <gds> -top_cell <top> -report <results_dir>
lvs: pegasus -lvs <rule_file> -gds <gds> -top_cell <top> -spice <netlist> -report <results_dir>
script_format: Pegasus rule format
execution_mode: sync

## Key Differences from Calibre

- Cadence tool, integrates with Innovus natively
- Can run in-design from Innovus (signoff DRC without GDS export)
- Different rule format
- Better suited for Cadence PnR flow

## Key Inputs

gds: layout GDS
rule_file: PDK Pegasus DRC/LVS rules
netlist: gate-level netlist (for LVS)

## Success Detection

DRC: 0 violations
LVS: MATCH result

## Clean

rm -rf pegasus_* *.log <results_dir>

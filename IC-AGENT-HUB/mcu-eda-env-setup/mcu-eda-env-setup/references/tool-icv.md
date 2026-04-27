# ICV Detection Template

name: icv
vendor: Synopsys
role: physical_ver
check_command: which icv_comp
version_command: icv_comp -version 2>&1 | head -1
module_name: (site-specific, e.g. icv/<version> — read from project config modules.icv)
binary: icv_comp

## Execution Pattern

drc: icv_comp -i <gds> -c <top_cell> -f <rule_file> -sf <results_dir>
lvs: icv_comp -i <gds> -c <top_cell> -f <rule_file> -sf <results_dir> -s <netlist>
script_format: rule file (ICV format)
execution_mode: sync

## Key Differences from Calibre

- Synopsys tool, integrates with StarRC and PrimeTime
- Different rule file format (not SVRF)
- Native support for Synopsys flow outputs
- Better suited for all-Synopsys tool chain

## Key Inputs

gds: layout GDS
rule_file: PDK ICV DRC/LVS rules
netlist: gate-level netlist (for LVS)

## Success Detection

DRC: 0 violations in summary
LVS: MATCH result

## Clean

rm -rf icv_* *.log <results_dir>

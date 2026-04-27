# Calibre Detection Template

name: calibre
vendor: Siemens (Mentor)
role: physical_ver
check_command: which calibre
version_command: calibre -version 2>&1 | head -1
module_name: (site-specific, e.g. calibre/<version> — read from project config modules.calibre)
binary: calibre

## Execution Pattern

drc: calibre -drc -hier <runset_file> 2>&1 | tee <log_path>
lvs: calibre -lvs -hier <runset_file> 2>&1 | tee <log_path>
script_format: runset file (Calibre SVRF format, NOT TCL)
execution_mode: sync

## Runset Structure — DRC

```
LAYOUT PATH "<gds_path>"
LAYOUT PRIMARY "<top_cell>"
LAYOUT SYSTEM GDSII

DRC RESULTS DATABASE "<results_db_path>" ASCII
DRC SUMMARY REPORT "<summary_path>"

INCLUDE "<drc_rule_deck_path>"
```

## Runset Structure — LVS

```
LAYOUT PATH "<gds_path>"
LAYOUT PRIMARY "<top_cell>"
LAYOUT SYSTEM GDSII

SOURCE PATH "<netlist_path>"
SOURCE PRIMARY "<top_cell>"
SOURCE SYSTEM VERILOG

LVS REPORT "<report_path>"

INCLUDE "<lvs_rule_deck_path>"
```

## Key Inputs

gds: layout GDS
drc_rules: PDK DRC rule deck
lvs_rules: PDK LVS rule deck
netlist: gate-level netlist (for LVS source)

## Key Outputs — DRC

results_db: <results_dir>/drc_results.db
summary: <results_dir>/drc_summary.rpt

## Key Outputs — LVS

report: <results_dir>/lvs_results.rpt
summary: <results_dir>/lvs_summary.rpt

## Success Detection — DRC

Parse summary for per-rule violation counts. Success = total violations == 0.

## Success Detection — LVS

Parse report for CORRECT vs INCORRECT. Success = CORRECT.

## Clean

rm -rf svdb *.log <results_dir>

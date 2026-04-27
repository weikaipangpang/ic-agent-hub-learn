# Formality Detection Template

name: formality
vendor: Synopsys
role: equivalence
check_command: which fm_shell
version_command: fm_shell -version 2>&1 | head -1
module_name: (site-specific, e.g. syn/<version> — read from project config modules.formality)
binary: fm_shell

## Execution Pattern

verify: fm_shell -file <tcl_script> 2>&1 | tee <log_path>
script_format: TCL
execution_mode: sync

## TCL Script Structure

1. Set reference (RTL): read_verilog -r <rtl_files> + set_top r:/<top>
2. Set implementation (netlist): read_verilog -i <netlist> + set_top i:/<top>
3. Read SVF guidance: set_svf <svf_file> (from DC synthesis)
4. Set black boxes: set_black_box <module> (for CPU cores, hard IP)
5. Read libraries: read_db <.db files>
6. match / verify
7. Report: status, failing points, matched/unmatched counts

## Key Inputs

reference: RTL filelist (same as synthesis input)
implementation: synthesized netlist (from DC output)
svf: guidance file from DC (maps clock gating transforms etc.)
libraries: same .db files used in synthesis
black_boxes: CPU core modules, third-party IP

## Key Outputs

status_report: <rpt_dir>/fm_status.rpt
failing_report: <rpt_dir>/fm_failing.rpt (only if FAIL)
log: <rpt_dir>/fm.log

## Success Detection

Log contains "Verification SUCCEEDED" or FORMAL_RESULT:PASS
Match statistics: FM_MATCHED_POINTS:N, FM_UNMATCHED_POINTS:N

## Cross-Tool Note

Formality reads DC's SVF file. If the synthesizer is Genus (not DC), SVF is not available — use Conformal instead for equivalence.

## Clean

rm -rf fm_work *.log <rpt_dir>/fm*

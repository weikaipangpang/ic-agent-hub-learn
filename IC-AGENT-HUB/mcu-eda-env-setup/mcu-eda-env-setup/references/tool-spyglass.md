# SpyGlass Detection Template

name: spyglass
vendor: Synopsys
role: lint
check_command: which spyglass
version_command: spyglass -version 2>&1 | head -1
module_name: (site-specific, e.g. spyglass/<version> — read from project config modules.spyglass)
binary: spyglass

## Execution Pattern

lint: spyglass -project <prj_path> -batch -goals "lint/lint_rtl"
cdc: spyglass -project <prj_path> -batch -goals "cdc/cdc_verify_struct,cdc/cdc_verify"
script_format: project file (set_option + read_file lines)
execution_mode: sync

## Project File Format

SpyGlass does not support VCS-style `-f filelist`. Must expand filelist into individual `read_file` lines:

```
set_option projectwdir <rpt_dir>
set_option top <top_module>
read_file -type verilog <file1.v>
read_file -type verilog <file2.v>
...
```

## Success Detection

lint_success: 0 fatals in summary (errors from black box analysis are tolerated)
cdc_success: exit code 0

## Report Parsing

Summary line format: "Reported Messages: N Fatals, N Errors, N Warnings"

## Clean

rm -rf spyglass_reports sg_work *.log .spyglass

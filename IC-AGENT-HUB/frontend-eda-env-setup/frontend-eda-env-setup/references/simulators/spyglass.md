# SpyGlass Lint Template

name: spyglass
vendor: Synopsys
check_command: which spyglass
module_name: spyglass/V-2023.12-SP2
role: lint

## Commands

lint_run: spyglass -batch -goal lint/lint_rtl -f flist -l spyglass.log
cdc_run: spyglass -batch -goal cdc/cdc_verify -f flist -l spyglass_cdc.log
rdc_run: spyglass -batch -goal rdc/rdc_verify -f flist -l spyglass_rdc.log

## Flags

top_flag: -top
waiver_flag: -waiver
define_flag: +define+

## Reports

lint_report: spyglass_reports/lint/
cdc_report: spyglass_reports/cdc/
rdc_report: spyglass_reports/rdc/

## Clean

clean: rm -rf spyglass_reports sg_work *.log .spyglass

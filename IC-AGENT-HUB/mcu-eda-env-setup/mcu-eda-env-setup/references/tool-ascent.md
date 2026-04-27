# Ascent Detection Template

name: ascent
vendor: Cadence
role: lint
check_command: which hal
version_command: hal -version 2>&1 | head -1
module_name: (site-specific, e.g. hal/<version> — read from project config modules.ascent)
binary: hal

## Execution Pattern

lint: hal -f <filelist> -top <top_module> -goal lint -log <log_path>
cdc: hal -f <filelist> -top <top_module> -goal cdc -log <log_path>
script_format: command-line with filelist
execution_mode: sync

## Key Differences from SpyGlass

- Cadence tool (formerly HAL)
- Supports VCS-style -f filelist natively
- Different report format
- Better suited for Cadence flow

## Success Detection

lint_success: 0 fatals and 0 errors
cdc_success: exit code 0

## Clean

rm -rf hal_* *.log

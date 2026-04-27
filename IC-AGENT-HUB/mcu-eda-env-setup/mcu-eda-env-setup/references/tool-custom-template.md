# Custom Tool Template

Copy this file to the appropriate role directory and fill in all fields.

name: <tool_name>
vendor: <vendor>
role: <simulator | lint | synthesizer | pnr | equivalence | sta | extraction | physical_ver>
check_command: <which command to detect, e.g. "which vcs">
version_command: <command to extract version string>
module_name: (site-specific — read from project config modules.<tool_name>)
binary: <main executable name>

## Execution Pattern

<list key execution commands, one per line, key: value format>
script_format: <TCL | command file | runset | project file | command-line>
execution_mode: <sync | async>

## Key Inputs

<list required input files/paths>

## Key Outputs

<list output files with path patterns>

## Success Detection

<how to determine if the tool run succeeded>

## Clean

<rm command for generated products>

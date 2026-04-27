# Custom Tool Template

Copy this file to `<tool_name>.md` and fill in all fields.

name: <tool_name>
vendor: <vendor>
check_command: <which command to detect, e.g. "which vcs">
module_name: <module load name, e.g. "vcs/V-2023.12-SP1">
role: <simulator | lint | synthesis | waveform>

## Commands

<list key commands, one per line, key: value format>

## Flags

<list flags used in Makefile generation>

## Reports

<list report paths or commands>

## Clean

clean: <rm command for generated products>

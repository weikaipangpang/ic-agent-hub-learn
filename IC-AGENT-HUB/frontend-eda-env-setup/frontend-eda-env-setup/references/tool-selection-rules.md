# Tool Selection Rules

When multiple tools are available for the same role, use these rules:

## Simulator

- If `input_config.json → sim.simulator` is `auto`, detect available tools and select automatically.
- If a specific simulator is specified, use it if available; otherwise fallback to another available simulator and warn.
- If both VCS and Xcelium are available with `auto` or no preference, prefer VCS.
- If only Questa is available, use Questa. Questa uses a two-step compile flow (vlog + vopt); see `references/simulators/questa.md`.
- If only one simulator is available, use it regardless of config.
- If none is available, stop and report.

## Waveform

- If Verdi is available, prefer Verdi over DVE.
- DVE is acceptable as fallback.

## Lint

- SpyGlass is the only supported lint tool currently.
- If unavailable, skip lint targets in Makefile and report.

## Synthesis

- DC Shell is the only supported synthesis tool currently.
- If unavailable, skip synthesis targets in Makefile and report.
- Synthesis is optional for front-end simulation flow.

## Module Load

- If a tool is not in PATH, scan `module avail` for matching modules and report them.
- Prompt the user to run `module load <module_name>` manually. Do not execute `module load` automatically.
- If the user confirms module is loaded, re-detect and proceed.
- Do not modify `.cshrc`, `.bashrc`, or module files.

---
name: mcu-eda-env-setup
description: Detect available EDA tools, validate PDK and library paths, check LSF availability, and produce a project environment inventory for MCU full-flow (Spec to GDS). Use when setting up a new project, switching tools, or when any stage skill reports missing tool or path errors.
license: PolyForm-Noncommercial-1.0.0
metadata:
  author: 中科麒芯
  organization: 中科麒芯智能技术（南京）有限公司
  homepage: https://www.ickylin.com/
  contact: info@ickylin.com
---

# MCU EDA Env Setup

Use this skill to establish or verify the EDA execution environment before any stage skill runs tools.

## Environment Assumptions

This skill assumes a Linux/Unix EDA server environment: `which` command available, POSIX shell, `module` system optional (for HPC clusters), and standard EDA tool installation paths. It is not designed for Windows or macOS hosts.

## Boundaries

- Do **not** generate stage-specific TCL scripts, runsets, or Makefiles. Each stage skill owns its own execution templates.
- Do **not** execute EDA tools (compile, synthesize, etc.). Only detect and validate.
- Do **not** modify project source files (RTL, testbench).
- Do **not** modify system environment (shell rc files, module configs).
- Do **not** install EDA tools. Only detect and validate existing environment.

The skill probes the customer's existing environment automatically, confirms findings with the user, and writes `eda_env.json` for downstream stage skills to read.

## Good Outcome

Produce:

- detected EDA tool inventory across all 8 roles (simulator, lint, synthesizer, pnr, equivalence, sta, extraction, physical_ver)
- selected tool set based on detection results and user confirmation
- PDK and library path validation results
- LSF availability and resource profile
- a written `eda_env.json` in the project directory that downstream skills can read
- clear warnings for anything missing or degraded

## Output Artifacts

| Artifact | Path | Description |
|----------|------|-------------|
| `eda_env.json` | Project root or docs dir | Full environment inventory. Schema: [output_schema.json](assets/output_schema.json) |

## Stage Entry Criteria

Use this skill when any of the following is true:

- starting a new project and need to know what tools are available
- a stage skill reported a missing tool or path error
- switching from one tool vendor to another
- verifying environment after system maintenance or module updates
- first time using these skills on an existing project

## Input Validation

This is Stage 0 — no upstream skill outputs are required. Instead, validate the system environment:

| Check | What to verify | Used for |
|---|---|---|
| Shell `which` command | Available and functional | Tool binary detection |
| `module` command | Available (optional, some sites don't use it) | Module-based tool loading |
| File system access | Can read /usr, /opt, /eda or wherever tools are installed | Tool path verification |
| `config/project.json` (if exists) | Valid JSON, readable | Reading user's tool/library preferences |

If `config/project.json` exists, validate these fields when present:

| Field | What to check | Used for |
|---|---|---|
| `tools.<role>.name` | String or "auto" | Tool preference per role |
| `modules.<tool_name>` | String (module load name) | Module load for tools not in PATH |
| `env.env_init_script` | Path exists and is readable (if set) | Environment initialization |
| `libraries.std_cell` | Has at least one corner key (ss/ff/tt) | Library path validation |
| `pdk` | Has at least one path field | PDK path validation |

If `config/project.json` does not exist, proceed with pure environment probing — do not fail.

## Workflow

### Step 1: Probe EDA tools

Detect what is already available in the customer's environment. Do NOT ask the user to fill in a config file first.

**1a. Check PATH directly**

For each known tool binary, run `which <binary>`. These binary names are industry-standard:

| Role | Binaries to check |
|------|-------------------|
| simulator | `vcs`, `xrun` (Xcelium), `irun`, `vsim` (Questa) |
| waveform | `verdi`, `simvision`, `dve` |
| lint | `spyglass`, `hal` (Ascent) |
| synthesizer | `dc_shell`, `genus` |
| pnr | `innovus`, `icc2_shell` |
| equivalence | `fm_shell` (Formality), `lec` (Conformal) |
| sta | `pt_shell` (PrimeTime), `tempus` |
| extraction | `StarXtract` (StarRC), `qrc` |
| physical_ver | `calibre`, `icv_comp`, `pegasus` |

For each tool found in PATH, consult the corresponding `references/tool-{tool_name}.md` file for the canonical version_command, execution pattern, and flags. The bundled `scripts/detect_eda_env.py` hardcodes tool-standard version commands for automation speed; the `tool-*.md` files serve as reference documentation and as the authoritative source when the script's hardcoded values need updating. If no reference file exists for a detected tool, note it as "no template available" and ask the user for version command.

**1b. Check module system**

If `module` command is available:

```
module avail 2>&1
```

Parse the output to find available EDA modules. Common module name patterns:
- Synopsys: `vcs/`, `syn/`, `pts/`, `starrc/`, `spyglass/`, `verdi/`, `icv/`, `icc2/`
- Cadence: `xcelium/`, `genus/`, `innovus/`, `tempus/`, `conformal/`, `pegasus/`
- Siemens: `calibre/`

If a tool was not in PATH but a module exists, note it as "available via module load" and record the module name.

**1c. Check environment variables**

Read known EDA environment variables that many sites set:

```
$SYNOPSYS          — Synopsys tool root
$CDS_INST_DIR      — Cadence tool root
$MGC_HOME          — Siemens/Mentor tool root
$VCS_HOME          — VCS install path
$VERDI_HOME        — Verdi install path
$DC_HOME           — Design Compiler install path
$INNOVUS_HOME      — Innovus install path
$PT_HOME           — PrimeTime install path
```

These help locate tools even if not yet in PATH.

**1d. Check existing project setup files**

If the project already has tool configuration files, read them to learn the environment:

- `.synopsys_dc.setup` — may contain `search_path`, `target_library`, `link_library`
- `cds.lib`, `.cdsinit` — Cadence library definitions
- `Makefile` or `*.mk` in sim/ or project root — may reveal tool commands and flags
- `*.f` (filelist) — reveals RTL structure
- `scripts/*.tcl` — may contain library paths and tool settings
- `sdc/*.sdc` — timing constraints with clock definitions

Extract any useful information (library paths, tool preferences, design parameters) from these files.

### Step 2: Probe PDK and libraries

**2a. Check PDK environment variables**

```
$PDK_HOME, $PDK_DIR, $TECH_DIR     — PDK root
$STD_CELL_DIR, $STDLIB              — standard cell library root
$MEM_IP_DIR, $SRAM_DIR              — memory macro root
```

**2b. Scan from discovered paths**

If synthesis setup files (`.synopsys_dc.setup`) or existing TCL scripts contain library paths, follow those paths to discover:

- Standard cell .db/.lib files and their corner structure (ss/ff/tt)
- Standard cell .lef files
- SRAM macro .db/.lib/.lef/.gds files
- Technology file (.tf)
- TLU+ files
- DRC/LVS rule decks
- StarRC/QRC technology files

**2c. Infer corner structure**

IC libraries follow naming conventions. From discovered .db/.lib files, infer:
- Which corners exist (ss, ff, tt)
- Which VT variants exist (rvt, hvt, lvt)
- Temperature and voltage conditions

### Step 3: Check LSF availability

1. Run `which bsub`
2. If found, LSF is available locally
3. If not found, check if user mentions a cluster or gateway
4. Record: available/unavailable, mode (local/ssh/none)

### Step 4: Present findings and confirm

Show the user what was detected. Structure the output as:

```
EDA Tools Detected:
  simulator:    vcs (path, version)
  lint:         spyglass (path, version)
  synthesizer:  dc_shell (path, version)
  ...

PDK/Libraries Found:
  PDK root:     /path/to/pdk
  Std cells:    /path/to/stdcells (ss/ff/tt corners found)
  SRAM macros:  /path/to/sram (2 macros found)
  Tech file:    /path/to/tech.tf
  TLU+:         max: /path/..., min: /path/...
  DRC rules:    /path/to/drc.rul
  LVS rules:    /path/to/lvs.rul

LSF:            available (local)

Missing or undetected:
  - extraction tool: StarRC/QRC not found (needed for signoff)
  - TLU+ min: not found (needed for hold analysis)
```

Ask the user to confirm or correct. If critical items are missing, ask the user to provide paths or module names.

### Step 5: Select tools

For each role, select based on:
1. If only one tool is available, use it
2. If multiple are available, apply [tool-selection-rules.md](references/tool-selection-rules.md)
3. If user has a preference (stated or inferred from existing scripts), respect it

### Step 6: Write eda_env.json

Write the confirmed inventory to `eda_env.json` using the schema in [output_schema.json](assets/output_schema.json).

Include:
- All detected tools with paths, versions, module names
- Selected tool per role
- PDK and library paths (validated)
- LSF status
- Environment init info (if a setup script was discovered)

### Step 7: Report and recommend

Summarize:
1. Ready tool set
2. Any gaps that will block specific stages
3. Recommended next step (which stage skill to use)

## Bundled References

- [tool-selection-rules.md](references/tool-selection-rules.md) — priority and fallback logic per role
- [pdk-library-validation.md](references/pdk-library-validation.md) — what paths to check and why
- [lsf-profile.md](references/lsf-profile.md) — per-tool resource profiles and submission rules
- Tool detection templates: `references/tool-*.md` — per-tool binary names, version commands, execution patterns
- [tools_registry.json](references/tools_registry.json) — structured JSON registry of all tools with version_cmd, version_regex, smoke_cmd
- [tool-custom-template.md](references/tool-custom-template.md) — template for documenting additional tools
- [detect_eda_env.py](scripts/detect_eda_env.py) — automated detection script
- [output_schema.json](assets/output_schema.json) — eda_env.json schema
- [project_config_template.json](assets/project_config_template.json) — reference config structure (for understanding, not mandatory input)

## Completion Gate

This stage is complete when:

- all 8 tool roles have been checked
- a tool is selected for each role needed by the project flow
- PDK and library paths are discovered and validated
- LSF availability is determined
- `eda_env.json` is written
- the user has confirmed the findings or provided corrections
- any blockers are reported with actionable guidance

## Reusable Outputs

- Tool inventory (name, path, version, role, vendor, module)
- Selected tool set per role
- PDK and library path inventory
- LSF profile
- `eda_env.json`

## Decision Rules

- Probe first, ask second. Never start by asking the user to fill a config file.
- If the environment already has tools in PATH, don't ask about modules — just use what's there.
- If existing project files (Makefile, TCL scripts, setup files) reveal tool choices, respect them as defaults.
- If both Synopsys and Cadence tools are available for a role and no preference is evident, use the priority in tool-selection-rules.md.
- Never modify `.cshrc`, `.bashrc`, `.synopsys_dc.setup`, or module configuration files.
- Never install EDA tools. Only detect and validate existing environment.
- PDK path validation failures for backend tools (pnr, sta, extraction, physical_ver) are blockers. For frontend-only flows (sim + lint), they are warnings.
- If a tool or path cannot be detected, ask the user once with a clear question. Do not ask repeatedly.

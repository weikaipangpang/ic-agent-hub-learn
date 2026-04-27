# LSF Profile and Job Submission

## Detection

1. Check `which bsub` — if found, LSF is available locally.
2. If not found, check `config/project.json → lsf.ssh_gateway`. If set, test SSH connectivity.
3. Record: `lsf_available` (true/false), `lsf_mode` (local/ssh/none).

## Per-Tool Resource Profiles

| Tool | Cores | Memory | Typical Runtime | Execution Mode |
|------|-------|--------|----------------|----------------|
| DC Shell | 8 | 50 GB | 5-15 min | async |
| Genus | 8 | 50 GB | 5-15 min | async |
| Innovus (floorplan) | 8 | 32 GB | 3-10 min | async |
| Innovus (P&R) | 8 | 32 GB | 10-30 min | async |
| StarRC | 4 | 16 GB | 3-10 min | async |
| PrimeTime | 4 | 16 GB | 2-5 min | sync |
| Calibre DRC | 4 | 16 GB | 2-5 min | sync |
| Calibre LVS | 4 | 16 GB | 2-5 min | sync |
| Formality | 4 | 16 GB | 2-5 min | sync |
| VCS compile | 2 | 8 GB | 1-3 min | sync |
| VCS simulate | 2 | 8 GB | 1-5 min | sync |
| SpyGlass | 2 | 8 GB | 1-3 min | sync |

## Execution Mode Rules

- **sync**: Tool finishes quickly (< 5 min). Block and wait for result.
- **async**: Tool runs long (> 5 min). Submit to LSF queue, return job ID, poll for completion.

If LSF is unavailable, all tools run locally. Async tools run as background processes.

## Runtime Anomaly Detection

If a job runs longer than 3x its typical runtime estimate, flag it as anomalous. Do not kill — just warn. The user decides whether to continue or abort.

## Queue Configuration

Default queue from `config/project.json → lsf.queue`. If not set, use `normal`.

## Command Wrapping

All EDA commands are wrapped with the site's environment setup:

```
<env_init_script> && module load <tool_modules> && <actual_command>
```

- `env_init_script` comes from `config/project.json → env.env_init_script`. If empty, skip the source step.
- `tool_modules` come from `config/project.json → modules.<tool_name>`. If empty, assume tool is already in PATH.

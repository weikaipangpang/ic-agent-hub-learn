# Backup Policy (EDA Env Setup)

## When to Backup

| Scenario | Action |
|----------|--------|
| First run, no sim/Makefile | No backup needed |
| Re-run, same simulator | Skip regeneration, keep existing |
| Re-run, different simulator | Backup sim/ then clean then regenerate |
| User explicitly requests regeneration | Backup then regenerate |

## What to Backup

```
sim/backup/<timestamp>/
  Makefile
  *.log
  coverage_txt/     (if exists)
  coverage reports   (if exist)
```

## What NOT to Backup

- simv, csrc, simv.daidir (too large, recompilable)
- xcelium.d (too large, recompilable)
- waveform dumps (too large)

## Rules

- Never delete backup directories.
- Backup directory uses timestamp format: `YYYY-MM-DD_HH-MM-SS`.
- If backup fails, stop and report. Do not overwrite without successful backup.

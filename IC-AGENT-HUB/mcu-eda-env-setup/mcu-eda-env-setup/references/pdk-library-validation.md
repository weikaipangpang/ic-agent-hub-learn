# PDK and Library Path Validation

## What to Validate

### Standard Cell Libraries

Per corner (ss, ff, tt):

| File Type | Used By | Required When |
|-----------|---------|---------------|
| `.db` (Liberty binary) | DC synthesis, Formality, PrimeTime | synthesizer or sta selected |
| `.lib` (Liberty text) | Innovus (MMMC timing) | pnr selected |
| `.lef` (cell abstract) | Innovus (physical) | pnr selected |
| `.gds` (cell layout) | Innovus GDS merge, Calibre LVS | physical_ver selected or GDS export |

Typical VT variants: RVT, HVT, LVT, and clock-gating variants (CG_RVT, CG_HVT).

### SRAM Macro Libraries

| File Type | Used By | Required When |
|-----------|---------|---------------|
| `.db` or `.lib` | DC, Formality, PrimeTime | design contains SRAM |
| `.lef` | Innovus | pnr selected |
| `.gds` | GDS merge, Calibre | physical_ver selected |

### PDK Physical Files

| File | Used By | Required When |
|------|---------|---------------|
| Technology file (`.tf`) | Innovus | pnr selected |
| TLU+ max (worst RC) | Innovus, PrimeTime | pnr or sta selected |
| TLU+ min (best RC) | Innovus, PrimeTime | pnr or sta selected |
| StarRC nxtgrd per corner | StarRC | extraction selected |
| StarRC ITF file | StarRC | extraction selected |
| Calibre DRC rule deck | Calibre | physical_ver = calibre |
| Calibre LVS rule deck | Calibre | physical_ver = calibre |
| ICV DRC/LVS rules | ICV | physical_ver = icv |
| Layer map file | Innovus GDS export | GDS export needed |

## Validation Logic

```
For each path in project.json:
  1. Resolve to absolute path
  2. Check file/directory exists
  3. Check readable
  4. Classify:
     - PASS: exists and readable
     - WARN: missing but only needed for stages not in current flow
     - FAIL: missing and required for a stage that has a selected tool
```

## Common Issues

- Library corners mislabeled (ss dir contains ff files)
- SRAM .db missing but .lib exists (use .lib as fallback for some tools)
- TLU+ files swapped (max used for min corner)
- Calibre rule deck path points to directory instead of file
- GDS files too large to validate content (only check existence)

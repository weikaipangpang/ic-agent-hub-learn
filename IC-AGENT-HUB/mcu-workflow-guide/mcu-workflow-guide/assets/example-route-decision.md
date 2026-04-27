## Current stage guess

`mcu-verification-triage`

## Why this stage fits

The user already has a failing compile log and a partial sim log. That is stronger evidence for a verification-entry problem than for architecture planning or synthesis review.

## Recommended skill

`mcu-verification-triage`

## Fallback skill if needed

`mcu-rtl-development`

## Missing inputs

- full compile command or normalized filelist
- top-level module name if the compile log is truncated
- whether the failure happens before or after the CPU wrapper is instantiated

## Recommended next step

Classify the compile failure first. If the issue turns out to be interface-contract drift rather than a raw syntax or missing-module problem, step back to `mcu-rtl-development`.

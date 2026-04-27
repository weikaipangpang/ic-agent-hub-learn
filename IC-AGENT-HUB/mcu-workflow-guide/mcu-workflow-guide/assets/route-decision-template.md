# Route Decision

## Current stage guess

State the stage number and skill name that best matches the user's current situation. Use the stage-selection-map.md to determine the match.

## Why this stage fits

Explain in 1-3 sentences what evidence led to this choice. Reference specific artifacts the user has (e.g., "user has a failing compile.log" or "user has product intent but no spec.md").

## Recommended skill

The primary skill to route to. Must be one of the 13 execution skills defined in the flow.

## Fallback skill if needed

An alternative skill if the primary turns out to be wrong after initial investigation. For example, if triage reveals an upstream spec issue, the fallback might be `mcu-spec-architecture-planning`.

## Missing inputs

List any artifacts or information that the recommended skill needs but are not yet available. For each missing item, state:
- What is missing
- Where it would normally come from
- Whether the user can provide it directly or whether an upstream stage must run first

## Recommended next step

One concrete, actionable instruction. Not "run the skill" but a specific first action like "read compile.log to classify the failure" or "check whether spec.md has a memory map section."

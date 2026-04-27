# Frontend Workflow Route Decision

## Current Stage Guess

State the stage number and skill name that best matches the user's current situation. Use the stage-selection-map.md to determine the match.

## Why This Stage Fits

Explain in 1-3 sentences what evidence led to this choice. Reference specific artifacts the user has (e.g., "user has extracted register views but no review" or "user has compile.log with errors").

## Primary Recommended Skill

The primary skill to route to. Must be one of the 11 stage skills defined in the pipeline.

## Fallback Skill If Needed

An alternative skill if the primary turns out to be wrong after initial investigation. For example, if spec review reveals missing extraction, the fallback is `frontend-spec-extraction`.

## Missing Facts Or Blockers

List any artifacts or information that the recommended skill needs but are not yet available. For each:
- What is missing
- Which upstream stage produces it
- Whether the user can provide it directly

## Continue / Pause / Step Back

State the recommended action:
- **Continue**: prerequisites met, proceed with the recommended skill
- **Pause**: one prerequisite is marginal, needs user confirmation
- **Step back**: a prerequisite is missing or contradictory, roll back to the upstream stage

## Rollback Signals

List any evidence that suggests the real problem is upstream, not at the current stage. Reference specific rollback patterns from rollback-signal-patterns.md.

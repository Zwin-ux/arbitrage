# Strategy Contributor Guide

Superior separates strategy discovery from execution on purpose.

## Expected boundaries

- `VenueAdapter`: pulls venue-specific market state into normalized quotes
- `ContractMatcher`: decides whether contracts are exact, probable, or rejected
- `OpportunityEngine`: turns quotes into explainable candidates with net-edge breakdowns
- `PaperExecutionEngine`: simulates deterministic paper runs
- `LiveExecutionEngine`: remains a separate, explicit path
- `BotConfigService`: owns starter bot blueprints, slot previews, and safe default bot configs
- `BotRecipeStore`: persists local forked bot recipes as plain JSON beside the profile data
- `PaperSimulationEngine`: stages scanner candidates into multi-bot paper sessions
- `DecisionTraceFormatter`: turns paper-bot decisions into a tactical trace that the desktop UI and QA client can inspect

## Contributor rules

- Use official venue APIs and clients only
- Prefer rejecting uncertain matches over stretching equivalence
- Keep live decision logic deterministic
- Add tests for reject reasons, edge decomposition, and risk interactions
- Keep Lab strategies out of guided beginner flows unless explicitly enabled
- Starter bots should explain themselves in plain English: family, gate, route choice, stake, and result
- Recipes stay intentionally small:
  - strategy family
  - min net edge
  - target stake
  - max assignments
  - route preference
  - source metadata for starter vs local fork
- Local forks are the safe way to customize a starter bot in v1. Do not add scripting or opaque ranking logic.
- Every paper decision path should leave enough trace data for a user to answer:
  - what route was considered
  - why it passed or failed the gate
  - what net edge survived costs
  - how the paper result changed score

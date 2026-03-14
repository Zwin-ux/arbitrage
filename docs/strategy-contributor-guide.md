# Strategy Contributor Guide

Superior separates strategy discovery from execution on purpose.

## Expected boundaries

- `VenueAdapter`: pulls venue-specific market state into normalized quotes
- `ContractMatcher`: decides whether contracts are exact, probable, or rejected
- `OpportunityEngine`: turns quotes into explainable candidates with net-edge breakdowns
- `PaperExecutionEngine`: simulates deterministic paper runs
- `LiveExecutionEngine`: remains a separate, explicit path

## Contributor rules

- Use official venue APIs and clients only
- Prefer rejecting uncertain matches over stretching equivalence
- Keep live decision logic deterministic
- Add tests for reject reasons, edge decomposition, and risk interactions
- Keep Lab strategies out of guided beginner flows unless explicitly enabled

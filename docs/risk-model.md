# Risk Model

Superior is designed to be stable software, not a promise of stable profits.

## Core principles

- Paper mode is the default.
- Live mode stays locked until a checklist passes.
- Risk policies cap position size, open positions, and daily loss.
- The coach can explain and summarize, but it cannot place or tune trades.
- Experimental strategies live in the Lab and stay paper-only in v1.

## What the scanner does

- Looks for explainable pricing dislocations in recorded market data
- Converts gross edge into net edge with deterministic cost adjustments
- Rejects imperfect or under-specified candidates instead of forcing action

## What the scanner does not do

- Guarantee fills, profits, or durable edge
- Infer undocumented venue behavior
- Ignore stale books, bad credentials, or diagnostics issues

## User expectation

The intended user experience is:

1. Learn the venue
2. Record local books
3. Inspect explainable scanner output
4. Run paper bots
5. Decide whether live unlock is earned

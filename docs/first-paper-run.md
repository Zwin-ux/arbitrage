# First Paper Run

This is the fastest clean path through Superior v1.

## Goal

Install the app, equip Polymarket, record a local sample, inspect one scanner signal, run one paper route, and see the score update.

## 1. Open the guided setup

- Create a new profile
- Keep `Guided` mode on
- Pick the default `learn and scan` or `paper arbitrage` goal
- Leave `Lab` off

## 2. Equip only what you need

- Keep `Polymarket` equipped
- Leave `Kalshi` off unless you explicitly want cross-venue research
- Leave credentials blank if you only want recorder plus paper mode

Recorder, scanner, and paper score do not require secrets.

## 3. Keep the first launch conservative

- Use the default recorder preset
- Keep the starter risk policy
- Leave live unlock acknowledgements alone for now

The app should show a safe state similar to:

- `Paper mode active`
- `Live gate locked`
- `Lab off`

## 4. Record local market data

From `Hangar`, start the recorder and wait for message and book counts to appear.

You want:

- raw messages greater than zero
- book snapshots greater than zero
- no obvious warnings in the hangar state

## 5. Scan one route

Open `Scanner` and refresh the scan.

Read one candidate in plain language:

- what matched
- why it passed or failed
- what deductions reduced gross edge to net edge

If no candidate appears, keep the first recording short and healthy rather than forcing a trade idea.

## 6. Run one paper route

Use `Paper selected` or `Paper top route`.

That should create:

- one paper run record
- one score update
- one ledger entry sequence in `Score`

## 7. Check the score board

`Score` should reflect:

- realized paper PnL
- completed runs
- expected edge versus realized edge
- recent ledger entries

If the score board is still empty, verify that the paper run completed instead of only opening the scanner.

## 8. Stop there

That is a successful first run.

Do not treat the live gate as the next default step. Superior v1 is paper-first, and the point of the first run is to prove the loop works with local evidence before you add more risk.

If you want the next step later, the safest one is `shadow` mode in `Live Gate`, not broad live trading.

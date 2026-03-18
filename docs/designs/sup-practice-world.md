# SUP Practice World

## Product line
Superior is a persistent fake-money prediction market where players run simple bots, grow a bankroll on replay tapes, and only graduate toward real money after the engine proves itself.

## What changes
- The product stops feeling like isolated demo runs.
- Every run feeds a persistent bankroll.
- Starter bots become benchmarks, not just labels.
- Replay tapes become a world map of lessons and pressure tests.
- Live stays locked and remains a graduation path.

## Core loop
1. Open the app.
2. Pick a tape.
3. Start with the current bankroll.
4. Hold to buy.
5. See the result.
6. Compare against Safe / Balanced / Aggressive.
7. Run again.

## First shipping world slice
- Persistent bankroll starting at `$100`
- Fixed stake cap of `$25`, reduced automatically when bankroll is lower
- Best bankroll
- Clear streak
- Tutorial and replay clears tracked separately
- Post-run bot comparison on the same tape
- Live gate still locked behind tutorial clears, replay clears, and consistency

## What makes it useful
- The user is always building or losing something visible.
- Every tape teaches timing and restraint through money movement, not theory.
- Bot comparison shows whether the user actually beat the house presets.
- The app stays local, deterministic, and safe.

## Not in this slice
- Shared multiplayer world state
- Chat, profiles, clans, or social systems
- Real-money execution
- Open strategy builder
- Cloud sync

## Immediate roadmap
1. Persistent bankroll and streaks
2. Bot comparison after every run
3. More tapes grouped into packs
4. Better pack progression and daily challenge
5. Only then consider social or live-facing layers

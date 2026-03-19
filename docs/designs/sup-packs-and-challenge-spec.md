# SUP Packs And Challenge Spec

## Decision
The next best move is `chapterized tape packs` with `daily challenge` built on the same content spine.

This is the highest-leverage step because the core loop already works:
- start with fake money
- time a buy
- see the bankroll move
- compare against presets

What is missing now is a reason to come back.

Do not add more engine ideas first.
Do not add live execution.
Do not add social systems yet.

Build a progression layer around the loop that already exists.

## Why this is next
Current state:
- the product is understandable
- the loop is deterministic
- the visuals are finally coherent
- bankroll persists
- preset comparison works

Current gap:
- there is no strong medium-term structure
- tape choice is flat
- replay has no campaign shape
- there is no daily reason to return

The product needs:
1. a path
2. a sense of clearing something
3. a repeatable reason to come back tomorrow

## Product move
Turn replay into a small practice world:

1. `Tutorial Packs`
- simple lesson packs
- teach timing and restraint
- guaranteed readable outcomes

2. `Replay Packs`
- more volatile tapes
- same fake-money rules
- more punishing timing

3. `Daily Challenge`
- one highlighted tape per day
- fixed rules
- compares your result against house presets
- no live money, no randomness

The result should feel like:
- start the app
- pick the next tape in a pack
- clear it
- unlock the next pack
- come back tomorrow for the daily challenge

## Scope decision
Ship in this order:

### Shipping slice A
- pack metadata
- pack selection
- pack unlock rules
- pack completion state
- better tape naming and grouping
- one daily challenge slot using bundled tapes

### Shipping slice B
- daily challenge history
- streaks for daily challenge
- best daily finish vs house presets

### Not in scope
- real multiplayer
- real-time shared economy
- cloud sync
- user-generated packs
- live execution
- chat or clan systems

## UX doctrine
Keep the current shell.
Do not add dashboards.
Do not add map clutter.

Add only:
- one pack rail
- one pack progress line
- one small challenge marker

Hierarchy:
1. current tape
2. current bankroll
3. current result
4. pack progress
5. challenge state

Visual rules:
- pack chips look like the existing mode and preset buttons
- active pack is gold
- locked pack is dim
- cleared pack gets a simple mark, not a badge explosion
- daily challenge is one blue-accent chip, not a new screen style

## User flow

```text
BOOT
  -> SELECT MODE
    -> SELECT PACK
      -> SELECT TAPE
        -> RUN
          -> RESULT
            -> COMPARE AGAINST HOUSE PRESETS
              -> CLEAR TAPE?
                -> YES: update pack progress
                -> NO: keep same pack/tape active
                  -> NEXT RUN
```

Daily challenge:

```text
BOOT
  -> DAILY CHALLENGE AVAILABLE
    -> PLAY TODAY'S TAPE
      -> RESULT
        -> YOU vs SAFE/BALANCED/AGGRESSIVE
          -> SAVE TODAY'S RESULT
```

## Minimal architecture
Do not add a new engine.
Extend the current content and progress layers.

### Extend existing modules
- `desktop-v1/src/domain/types.ts`
- `desktop-v1/src/services/datasetLoader.ts`
- `desktop-v1/src/services/progressService.ts`
- `desktop-v1/src/services/persistenceService.ts`
- `desktop-v1/src/app/useRehearsalMachine.ts`
- `desktop-v1/src/screens/ModeSelectScreen.tsx`
- `desktop-v1/src/screens/RunScreen.tsx`

### Add at most two new modules
- `desktop-v1/src/services/packManifest.ts`
- `desktop-v1/src/services/dailyChallenge.ts`

This keeps the diff small and avoids another abstraction wave.

## Data model additions

### New types
```ts
export interface TapePack {
  id: string;
  mode: "tutorial" | "replay";
  name: string;
  order: number;
  label: string;
  tapeIds: string[];
  unlock: {
    type: "free" | "requires_pack_clear" | "requires_tape_clear";
    targetId?: string;
  };
}

export interface PackProgress {
  packId: string;
  clearedTapeIds: string[];
  completed: boolean;
  bestNetPnl: number;
}

export interface DailyChallengeEntry {
  challengeId: string;
  tapeId: string;
  date: string;
  completed: boolean;
  netPnl: number | null;
  grade: "clear" | "early" | "late" | "miss" | "blocked" | null;
}
```

### Extend `ProgressSnapshot`
```ts
packProgress: PackProgress[];
lastSelectedPackId: string | null;
dailyChallengeHistory: DailyChallengeEntry[];
currentDailyChallengeId: string | null;
```

## Tape organization
Current tapes should no longer be treated as a flat list.

Initial content target:

### Tutorial packs
- `PACK 01 / OPEN`
  - `INTRO ROUTE`
  - `STEADY WINDOW`
- `PACK 02 / TIMING`
  - `EARLY SHAKE`
  - `LATE COLLAPSE`

### Replay packs
- `PACK 03 / VOLATILE`
  - `OPENING WINDOW`
  - `THIN REVERSAL`
- `PACK 04 / PRESSURE`
  - `DOUBLE FAKE`
  - `FAST EXIT`

This means the next content pass should add at least four new tapes, not one.

## Daily challenge
Do not build a server dependency.

Use a deterministic local selection function:
- seed = local date in `YYYY-MM-DD`
- source pool = unlocked replay tapes
- fallback = first replay pack if pool is empty

Challenge ID format:
- `daily-2026-03-18`

Rules:
- one tape per day
- one visible highlighted slot
- same fake-money rules
- same preset comparison
- saves one result per day in local progress

## Unlock rules
Keep them simple:

### Pack unlock
- first tutorial pack: free
- next tutorial pack: unlock after prior pack cleared
- first replay pack: unlock after all tutorial packs cleared
- next replay pack: unlock after prior replay pack cleared

### Pack clear
A pack is cleared when every tape in the pack has one successful run.

### Live gate
Do not change the live gate yet except to let pack clears count toward existing replay/tutorial totals.

## UI changes

### Mode select
Keep the current mode row.
When tutorial or replay is active, show a second slim pack row beneath it.

### Run surface
Add:
- `PACK` label in the header rail
- pack progress text like `01 / 02 CLEARED`
- if daily challenge is active, show `TODAY` as a small accent marker

Do not add:
- charts
- world maps
- side panels
- achievement grids

### Result state
Add one extra compact line:
- `PACK CLEAR`
- `NEXT PACK OPEN`
- `TODAY SAVED`

Short only.

## State flow changes

```text
MODE
  -> PACK
    -> TAPE
      -> RUN
        -> RESULT
          -> UPDATE PACK PROGRESS
            -> MAY UNLOCK NEXT PACK
              -> READY
```

## Engineering notes

### `datasetLoader.ts`
Extend it to support:
- `listPacks(mode)`
- `getPackById(packId)`
- `listTapesForPack(packId)`

Avoid a second manifest system.
Tape manifest and pack manifest should stay close together.

### `progressService.ts`
Extend `recordRun()` so it:
- updates tape clears inside the active pack
- marks pack complete when all tapes are cleared
- updates best pack P/L
- updates daily challenge entry if the current tape is the daily challenge

### `persistenceService.ts`
Bump the versioned envelope.
Add migration for:
- missing `packProgress`
- missing `dailyChallengeHistory`
- missing `lastSelectedPackId`

### `useRehearsalMachine.ts`
Add:
- selected pack state
- selected daily challenge state
- derived tape list from active pack
- pack progression update after each run

Do not split this hook yet unless the pack logic becomes unreadable.

## Test plan

### Unit
- pack unlocks from prior pack clear
- replay packs stay locked before tutorial clear
- daily challenge picks the same tape for the same day
- persistence migration from pre-pack progress blobs
- pack clear only counts successful runs
- replaying the same cleared tape does not duplicate progress

### Integration
- selecting a mode updates pack rail
- selecting a pack updates available tapes
- clearing final tape unlocks the next pack
- daily challenge saves one result per day
- reload preserves pack selection and progress

### Visual / browser
- pack rail renders on site/app without wrapping badly
- locked packs are visibly subordinate
- daily challenge marker appears only once
- result state still remains the dominant element

## Milestones

### M1 — Pack manifest
- add `TapePack` type
- add pack manifest
- add pack-aware loader functions

Acceptance:
- tutorial and replay tapes resolve through packs
- flat tape lists still work through the new loader layer

### M2 — Progress model
- extend progress snapshot
- migrate persistence
- record pack clears and completion

Acceptance:
- older local progress loads safely
- new progress survives reload

### M3 — UI integration
- add pack rail
- add pack progress line
- wire selected pack into tape selection

Acceptance:
- user can move mode -> pack -> tape without dead ends
- locked packs cannot be entered

### M4 — Daily challenge
- deterministic daily challenge selection
- challenge marker in UI
- local history write

Acceptance:
- same day gives same challenge
- challenge result is stored once

### M5 — Content pass
- add at least four new tapes
- assign all tapes to packs
- tune names for readability

Acceptance:
- app has enough content for a real session arc

## Codex execution order
Use this order exactly:

1. `types.ts`
2. `datasetLoader.ts` + `packManifest.ts`
3. `progressService.ts`
4. `persistenceService.ts`
5. tests for pack logic and migration
6. `useRehearsalMachine.ts`
7. `ModeSelectScreen.tsx`
8. `RunScreen.tsx`
9. add new tapes
10. browser and Tauri validation

## Codex constraints
- no new dependency
- no cloud requirement
- no new engine
- no dashboard screens
- no social features in this pass
- keep visuals inside the current shell

## Recommendation
Implement `Tape Packs + Pack Progression` first.

Build `Daily Challenge` on the same data model in the same pass if the lake is still small.
Do not start “MMO” features before this structure exists.

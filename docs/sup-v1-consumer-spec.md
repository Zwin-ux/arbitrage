# SUP v1 Consumer Spec

## 1. Locked Product Summary
- Product: a rehearsal machine for timing, restraint, and commitment before real action.
- Primary loop: `Standby -> Arm -> Run -> Pressure -> Commit Hold -> Resolution -> Afterimage -> Reset`.
- v1 modes: `Tutorial`, `Replay`, `Live Books`.
- v1 doctrine: Tutorial and Replay are the real product; Live Books is locked and secondary.
- Visual doctrine: restrained 16-bit control panel, not a dashboard, not terminal cosplay, not cyberpunk.
- Data doctrine: bundled local replay tapes, deterministic playback, no credentials required for first run.

## 2. Final Screen List
1. Entry / Mode Select
   - Three choices only: Tutorial, Replay, Live Books (locked)
   - No scrolling, no paragraphs, no analytics framing
2. Tutorial Mode
   - Curated tapes
   - Slower opportunity windows
   - Clear route math and commit timing
3. Replay Mode
   - Deterministic tape playback
   - Start, Step, Hold to Commit, Reset
   - Same lane, same rules, different tapes
4. Run Debrief
   - Inline after resolution
   - Max 2-4 short lines
5. Live Books (Locked)
   - Visible, read-only, subordinate
   - Explains what remains required

## 3. Engine / Services
- Tape Engine: bundled tapes, cursor, playback, step, pause, reset
- Run Engine: run phase transitions and hold-to-commit timing
- Route Evaluator: gross, deductions, net, quality, pass/fail reason
- Bot Engine: Safe / Balanced / Aggressive presets on the same tape
- Progress / Gating Service: successful runs, consistency score, Live Books unlock state
- Dataset Loader: bundled tape metadata and payloads
- Persistence Service: last selected mode, replay history, and local progress

## 4. Data Models
- `Tape`
- `TapeEvent`
- `RunRecord`
- `Debrief`
- `BotPreset`
- `LiveGate`
- `ProgressSnapshot`

See `/desktop-v1/src/domain/types.ts` for exact TypeScript interfaces.

## 5. Tape Format
- Format: JSON
- Requirements:
  - deterministic
  - inspectable
  - bundle-friendly
  - supports tutorial and replay
- Top-level:
  - tape metadata
  - lane defaults
  - ordered event list
  - optional authored route windows
- Event payload:
  - `t`
  - `value`
  - `volume`
  - `eventType`
  - `severity`
  - optional `window`
  - optional `routeSnapshot`

See `/desktop-v1/src/tapes/tutorial/intro-route.json` for the first concrete tape schema.

## 6. Folder / File Architecture
- `/desktop-v1/package.json`
- `/desktop-v1/tsconfig.json`
- `/desktop-v1/src/app`
- `/desktop-v1/src/domain`
- `/desktop-v1/src/services`
- `/desktop-v1/src/presets`
- `/desktop-v1/src/screens`
- `/desktop-v1/src/ui`
- `/desktop-v1/src/tapes`
- `/desktop-v1/src/ingest`

## 7. Exact v1 Milestone Tickets

### Phase 1 — Core Loop
1. `SUP-101 Implement run phase state machine`
   - Purpose: define valid transitions for the rehearsal loop
   - Implementation notes: pure TypeScript reducer; no UI coupling
   - Acceptance: invalid transitions are rejected; reset always returns to standby
2. `SUP-102 Build deterministic lane timeline model`
   - Purpose: represent tape motion and authored windows cleanly
   - Implementation notes: tape events ordered by `t`; cursor supports play/step/reset
   - Acceptance: same tape produces same cursor positions every run
3. `SUP-103 Add commit-hold mechanic`
   - Purpose: replace click confirmation with weighted commitment
   - Implementation notes: hold duration threshold; release early cancels
   - Acceptance: early release never commits; full hold records commit timestamp
4. `SUP-104 Add resolution and afterimage state`
   - Purpose: make outcome and reflection part of the loop
   - Implementation notes: freeze lane on resolution; generate compact afterimage summary
   - Acceptance: every resolved run produces outcome + debrief + reset path

### Phase 2 — Replay Product
5. `SUP-201 Define bundled tape format and loader`
   - Purpose: make v1 independent from live APIs
   - Implementation notes: JSON tapes, manifest, mode-based loading
   - Acceptance: tutorial and replay tapes load from bundled assets
6. `SUP-202 Ship first tutorial tape set`
   - Purpose: guarantee a strong first session
   - Implementation notes: 3 authored tapes with easier windows and explicit route snapshots
   - Acceptance: user can finish a full tutorial run without credentials
7. `SUP-203 Implement route evaluator`
   - Purpose: show gross, deductions, net, and route quality deterministically
   - Implementation notes: pure functions against route snapshots
   - Acceptance: route outputs are stable for the same snapshot
8. `SUP-204 Add starter bot presets`
   - Purpose: let users compare disciplined preset behavior without customization
   - Implementation notes: Safe, Balanced, Aggressive use deterministic thresholds
   - Acceptance: same preset on same tape yields same decision timing
9. `SUP-205 Build inline debrief surface`
   - Purpose: teach through consequence rather than copy
   - Implementation notes: max 4 lines, fed by evaluator + run engine
   - Acceptance: every run ends with concise outcome + recommendation

### Phase 3 — Product Shell
10. `SUP-301 Build mode-select entry screen`
    - Purpose: make Tutorial and Replay the visible default
    - Implementation notes: one playfield, three options, Live Books visibly locked
    - Acceptance: no scrolling; live mode is subordinate
11. `SUP-302 Add persistence and progress gating`
    - Purpose: track improvement and gate Live Books simply
    - Implementation notes: save mode, run history, successfulRuns, consistencyScore locally
    - Acceptance: app reload restores progress and last selected mode
12. `SUP-303 Add Live Books locked view`
    - Purpose: create aspiration without widening v1
    - Implementation notes: read-only copy and unmet requirements only
    - Acceptance: no credentials requested from first-run path

### Phase 4 — Quality
13. `SUP-401 Stabilize motion and frame timing`
    - Purpose: preserve mechanical feel
    - Implementation notes: requestAnimationFrame, transform-only motion, no layout churn
    - Acceptance: playback remains visually stable under step and run
14. `SUP-402 Add deterministic engine tests`
    - Purpose: lock product identity to reliable behavior
    - Implementation notes: fixtures for state machine, evaluator, bot presets, tape playback
    - Acceptance: same tape + preset + actions always yields the same outcome
15. `SUP-403 Package first Windows rehearsal build`
    - Purpose: produce the first consumer EXE slice
    - Implementation notes: bundle tapes, local persistence, no cloud requirement
    - Acceptance: installer boots to mode select and can finish a tutorial run offline

## 8. Recommended Desktop Shell Choice
- Recommendation: `Tauri 2 + React + TypeScript`
- Why:
  - small Windows footprint
  - good local file bundling for tapes
  - straightforward EXE packaging
  - lets the UI stay TypeScript-first without forcing a browser-style product shell

## 9. First Shipping Slice for EXE
- Mode Select
- Tutorial tape #1
- Replay tape #1
- Safe / Balanced / Aggressive preset playback
- Start / Step / Hold to Commit / Reset loop
- Inline debrief
- Local progress save
- Live Books locked screen

## 10. Immediate Next Steps
1. Wire the state machine and tape engine together.
2. Hook one tutorial tape into the Run screen.
3. Render the single central lane with deterministic stepping.
4. Attach hold-to-commit and resolution logic.
5. Persist run history and live gate progress locally.

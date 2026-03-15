# Repo Understanding Memo

This memo is the distilled understanding of the current repository.

## What the repo already does well

- It already has a real product spine.
- It is not just a script repo.
- It has a disciplined trust model.
- It already contains a coherent release lane.

### Current structure
You are working in the Superior repository from `arbitrage-main.zip`.

Ground truth from the repo:
- Public product name: Superior. Current Python package and entrypoints still use `market-data-recorder`.
- Stack: Python 3.11, PySide6 desktop app, DuckDB recorder core, Astro public site, PyInstaller + Inno Setup Windows packaging.
- Core packages:
  - `src/market_data_recorder/`: recorder core, CLI, storage, replay, verify, websocket/gamma/clob clients.
  - `src/market_data_recorder_desktop/`: onboarding wizard, profile store, keychain-backed credentials, scanner, paper bots, score attack, unlock flow, coach, diagnostics, Qt UI.
  - `site/`: Astro landing/docs/download surface with variant lab.
  - `packaging/windows/`: EXE + installer lane.
- Important desktop files and classes:
  - `window.py`: `DesktopMainWindow`, `ArcadeScannerWidget`, tab classes.
  - `ui/hangar.py`: newer Hangar-specific UI components.
  - `ui/shell.py`: shell, header, nav, state overlays.
  - `ui/theme.py`: `ThemeTokens`, stylesheet generation.
  - `wizard.py`: guided onboarding flow.
  - `bot_services.py`: `VenueAdapter`, `ContractMatcher`, `OpportunityEngine`, `PaperExecutionEngine`, `LiveExecutionEngine`, `UnlockService`, `ExperimentalLiveService`, `AssistantService`, `ArbitrageService`.
  - `score_attack.py`: bot blueprints/configs, unlock tracks, paper simulation, progression.
  - `qa_client.py`: product-level deterministic QA scenarios and headless report export.
- Existing product posture is intentionally trustworthy:
  - paper-first
  - live locked by default
  - local-first
  - keychain-only secrets
  - no profit guarantees
  - experimental live is staged and tiny
- Existing design docs matter:
  - `docs/superior-graphics-system.md`
  - `docs/risk-model.md`
  - `docs/architecture.md`
  - `docs/testing.md`
- Existing visual direction is already close to the target:
  - dark graphite/navy
  - thin vector geometry
  - radial scanner focal point
  - cyan / green / magenta / yellow accents
  - “focused 16-bit market machine”, not a finance dashboard
  - Polybius / arcade cabinet energy, but restrained and trustworthy

## Product interpretation

Right now, the repo is strongest as:
- a beginner-safe prediction-market desktop machine
- a local-first recorder/scanner/paper-run loop
- a gradual unlock system
- a public site + Windows release lane

It is **not yet fully the GMOD-for-bots sandbox**, but it has the right seams to evolve there.

## Current strengths

1. Strong trust posture.
2. Reusable recorder core.
3. Explicit service boundaries.
4. Serious product docs.
5. Real visual theory already documented.
6. Deterministic QA client with scenario artifacts.

## Current tensions / opportunities

1. Brand split:
   - public name = Superior
   - package/entrypoints = market-data-recorder

2. UI duplication:
   - `window.py` contains older tab/widget surfaces and primitives
   - `ui/hangar.py` / `ui/shell.py` / `ui/theme.py` look like the newer system
   - there is room to consolidate toward one design system

3. Product center of gravity:
   - currently recorder/scanner/paper-first
   - future target should lean more into Hangar / Bot Bay / Replay Lab / Registry

4. “Fun engine” is mostly conceptual right now:
   - score attack is present
   - unlocks are present
   - bot slots are present
   - but the sandbox / bot garage / replay film-room identity can get much stronger

## Correct product evolution

Do not throw away the current trust-first spine.

Instead, evolve in this order:
1. clean up brand and UI system
2. strengthen Hangar / Scanner / Score / Live Gate
3. make bot slots feel like a real bot bay
4. add replay lab
5. add registry/forking/recipes
6. add carefully staged macOS support
7. expand QA + release coverage

## Design brief recap

Design target:
Superior should feel like a radically high-quality local market machine.

Emotional feel:
- mission control
- cabinet loadout
- score attack
- replay lab
- trustworthy experimental machine

Visual inspirations:
- Polybius cabinet
- restrained CRT scanlines
- military/mission display discipline
- 16-bit vector geometry
- authored EXE, not a themed dashboard

Not allowed:
- meme trading visuals
- giant rounded SaaS cards everywhere
- gamer RGB clutter
- overblown gradients
- generic admin-template spacing
- copy that implies guaranteed gains

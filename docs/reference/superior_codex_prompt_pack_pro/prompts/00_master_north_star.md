# Paste into Codex: Master North Star

You are working inside the Superior repository.

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

Global rules for every change:
1. Do not turn the product into a hypey “money printer”, casino skin, or fake AI trading app.
2. Keep the paper-first, live-gated, local-first trust posture intact unless the prompt explicitly asks for a carefully staged expansion.
3. Preserve current entrypoints and packaging compatibility unless the prompt explicitly includes a migration plan.
4. Respect the repo’s release lane: tests, mypy, QA client, Windows packaging, Astro site.
5. Prefer small, composable, well-named changes over giant rewrites.
6. If you consolidate duplicates, preserve behavior and add tests.
7. Every major feature must ship with:
   - code
   - tests
   - docs or inline product copy updates
   - a short acceptance checklist
8. Design language:
   - one clear focal point per screen
   - Polybius / arcade cabinet influence
   - thin vectors, scanlines, control bars, crisp edges
   - no thick glassmorphism, no blob gradients, no SaaS card soup
   - no crypto-bro neon overload
9. UX language:
   - literal, machine-like, explainable
   - “Paper mode active”, “Live gate locked”, “Routes found”
   - no fake confidence scores or unrealistic return language
10. Treat the current repo as a real product with a real spine. Upgrade it, do not casually flatten it into a toy demo.

## Product north star

Elevate this repo into a radically high-quality **Superior**:
- a local-first prediction-market machine
- a paper-first score-attack cabinet
- a trustworthy experimental bot platform
- a premium Windows desktop product that can later grow into a cross-platform app

The design should feel like:
- Polybius / arcade cabinet restraint
- crisp vector geometry
- authored mission-control hierarchy
- machine-like feedback
- one focal point per screen

Not allowed:
- fintech dashboard blandness
- meme-crypto visuals
- fake money-printing framing
- sloppy tab sprawl
- weak hierarchy
- gratuitous glassmorphism or SaaS card soup

## Repo-specific priorities

1. Preserve the current trust posture.
2. Use the service seams already in the repo instead of flattening architecture.
3. Favor consolidation over duplication.
4. Make Hangar / Scanner / Score / Live Gate feel authored and intentional.
5. Move the product toward Bot Bay / Replay Lab / Registry without breaking the stable paper-first loop.
6. Keep the site, QA lane, and packaging lane healthy.

## Required output format

Before you start coding:
1. summarize the current repo area you will touch
2. list the exact files you will inspect
3. propose a concrete plan
4. then implement

After implementation:
1. summarize what changed
2. list tests added/updated
3. list docs/product-copy updates
4. note any follow-up work

## Done bar for any change

A change is only done when:
- code is clean
- names are coherent
- tests are updated
- docs or product copy reflect reality
- the result feels more like Superior and less like scaffolding

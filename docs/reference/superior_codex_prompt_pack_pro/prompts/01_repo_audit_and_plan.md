# Prompt 01: Audit the repo, map the architecture, and produce a staged implementation plan

Paste this entire prompt into Codex.

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

## Objective

Deeply inspect the current repo and produce a concrete staged plan for upgrading Superior without destabilizing the current release lane. Then implement only the smallest high-value cleanup that clarifies the architecture.

## Files to inspect first

- `README.md`
- `docs/architecture.md`
- `docs/testing.md`
- `docs/superior-graphics-system.md`
- `src/market_data_recorder_desktop/window.py`
- `src/market_data_recorder_desktop/ui/hangar.py`
- `src/market_data_recorder_desktop/ui/shell.py`
- `src/market_data_recorder_desktop/ui/theme.py`
- `src/market_data_recorder_desktop/bot_services.py`
- `src/market_data_recorder_desktop/score_attack.py`
- `src/market_data_recorder_desktop/qa_client.py`
- `tests/test_desktop_ui.py`
- `tests/test_bot_services.py`

## What to change

1. Write a precise architecture map that explains the current layers, key seams, and which parts are newer versus older surfaces.
2. Identify duplication, naming drift, and tab-level inconsistencies, especially around `window.py` versus `ui/*`.
3. Create a staged plan with milestones for: shell cleanup, Hangar upgrade, Bot Bay evolution, Replay Lab foundation, site polish, and macOS PoC.
4. Implement one small but meaningful cleanup now, such as improving naming, adding a missing architecture doc section, or centralizing a tiny shared helper, as long as it is safe and test-covered.

## Constraints

- Do not start a giant rewrite in this prompt.
- Do not break entrypoints or packaging names yet.
- Be explicit about what should stay stable versus what should evolve.
- Prefer writing clarity into docs if the code is not yet ready for a larger move.

## Deliverables

- production-quality code changes
- updated tests
- updated docs or in-app copy where the behavior changed
- a short implementation summary
- a short “follow-up opportunities” list

## Done bar

- There is a clear staged roadmap grounded in the real repo.
- One safe cleanup landed with tests.
- Future prompts will have a cleaner starting point.

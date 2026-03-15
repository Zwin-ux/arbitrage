# Prompt 02: Unify Superior branding without breaking current package compatibility

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

Strengthen the public/internal naming story so the repo feels like one product: Superior, with an intentional compatibility layer for `market-data-recorder` packaging and CLI names.

## Files to inspect first

- `README.md`
- `pyproject.toml`
- `docs/release-process.md`
- `docs/release-checklist.md`
- `site/src/data/landingVariants.js`
- `site/src/pages/download.astro`
- `src/market_data_recorder_desktop/main.py`
- `src/market_data_recorder_desktop/window.py`
- `packaging/windows/desktop_entry.py`
- `packaging/windows/installer.iss`

## What to change

1. Audit all visible user-facing labels, copy, installer text, titles, and docs for brand consistency.
2. Define a compatibility policy: product name = Superior, package/runtime compatibility = market-data-recorder for v1.
3. Update copy so users always understand the relationship and do not feel brand drift.
4. Add a small, explicit note in relevant docs and/or About surfaces explaining the compatibility story.
5. Keep release links and installer behavior intact unless the prompt clearly includes a migration plan.

## Constraints

- Do not rename import packages or break existing scripts in this prompt.
- Do not casually rename the CLI entrypoints.
- Make the naming story clearer, not noisier.

## Deliverables

- production-quality code changes
- updated tests
- updated docs or in-app copy where the behavior changed
- a short implementation summary
- a short “follow-up opportunities” list

## Done bar

- A user can understand the product name versus compatibility names instantly.
- The repo feels less split between ‘Superior’ and ‘market-data-recorder’.
- No packaging or install path regressions were introduced.

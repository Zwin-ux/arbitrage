# Prompt 07: Evolve Loadout into a true Bot Bay / cabinet loadout surface

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

Upgrade the Loadout screen so it feels like arming a bot machine, not filling out a settings form.

## Files to inspect first

- `src/market_data_recorder_desktop/window.py`
- `src/market_data_recorder_desktop/score_attack.py`
- `src/market_data_recorder_desktop/bot_services.py`
- `src/market_data_recorder_desktop/app_types.py`
- `tests/test_desktop_ui.py`
- `tests/test_bot_services.py`

## What to change

1. Use the existing bot slot, blueprint, and unlock concepts to make the loadout surface feel like a Bot Bay.
2. Make slot states and unlock logic visually clear: empty, armed, staged, running, banked, blocked, locked.
3. Show strategy family, threshold, target stake, and why a slot is available or unavailable.
4. Expose equipped connectors and modules in a more cabinet-like, low-clutter layout.
5. Rename in-app copy where needed so ‘Loadout’ reads as an intentional Superior surface, possibly ‘Loadout / Bot Bay’ or similar transitional wording.

## Constraints

- Do not promise a full visual bot builder yet.
- Do not break the existing config logic in `score_attack.py`.
- Keep the paper-first tone.

## Deliverables

- production-quality code changes
- updated tests
- updated docs or in-app copy where the behavior changed
- a short implementation summary
- a short “follow-up opportunities” list

## Done bar

- The screen feels like arming a machine.
- Bot slots have identity.
- Unlocks and restrictions are easy to understand.

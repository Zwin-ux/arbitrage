# Repo Map Quick Reference

## Core runtime
- `src/market_data_recorder/`
  - `service.py`: async recorder flow
  - `storage.py`: DuckDB persistence
  - `replay.py`: replay utilities
  - `verify.py`: validation
  - `arbitrage.py`: CLI arbitrage analysis
  - `clients/`: Gamma, CLOB, websocket

## Desktop
- `main.py`: app boot, style, smoke mode
- `window.py`: main window, tabs, scanner widget
- `ui/theme.py`: desktop tokens + stylesheet
- `ui/shell.py`: shell/header/nav/state overlays
- `ui/hangar.py`: Hangar-specific UI system
- `wizard.py`: guided onboarding
- `profiles.py`: profile store
- `credentials.py`: keychain-backed providers
- `bot_services.py`: venue/loadout/opportunity/paper/live/assistant services
- `score_attack.py`: bot configs, slot unlocks, paper simulation, progression
- `qa_client.py`: deterministic product QA client

## Site
- `site/src/data/landingVariants.js`
- `site/src/components/landing/*`
- `site/src/pages/index.astro`
- `site/src/pages/download.astro`
- `site/tests/landing.spec.ts`

## Packaging
- `packaging/windows/*`
- `scripts/build-windows-release.ps1`
- `scripts/smoke-test-windows-release.py`
- `scripts/smoke-test-installer.ps1`

## Docs worth reading before major changes
- `README.md`
- `docs/architecture.md`
- `docs/superior-graphics-system.md`
- `docs/risk-model.md`
- `docs/testing.md`
- `docs/first-paper-run.md`

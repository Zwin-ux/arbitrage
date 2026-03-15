# Superior Codex Prompt Pack Pro

This pack is tailored to the actual repository structure from `arbitrage-main.zip`.

It is built for Codex sessions that need to make **high-quality, repo-aware changes** without losing the current strengths of the codebase:
- Windows-first, local-first desktop shell
- PySide6 app with guided onboarding
- recorder/scanner/paper-bot loop
- explainable opportunity engine
- QA client and packaging lane
- Astro public site
- trust-first product posture

## What this pack is for

Use these prompts to push the repo toward a more premium, more authored, more modular **Superior**:
- stronger shell and visual system
- cleaner tab architecture
- better Hangar / Scanner / Score / Live Gate
- evolution toward Bot Garage / Replay Lab / Registry
- tighter docs and site tone
- a real macOS proof-of-concept path
- better release/QA coverage

## What I studied in the repo before building this pack

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

## Core design stance

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

## How to use this pack

1. Start every serious Codex session with:
   - `prompts/00_master_north_star.md`
   - one targeted workstream prompt
2. For large sessions, also include:
   - `REPO_UNDERSTANDING_MEMO.md`
   - `EXPERIENCE_SIMULATION_CHECKLIST.md`
3. For release-quality work, finish with:
   - `prompts/23_final_polish_pass.md`
   - `prompts/25_performance_accessibility_and_responsiveness.md`
4. For macOS exploration, use:
   - `prompts/20_macos_poc_cross_platform_qt.md`
   - `prompts/21_macos_packaging_and_launchagent.md`
   - bonus templates in `bonus/macos_poc/`

## Suggested run order

See:
- `INDEX.md`
- `PROMPT_STACKING_GUIDE.md`

## Bonus material

- `bonus/macos_poc/`: starter templates for packaging + LaunchAgent PoC
- `bonus/issue_board/`: epics and issue seeds
- `session_bundles/`: ready-to-paste multi-step sessions

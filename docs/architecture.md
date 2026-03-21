# Architecture

## Layers

- `market_data_recorder`: async recorder core, CLI, storage, replay, verify
- `market_data_recorder_desktop`: guided onboarding, profile store, keychain-backed credentials, scanner, practice-run engine, unlock flow, coach, diagnostics, Qt UI
- `packaging/windows`: PyInstaller and Inno Setup assets
- `site`: Astro static site for Railway-hosted docs/download surface

## Runtime Shape

- The CLI and desktop app share the same recorder core.
- The desktop app runs recorder actions through `EngineController`.
- Scanner and practice-run flows sit on top of local DuckDB recorder data.
- Long-running recorder work executes in a background thread so the UI remains responsive.
- Profiles live in per-user config storage; secrets live in the OS keychain only.
- The coach is read-only and local-first; it does not enter the live execution path.

## Desktop UI Ownership

- `src/market_data_recorder_desktop/ui/primitives.py` is the shared source of truth for small framed desktop primitives such as badges, state cards, and stat cells.
- `src/market_data_recorder_desktop/ui/scanner.py` owns the radial scanner centerpiece and its machine-style telemetry rendering.
- `src/market_data_recorder_desktop/ui/hangar.py` owns the Home control-surface composition: mission header, checklist, action bar, system console, progress panel, and telemetry group.
- `src/market_data_recorder_desktop/window.py` should orchestrate tabs, services, and state refreshes. It should not be the long-term home for duplicate primitive widgets.

## Score-Attack Engine

- `score_attack.py` owns the practice-run machine:
  - starter bot blueprints and slot previews
  - starter registry visibility
  - unlock track evaluation
  - portfolio snapshots
  - decision traces for practice runs
- The intended user loop is:
  - finish setup
  - arm starter bots
  - refresh the scanner
  - stage a practice run
  - bank score
  - inspect unlock progress and decision traces

## Future Compatibility

- The desktop layer isolates startup behavior behind `StartupManager`.
- The recorder core remains reusable for a future macOS service/LaunchAgent host.
- Venue-specific logic is isolated behind `VenueAdapter`, `ContractMatcher`, `OpportunityEngine`, `PaperExecutionEngine`, and `UnlockService`.
- The public website is isolated from recorder runtime concerns and should remain a static showcase/docs surface.

# Superior

![Superior emblem](docs/assets/superior-emblem.png)

Open-source, Windows-first prediction-market desktop app for learning Polymarket, recording market data, scanning explainable arbitrage ideas, and paper-testing bots before any live unlock.

The public brand is `Superior`. The current Python package name and CLI entrypoints remain `market-data-recorder` in v1 to avoid breaking existing packaging and release links.

You can complete the first paper loop without entering any venue credentials: equip Polymarket, record a local sample, inspect one route, paper it, and watch Score update.

## What it includes

- Guided desktop onboarding for Polymarket-first users
- Local-first recorder built on current Gamma, CLOB, and market WebSocket flows
- Explainable scanner for internal binary dislocation and future exact-match cross-venue work
- Paper bot execution with simple deterministic fills and local portfolio history
- Live-unlock checklist tied to credentials, diagnostics, risk acknowledgements, and paper activity
- OS-keychain-backed credential vault for Polymarket, Kalshi, and optional AI coach keys
- Open packaging assets for PyInstaller and Inno Setup
- Astro-based public site for Railway deployment

## Product posture

- License: MIT
- Telemetry: off by default
- Secrets: OS keychain only
- Default mode: guided beginner, paper first
- Live mode: locked until the checklist passes
- Lab strategies: explicit opt-in and paper-only in v1
- Profit claims: none; the software aims to be stable and transparent, not to guarantee returns

## Install

```bash
python -m pip install -e ".[dev]"
```

For packaging work:

```bash
python -m pip install -e ".[packaging]"
```

For the public site:

```bash
npm.cmd --prefix site install
npm.cmd --prefix site run build
```

## Entry points

Launch the desktop app:

```bash
market-data-recorder-app
```

Launch the desktop QA client:

```bash
market-data-recorder-qa
market-data-recorder-qa --headless --output .tmp/qa-report.json
```

Run the recorder and analysis CLI:

```bash
market-data-recorder discover
market-data-recorder record
market-data-recorder replay
market-data-recorder verify
market-data-recorder arbitrage --min-edge 0.02
```

## Desktop app surface

The Superior shell is built around:

- `Hangar`: safe state, venue connections, recorder controls, and next steps
- `Loadout`: equip connectors and strategy modules deliberately
- `Learn`: local-first coach and beginner guidance
- `Scanner`: explainable opportunity candidates
- `Paper Bots`: deterministic paper runs against current candidates
- `Score`: local paper ledger, score board, and recent run history
- `Live Gate`: checklist and acknowledgements
- `Lab`: explicit experimental surface
- `Diagnostics` and `About`

## Storage

DuckDB tables are documented in [`docs/schema.md`](docs/schema.md).

Desktop app data uses per-user paths from `platformdirs`:

- config: `profiles.json`
- data: profile DuckDB files, paper run history, and exports
- logs: per-user app log directory

Secrets are not stored in those paths.

## Trust docs

- [`docs/risk-model.md`](docs/risk-model.md)
- [`docs/live-trading-limitations.md`](docs/live-trading-limitations.md)
- [`docs/privacy-and-secrets.md`](docs/privacy-and-secrets.md)
- [`docs/first-paper-run.md`](docs/first-paper-run.md)
- [`docs/release-checklist.md`](docs/release-checklist.md)
- [`docs/strategy-contributor-guide.md`](docs/strategy-contributor-guide.md)
- [`docs/release-process.md`](docs/release-process.md)

## Packaging

- PyInstaller spec: [`packaging/windows/market_data_recorder_app.spec`](packaging/windows/market_data_recorder_app.spec)
- Inno Setup script: [`packaging/windows/installer.iss`](packaging/windows/installer.iss)
- Official Inno Setup bootstrap: [`scripts/bootstrap-iscc.ps1`](scripts/bootstrap-iscc.ps1)
- Release build script: [`scripts/build-windows-release.ps1`](scripts/build-windows-release.ps1)
- Packaged app smoke test: [`scripts/smoke-test-windows-release.py`](scripts/smoke-test-windows-release.py)
- Installer smoke test: [`scripts/smoke-test-installer.ps1`](scripts/smoke-test-installer.ps1)
- Release manifest: `dist/SHA256SUMS.txt`

## Public site

- Site source: [`site/`](site/)
- Railway config: [`site/railway.toml`](site/railway.toml)
- Release/download target: [GitHub Releases](https://github.com/Zwin-ux/arbitrage/releases)
- Variant lab: `/lab`, `/lab/control`, `/lab/focus`

Railway should host only the public site. The app runtime, secrets, and user data should not be deployed there.

## Development checks

```bash
pytest -q
python -m mypy src tests
market-data-recorder-qa --headless --output .tmp/qa-report.json
npm.cmd --prefix site run build
npm.cmd --prefix site run test:browser
```

See [`docs/testing.md`](docs/testing.md) for the Windows release lane, frontend checks, and the new QA client workflow.

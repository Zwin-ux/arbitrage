# market-data-recorder

Open-source Polymarket market-data recorder with a Typer CLI and a Windows-first PySide6 desktop app.

## What it includes

- Public Polymarket recorder built on current Gamma, CLOB, and market WebSocket flows
- DuckDB-backed raw and normalized storage
- Replay and verify tooling
- Desktop onboarding wizard with multiple profiles
- OS-keychain-backed credential vault for Polymarket and Kalshi
- Local-only diagnostics export and tray-based background flow
- Open packaging assets for PyInstaller and Inno Setup
- Astro-based public site for Railway deployment

## Open-Source Defaults

- License: MIT
- Telemetry: off by default
- Secrets: OS keychain only
- Build scripts: committed in `packaging/windows`
- Docs: architecture, release process, and privacy docs in `docs/`
- Public site: committed in `site/`

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

## CLI

Discover current tradable markets:

```bash
market-data-recorder discover
```

Record indefinitely:

```bash
market-data-recorder record
```

Replay stored raw messages:

```bash
market-data-recorder replay
```

Verify stored hashes and stream consistency:

```bash
market-data-recorder verify
```

## Desktop App

Launch the GUI:

```bash
market-data-recorder-app
```

The desktop app provides:

- first-run setup wizard
- multiple profiles with per-profile data directories
- optional Polymarket and Kalshi credential storage
- default presets for record, replay, and verify
- diagnostics and trust/about views
- system tray behavior for long-running recorder sessions

## Storage

DuckDB tables are documented in [`docs/schema.md`](docs/schema.md).

Desktop app data uses per-user paths from `platformdirs`:

- config: `profiles.json`
- data: profile DuckDB files and exports
- logs: per-user app log directory

Secrets are not stored in those paths.

## Packaging

- PyInstaller spec: [`packaging/windows/market_data_recorder_app.spec`](packaging/windows/market_data_recorder_app.spec)
- Inno Setup script: [`packaging/windows/installer.iss`](packaging/windows/installer.iss)
- Official Inno Setup bootstrap: [`scripts/bootstrap-iscc.ps1`](scripts/bootstrap-iscc.ps1)
- Release build script: [`scripts/build-windows-release.ps1`](scripts/build-windows-release.ps1)

## Public Site

- Site source: [`site/`](site/)
- Railway config: [`site/railway.toml`](site/railway.toml)
- Release/download target: [GitHub Releases](https://github.com/Zwin-ux/arbitrage/releases)

Railway should host only the public site. The recorder runtime, secrets, and user data should not be deployed there.

Railway setup for this monorepo:

1. Connect the GitHub repo to a Railway service.
2. Set the service root directory to `/site`.
3. Set the config-as-code path to `/site/railway.toml`.
4. Generate a public Railway domain.
5. Set `SITE_URL` to the public Railway URL once the domain exists.
6. Enable `Wait for CI` so deployments wait for the GitHub Actions workflow on `main`.

## Development Checks

```bash
pytest -q
python -m mypy src tests
npm.cmd --prefix site run build
```

## Notes

- The workspace runtime is Python 3.11. The package targets 3.11+.
- The recorder core remains deterministic and reusable from both CLI and desktop flows.
- The desktop credential vault stores secrets only in the OS keychain and validates completeness locally.

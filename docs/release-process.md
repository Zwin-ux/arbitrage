# Release Process

## Desktop Build

1. Install packaging dependencies:
   `python -m pip install -e ".[packaging]"`
2. Install or verify `ISCC` using `scripts/bootstrap-iscc.ps1`.
3. Build the release assets with `scripts/build-windows-release.ps1`.
4. Smoke-test install, launch, record, replay, verify, and uninstall.

## Signing

Code-signing certificates and distribution credentials may stay private operational material. The build scripts themselves stay in-repo.

## Required Checks

- `pytest -q`
- `python -m mypy src tests`
- `npm --prefix site ci`
- `npm --prefix site run build`
- local GUI launch
- installer output contains license and third-party notices

## GitHub Releases and Railway

- GitHub Releases should host the Windows installer and portable bundle zip.
- Railway should deploy the Astro site from `site/`.
- Railway should use the default domain first and enable `Wait for CI`.

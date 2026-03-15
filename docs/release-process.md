# Release Process

## Desktop Build

1. Install packaging dependencies:
   `python -m pip install -e ".[packaging]"`
2. Install or verify `ISCC` using `scripts/bootstrap-iscc.ps1`.
3. Build the release assets with `scripts/build-windows-release.ps1`.
4. Confirm the output contains:
   - `dist\market-data-recorder-setup.exe`
   - `dist\market-data-recorder-app-portable.zip`
   - `dist\SHA256SUMS.txt`
5. Smoke-test install, launch, and uninstall through the scripted release lane.

## Signing

Code-signing certificates and distribution credentials may stay private operational material. The build scripts themselves stay in-repo. Until signing exists, public checksums and clear SmartScreen guidance are required.

## Required Checks

- `pytest -q`
- `python -m mypy src tests`
- `market-data-recorder-qa --headless --output .tmp/qa-report.json`
- `npm --prefix site ci`
- `npm --prefix site run build`
- `npm --prefix site run test:browser`
- scripted Windows release build returns zero
- installer output contains license and third-party notices

See [`docs/release-checklist.md`](release-checklist.md) for the full operator checklist and [`docs/testing.md`](testing.md) for the exact smoke lanes.
Use [`docs/release-notes-template.md`](release-notes-template.md) when drafting tag release notes.

## GitHub Releases and Railway

- GitHub Releases should host the Windows installer, portable bundle zip, and `SHA256SUMS.txt`.
- Railway should deploy the Astro site from `site/`.
- Railway should use the default domain first and enable `Wait for CI`.
- Railway should never host runtime services, user data, or secrets.

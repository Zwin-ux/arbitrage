# Release Process

## Desktop Build

1. Install Node dependencies for `desktop-v1`:
   `npm --prefix desktop-v1 ci`
2. Install a stable Rust toolchain.
3. Build the public Windows release with:
   `npm --prefix desktop-v1 run tauri:build`
4. Confirm the release workflow publishes:
   - `Superior_<version>_x64-setup.exe`
   - `Superior_<version>_x64-portable.zip`
   - `Superior_<version>_x64_en-US.msi`
   - `SHA256SUMS.txt`
5. Smoke-test install and first launch from the bundled installer.

## Legacy Python Build

The older Python/Qt release lane remains in-repo for recorder/tooling debt:

1. Install packaging dependencies:
   `python -m pip install -e ".[packaging]"`
2. Install or verify `ISCC` using `scripts/bootstrap-iscc.ps1`.
3. Build the legacy release assets with `scripts/build-windows-release.ps1`.

## Signing

Public releases should be signed when a real Windows code-signing certificate is available. The GitHub release workflow supports optional signing through:

- `WINDOWS_CODESIGN_PFX_BASE64`
- `WINDOWS_CODESIGN_PASSWORD`

Until signing exists, public checksums and clear SmartScreen guidance are required.

## Required Checks

- `pytest -q`
- `python -m mypy src tests`
- `market-data-recorder-qa --headless --output .tmp/qa-report.json`
- `npm --prefix desktop-v1 ci`
- `npm --prefix desktop-v1 run check`
- `npm --prefix desktop-v1 run test`
- `npm --prefix desktop-v1 run build`
- `npm --prefix site ci`
- `npm --prefix site run build`
- `npm --prefix site run test:browser`
- Tauri Windows release build returns zero
- installer output contains the correct app name, icon, and metadata

See [`docs/release-checklist.md`](release-checklist.md) for the full operator checklist and [`docs/testing.md`](testing.md) for the exact smoke lanes.
Use [`docs/release-notes-template.md`](release-notes-template.md) when drafting tag release notes.

## GitHub Releases and Railway

- GitHub Releases should host the Tauri Windows installer, portable zip, MSI, and `SHA256SUMS.txt`.
- Railway should deploy the Astro site from `site/`.
- Railway should use the default domain first and enable `Wait for CI`.
- Railway should never host runtime services, user data, or secrets.

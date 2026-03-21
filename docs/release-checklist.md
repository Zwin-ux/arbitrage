# Release Checklist

Use this before every public Windows release of Superior.

## Product checks

- Confirm the public product name is `Superior` across the desktop app, installer text, site copy, and release notes.
- Confirm the golden path still works in `desktop-v1`: launch, choose a mode, run a practice tape, resolve, reset.
- Confirm the app still defaults to practice money and keeps the live gate locked until the checklist is earned.
- Confirm the site download page points to the current installer, portable zip, source repo, and `SHA256SUMS.txt`.

## Local validation

Run the full local gate:

```powershell
npm.cmd --prefix desktop-v1 ci
npm.cmd --prefix desktop-v1 run check
npm.cmd --prefix desktop-v1 run test
npm.cmd --prefix desktop-v1 run build
npm.cmd --prefix desktop-v1 run tauri:build
python -m pytest -q
python -m mypy src tests
market-data-recorder-qa --headless --workspace .tmp\qa-release --output .tmp\qa-release\report.json
npm.cmd --prefix site run build
npm.cmd --prefix site run test:browser
```

Review:

- `.tmp\qa-release\report.json`
- `desktop-v1\src-tauri\target\release\bundle\nsis\Superior_<version>_x64-setup.exe`
- `desktop-v1\src-tauri\target\release\bundle\msi\Superior_<version>_x64_en-US.msi`
- `dist\Superior_<version>_x64-portable.zip`
- `dist\SHA256SUMS.txt`

## GitHub Actions

- `CI` passes on `main`
- `Desktop V1 Checks` passes on `windows-latest`
- tag builds publish the installer, portable zip, MSI, and checksum manifest

## Release page

- Release notes describe what changed and any known limitations
- Assets include:
  - `Superior_<version>_x64-setup.exe`
  - `Superior_<version>_x64-portable.zip`
  - `Superior_<version>_x64_en-US.msi`
  - `SHA256SUMS.txt`
- publisher metadata is correct on `superior.exe`
- SmartScreen and unsigned-installer expectations are called out clearly if signing is not yet enabled

## Railway/site

- Railway deploy uses `site/` only
- The homepage primary CTA resolves to the latest installer
- The download page resolves to the installer, portable zip, GitHub source, and checksum manifest
- Docs and README describe the same product posture: local-first, practice money first, live-gated

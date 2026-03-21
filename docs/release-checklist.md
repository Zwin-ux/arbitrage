# Release Checklist

Use this before every public Windows release of Superior.

## Product checks

- Confirm the public product name is `Superior` across the desktop app, installer text, site copy, and release notes.
- Confirm the golden path still works: setup, record, scan, practice, score.
- Confirm the app still defaults to practice mode and keeps the live gate locked until the checklist is earned.
- Confirm the site download page points to the current installer, portable zip, source repo, and `SHA256SUMS.txt`.

## Local validation

Run the full local gate:

```powershell
python -m pytest -q
python -m mypy src tests
market-data-recorder-qa --headless --workspace .tmp\qa-release --output .tmp\qa-release\report.json
npm.cmd --prefix site run build
npm.cmd --prefix site run test:browser
powershell -ExecutionPolicy Bypass -File scripts\build-windows-release.ps1
```

Review:

- `.tmp\qa-release\report.json`
- `dist\market-data-recorder-setup.exe`
- `dist\market-data-recorder-app-portable.zip`
- `dist\SHA256SUMS.txt`

## GitHub Actions

- `CI` passes on `main`
- `Windows Package Smoke` passes on `windows-latest`
- tag builds publish the installer, portable zip, and checksum manifest

## Release page

- Release notes describe what changed and any known limitations
- Assets include:
  - `market-data-recorder-setup.exe`
  - `market-data-recorder-app-portable.zip`
  - `SHA256SUMS.txt`
- SmartScreen and unsigned-installer expectations are called out clearly

## Railway/site

- Railway deploy uses `site/` only
- The homepage primary CTA resolves to the latest installer
- The download page resolves to the installer, portable zip, GitHub source, and checksum manifest
- Docs and README describe the same product posture: local-first, practice-first, live-gated

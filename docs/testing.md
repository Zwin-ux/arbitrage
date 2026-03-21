# Testing

This repo now has three deliberate test lanes:

## 1. Windows release lane

Use this before publishing a Windows release:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows-release.ps1
```

To validate the exact shell-wrapped path used by CI/terminal wrappers:

```powershell
cmd /c "powershell -ExecutionPolicy Bypass -File scripts\build-windows-release.ps1 > .tmp\release-run.log 2>&1 & echo EXITCODE:%ERRORLEVEL%"
```

That script now does all of the following:

- runs `pytest -q`
- runs `python -m mypy src tests`
- runs the headless `market-data-recorder-qa` client and writes `.tmp\qa-release\report.json`
- builds the PyInstaller bundle
- builds a packaged smoke companion with the console bootloader
- smoke-tests the packaged build through that frozen smoke companion
- builds the Inno Setup installer
- installs the installer silently into a temp folder
- smoke-tests the installed bundle through the installed smoke companion
- writes final release assets to `dist/`
- writes `dist\SHA256SUMS.txt` for the installer and portable zip

Standalone smoke commands:

```powershell
python -m PyInstaller --noconfirm --distpath .tmp\smoke-companion\dist --workpath .tmp\smoke-companion\build packaging\windows\market_data_recorder_smoke.spec
python scripts\smoke-test-windows-release.py --bundle-exe .tmp\smoke-companion\dist\market-data-recorder-smoke.exe
powershell -ExecutionPolicy Bypass -File scripts\smoke-test-installer.ps1
```

## One-command validation lane

Use this when you want one repeatable developer command instead of remembering every check manually:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-superior.ps1 -IncludeSite
```

Full local gate including site and packaging:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\validate-superior.ps1 -IncludeSite -IncludePackaging
```

That script writes:

- `.tmp\validate-superior.log`
- `.tmp\validate-superior-summary.json`
- a headless QA report under `.tmp\qa-release\report.json` unless you override the workspace/output paths

## Why the smoke companion exists

The shipped Windows app uses the windowed PyInstaller bootloader. In some constrained shell environments, frozen windowed executables are not a reliable automation target even when the app itself is fine for normal desktop users. The smoke companion uses the console bootloader so CI can verify the frozen Python environment, packaged resources, and installer contents deterministically.

GitHub Actions on `windows-latest` is the source of truth for packaged EXE and installer execution.

## 2. QA client lane

Use the local QA client when you want a product-level read on the guided path instead of raw unit tests:

```powershell
market-data-recorder-qa
market-data-recorder-qa --headless --output .tmp\qa-report.json
```

The QA client runs deterministic local scenarios for:

- guided onboarding and profile bootstrap
- setup and capability gating
- scanner detection on seeded Polymarket fixtures
- first practice loop without credentials
- practice-score ledger updates
- experimental live graduation
- live-gate lock and unlock rules
- coach guardrails
- engine controller state transitions

Each scenario writes reviewable artifacts into an isolated workspace so QA can inspect evidence instead of treating success as a black box.

In CI, the headless QA client exports a report artifact named `superior-qa-report`, and the Windows packaging lane also carries the QA report into failure artifacts when the release wrapper fails.

## 3. Frontend variant lane

The site now has a simple variant lab:

- `/` = public homepage control
- `/lab` = variant chooser
- `/lab/control` = control landing page
- `/lab/focus` = challenger landing page

Use this to compare headline, CTA, and product tone without replacing the public homepage immediately.

## Browser smoke tests

Install site dependencies once:

```powershell
npm.cmd --prefix site install
```

Run the browser tests:

```powershell
npm.cmd --prefix site run test:browser
```

These tests confirm:

- the homepage renders and keeps the primary Windows download CTA
- the variant lab is reachable
- the control and focus variants remain intentionally distinct

## CI coverage

GitHub Actions now covers:

- Python tests and mypy
- headless QA client with an uploaded JSON/artifact trail
- Windows package build + smoke tests
- QA client coverage through the normal Python test suite
- site build + browser smoke tests

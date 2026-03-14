# Testing

This repo now has two deliberate test lanes:

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
- builds the PyInstaller bundle
- builds a packaged smoke companion with the console bootloader
- smoke-tests the packaged build through that frozen smoke companion
- builds the Inno Setup installer
- installs the installer silently into a temp folder
- smoke-tests the installed bundle through the installed smoke companion
- writes final release assets to `dist/`

Standalone smoke commands:

```powershell
python -m PyInstaller --noconfirm --distpath .tmp\smoke-companion\dist --workpath .tmp\smoke-companion\build packaging\windows\market_data_recorder_smoke.spec
python scripts\smoke-test-windows-release.py --bundle-exe .tmp\smoke-companion\dist\market-data-recorder-smoke.exe
powershell -ExecutionPolicy Bypass -File scripts\smoke-test-installer.ps1
```

## Why the smoke companion exists

The shipped Windows app uses the windowed PyInstaller bootloader. In some constrained shell environments, frozen windowed executables are not a reliable automation target even when the app itself is fine for normal desktop users. The smoke companion uses the console bootloader so CI can verify the frozen Python environment, packaged resources, and installer contents deterministically.

GitHub Actions on `windows-latest` is the source of truth for packaged EXE and installer execution.

## 2. Frontend variant lane

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
- Windows package build + smoke tests
- site build + browser smoke tests

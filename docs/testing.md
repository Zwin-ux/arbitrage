# Testing

This repo now has two deliberate test lanes:

## 1. Windows release lane

Use this before publishing a Windows release:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\build-windows-release.ps1
```

That script now does all of the following:

- runs `pytest -q`
- runs `python -m mypy src tests`
- builds the PyInstaller bundle
- smoke-tests the packaged `.exe` via built-in desktop app smoke mode
- builds the Inno Setup installer
- installs the installer silently into a temp folder
- smoke-tests the installed app
- writes final release assets to `dist/`

Standalone smoke commands:

```powershell
python scripts\smoke-test-windows-release.py --bundle-exe dist\market-data-recorder-app\market-data-recorder-app.exe
powershell -ExecutionPolicy Bypass -File scripts\smoke-test-installer.ps1
```

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

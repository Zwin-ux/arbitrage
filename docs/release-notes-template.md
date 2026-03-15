# Release Notes Template

Use this when publishing a new public beta tag for Superior.

## Summary

- one short paragraph on what changed
- one short paragraph on who should care

## What changed

- user-facing improvements
- release engineering or installer fixes
- docs or trust updates

## Verification

- `market-data-recorder-setup.exe`
- `market-data-recorder-app-portable.zip`
- `SHA256SUMS.txt`
- CI passed on `main`
- Windows package smoke passed

## Known issues

- SmartScreen friction is expected until signing exists
- Windows is the only supported packaged platform in v1 beta
- `Live Gate` is visible but public live execution remains out of scope

## Verify your download

Compare the installer or portable zip against `SHA256SUMS.txt` from the same release before running it.

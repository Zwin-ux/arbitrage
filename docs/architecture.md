# Architecture

## Layers

- `market_data_recorder`: async recorder core, CLI, storage, replay, verify
- `market_data_recorder_desktop`: profile store, keychain-backed credentials, controller, diagnostics, Qt UI
- `packaging/windows`: PyInstaller and Inno Setup assets
- `site`: Astro static site for Railway-hosted docs/download surface

## Runtime Shape

- The CLI and desktop app share the same core services.
- The desktop app runs recorder actions through `EngineController`.
- Long-running recorder work executes in a background thread so the UI remains responsive.
- Profiles live in per-user config storage; secrets live in the OS keychain only.

## Future Compatibility

- The desktop layer isolates startup behavior behind `StartupManager`.
- The recorder core remains reusable for a future macOS service/LaunchAgent host.
- The public website is isolated from recorder runtime concerns and should remain a static showcase/docs surface.

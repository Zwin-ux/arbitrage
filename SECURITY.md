# Security Policy

## Scope

This project is local-first and stores credentials only in the OS keychain. Bugs that expose secrets, bypass profile isolation, or cause unintended network behavior are security issues.

## Reporting

- Do not open public issues for secret-handling vulnerabilities.
- Report privately to the maintainers for coordinated remediation.
- Include affected version, platform, and the smallest redacted reproduction possible.

## Supported Expectations

- Secrets must not be written to JSON, DuckDB, logs, or diagnostics bundles.
- Telemetry is off by default.
- Packaging scripts and runtime dependencies must remain inspectable in-repo.

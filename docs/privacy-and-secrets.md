# Privacy and Secrets

## What Stays Local

- profile JSON
- DuckDB market data
- diagnostics exports
- credential material stored in the OS keychain

## What Must Never Happen

- private keys in `.env`
- secrets in `profiles.json`
- secrets in DuckDB
- secrets in logs or exported diagnostics

## Telemetry

Telemetry is off by default. Diagnostics export is manual and writes a user-selected local JSON bundle.

## Credential UX

- users may skip credentials entirely
- the app validates credential completeness locally
- future live-trading adapters must continue using the same keychain-only storage rule

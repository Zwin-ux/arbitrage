# Contributing

## Ground Rules

- Keep runtime behavior deterministic.
- Do not add hosted control-plane dependencies.
- Do not store secrets outside the OS keychain.
- Keep the CLI working when desktop features change.

## Local Setup

```bash
python -m pip install -e ".[dev]"
pytest -q
python -m mypy src tests
```

## Pull Requests

- Add or update tests for behavior changes.
- Call out any new user-visible settings, packaging steps, or security implications.
- Prefer additive migrations for profiles and desktop config.

## Issues

- Use reproducible steps.
- Include redacted diagnostics bundles when relevant.
- Never paste real private keys, passphrases, or PEM material.

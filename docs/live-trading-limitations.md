# Live Trading Limitations

Superior v1 is a staged consumer autopilot, not a broad trading engine.

## Live is intentionally narrow

- The consumer path is `learn`, `shadow`, `armed`, `auto on`, then `halted` if something goes wrong.
- `Shadow` stays read-only and records would-be decisions before auto can be armed.
- The first real-money live lane is Kalshi-only.
- The first live strategy family is internal-binary only.
- Validated credentials, shadow completion, and visible caps must exist before auto can start.
- Tiny live caps are intentional. The point is constrained trust, not broad autonomy.

## Live mode does not mean unlimited autonomy

- The starter bot can only run inside its fixed venue, strategy, and cap envelope.
- The in-app coach cannot place trades or override risk controls.
- Experimental Lab strategies do not bypass the starter-bot gate.
- A kill switch must remain visible on the main consumer path.
- Live claims must stay narrower than the actual execution spine.

## Hosted services

- Railway hosts only the public site.
- User data, diagnostics, and secrets remain local-first.
- No hosted bot runtime is part of v1.

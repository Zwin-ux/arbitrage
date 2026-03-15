# Live Trading Limitations

Superior v1 is paper-first.

## Experimental live is intentionally limited

- Live begins as a staged rollout: `locked`, `shadow`, `micro`, then `experimental`.
- `Shadow` mode never sends real orders. It records would-be live decisions only.
- `Micro` and `experimental` modes are Polymarket-first in v1.
- Validated credentials, paper activity, and risk acknowledgements must exist before live modes above `shadow`.
- Critical diagnostics issues block progression.
- Tiny live caps are intentional. The point is controlled experimentation, not broad consumer autonomy.

## Live mode does not mean autonomy

- The in-app coach cannot place trades.
- The coach cannot unlock live mode.
- The coach cannot override risk controls.
- Experimental Lab strategies do not bypass the paper-first gate.
- Paper score and live score remain separate.

## Hosted services

- Railway hosts only the public site.
- User data, diagnostics, and secrets remain local-first.
- No hosted bot runtime is part of v1.

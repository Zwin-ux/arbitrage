# Superior Graphics System

## Purpose

Superior should feel like a focused 16-bit market machine, not a business dashboard. The graphics system exists to create:

- one clear visual center per screen
- machine-like feedback during recorder and scanner use
- strong contrast between active, locked, and idle states
- a consistent retro-arcade language across the EXE, site, and release assets

The target mood is:

- technical
- hypnotic
- symmetric
- restrained
- local-first and trustworthy

## Visual Principles

### Radial focus

Every major screen should have one centered visual anchor. The primary pattern is a radial scanner:

- uniform vector lines
- central signal node
- rotating sweep
- orbiting data dots
- shallow CRT scanlines

Use this in:

- `Scanner` as the main center visual
- `Home` in compact form when showing mission readiness
- `Score` in a later pass as a probability or score ring

### Thin vector geometry

Use 1px to 2px line work with crisp edges. Prefer:

- line grids
- circles
- bars
- orbit tracks
- symmetrical dividers

Avoid:

- heavy glass cards
- thick blobs
- large soft gradients
- dashboard-style chart blocks

### Limited palette

Keep the core palette narrow:

- background: `#061127`
- deep panel: `#081630`
- cyan vector: `#00f0ff`
- green active: `#7cffb2`
- magenta event: `#ff3ed2`
- yellow caution: `#ffd700`

Color assignments:

- cyan: structure, vector lines, baseline system graphics
- green: active or healthy signal
- magenta: event or route emphasis
- yellow: caution, locked gate, or transitional state

### Motion through geometry

Prefer machine motion over UI flourish:

- rotating sweep
- pulsing center node
- orbit drift
- narrow control bars
- subtle scanline movement if performance allows

Avoid large card transitions and decorative bounce.

## Screen Rules

### Home

Purpose:

- mission control
- next step
- system readiness

Rules:

- mission board is the highest-weight panel
- machine state uses compact signal badges
- console feedback must look alive
- any decorative graphic stays secondary to the recorder and route state

### Profile

Purpose:

- equip connectors and modules

Rules:

- compact rows
- low panel count
- no decorative clutter
- equipment state should read like a clean setup console, not a settings form

### Scanner

Purpose:

- one strong center visual plus a route list and explanation

Rules:

- the radial scanner is the focal point
- candidate list is secondary
- route explanation is tertiary
- the scanner graphic must stay truthful to available data

Current v1 signals:

- signals found
- routes ready
- top net edge
- focused strategy label

### Practice

Purpose:

- turn routes into score updates

Rules:

- recent practice result is the primary card
- run history is secondary
- future graphic work should use route bars, not traditional PnL charts

### Score

Purpose:

- show paper progress, not a fake finance dashboard

Rules:

- practice score stays primary
- live score remains visually present but inactive
- a later pass should add a score-ring or probability meter instead of line charts

### Live Gate

Purpose:

- communicate caution and eligibility

Rules:

- warning state uses yellow accents
- acknowledgements and checklists stay plain-language
- avoid hype or high-energy visuals here

## Components

### Signal badges

Compact state chips for:

- practice mode
- live gate
- lab

### Status tiles

Three compact machine-readout tiles for:

- recorder
- scanner
- route

### Arcade scanner widget

The reusable focal component introduced in v1:

- radial burst field
- center node
- sweep line
- orbiting dots
- control stripe
- scanline overlay

This is the baseline visual language for future machine graphics in the app.

## Interaction Language

Buttons should behave like a cabinet control panel:

- one primary action per row
- secondary outline buttons for support actions
- locked actions look clearly unavailable

State language should stay literal:

- `Practice mode active`
- `Live gate locked`
- `Scanner standby`
- `Routes found`

Avoid abstract product-market copy in the EXE.

## Implementation Guidance

### Desktop app

Use `QPainter` for machine visuals rather than layering more static panels. Keep:

- one major animated graphic per screen
- subtle animation timers
- deterministic visual states based on real app data

### Site

The site should borrow the same geometry system:

- central radial composition
- thin vector lines
- arcade control bars
- restrained scanline treatment

The site should not become a dashboard.

## Acceptance Bar

The graphics system is working when:

- each screen has an obvious focal point
- active state feels machine-driven
- the app reads as a coherent arcade system
- visuals support the product loop instead of distracting from it
- the EXE looks authored, not themed

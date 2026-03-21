# Design System - Superior

## Product Context
- **Canonical product spec:** `docs/sup-v1-consumer-spec.md`
- **What this is:** Superior is a Windows-first prediction-market practice product with a public site, installer flow, docs, and a desktop app for paper-first learning. It teaches timing and workflow before live risk.
- **Who it's for:** Curious retail users, early traders, and market learners who want structure, not hype.
- **Space/industry:** Prediction markets, retail trading, paper trading, and market education.
- **Project type:** Hybrid marketing site, installer/docs surface, and product shell.

## Aesthetic Direction
- **Direction:** SNES Vector Cabinet
- **Decoration level:** expressive, but controlled
- **Mood:** It should feel like an official late-16-bit machine: cartridge-era window frames, hard-edged control hardware, and a black vector playfield with bright phosphor geometry. Not cyberpunk, not fintech-minimal, not novelty pixel cosplay.
- **Reference systems:** SNES menu and HUD windowing, F-Zero / Super Mario Kart Mode 7 depth cues, Super Metroid-style framed overlays, Atari vector arcade linework from Battlezone, Tempest, and Star Wars.

## Why This Direction
- The product already has a strong pixel logo. The mistake was surrounding it with modern product UI.
- SNES-era interfaces and vector-arcade screens are both highly artificial, highly readable, and mechanically disciplined.
- The right blend is not fifty-fifty. The shell, frames, buttons, and screen furniture come from SNES-era raster UI. The lane, targets, grids, and motion come from vector-arcade phosphor graphics.
- This gives Superior a specific historical grammar instead of vague "retro tech."

## Historical Rules
- **SNES shell:** 8px / 16px tile logic, framed windows, stepped corners, inset panels, palette ramps, chunkier separators, dither fills, and beveled hardware controls.
- **Vector playfield:** black space, sparse luminous lines, reticles, wireframe depth cues, horizon or tunnel geometry, and phosphor-like persistence.
- **Do not mix the rendering logic incorrectly:** the playfield should not use fake scanlines like a raster CRT, and the shell should not look like neon vector wireframes.

## Core Principles
- One dominant silhouette: a dedicated machine, not a web page made of cards.
- The logo is allowed to be rich and decorative. The UI must support it with historically grounded structure.
- The main screen should behave like a cartridge-era action panel: header rail, dominant playfield, physical control deck.
- Secondary routes should read as alternate machine modes, not separate layout families.
- Every visual flourish must belong to either SNES window grammar or vector-arcade grammar. If it belongs to neither, remove it.
- Do not let the design explain its own references on-screen. No labels like `field vector`, `shell snes`, `design consultation`, or other meta commentary inside the visual.

## Typography
- **Primary UI label font:** self-hosted bitmap font preferred; fallback **Silkscreen**. Use for tabs, button labels, readout labels, route labels, and frame annotations.
- **Display/readout font:** **Oxanium**. Use for short major labels, numeric readouts, and compact feature headings when bitmap text would be too rigid.
- **Body/data font:** **Space Mono**. Use for short paragraphs, specs, docs copy, timestamps, and structured explanatory text.
- **Accent font:** **Press Start 2P** only for the rarest brand lockups or commemorative labels. Never use it for nav, dense UI, or body copy.
- **Scale:** 8px, 10px, 12px, 16px, 24px, 32px, 48px. Snap everything to this cadence.
- **Lettercase:** labels mostly uppercase; body copy sentence case; big hero-style title sentences are discouraged.

## Color
- **Approach:** expressive but limited
- **Backdrop black:** `#04060A`
- **Shell navy:** `#11192B`
- **Inner frame indigo:** `#232A57`
- **Panel steel:** `#1E2438`
- **Raster highlight:** `#E7ECF5`
- **Vector cyan:** `#4CE7FF`
- **Vector green:** `#7DFF9B`
- **Vector magenta:** `#FF4FD8`
- **Commit gold:** `#FFD34D`
- **Warning red:** `#FF6B6B`
- **Muted line:** `#4D5674`
- **Palette behavior:** use obvious ramps, not subtle gradients. If a surface needs depth, build it from stepped shades or banded fills.

## Spacing
- **Base unit:** 8px
- **Density:** compact and mechanical
- **Scale:** 4, 8, 16, 24, 32, 48, 64
- **Grid behavior:** anchor frames, borders, button heights, lane markers, and module widths to 8px increments. Avoid fluid "designerly" whitespace.

## Layout
- **Approach:** screen-first, cartridge-era framing
- **Grid:** desktop shells should still use a modern responsive grid under the hood, but visible composition should feel like fixed machine zones rather than loose web sections
- **Max content width:** 1024px for the machine shell, with internal zones sized in 8px or 16px steps
- **Border radius:** `0px` by default
- **Corners:** use stepped pixel corners or clipped frame motifs instead of rounded corners
- **Preferred route structure:** top rail / dominant screen / control deck / alternate mode strip

## Surface Rules
- No glassmorphism, blur, or soft modern glow.
- No modern pill-chip UI as a default pattern.
- No smooth SaaS shadows. Use inset borders, bevels, and stepped shade bands.
- No generic feature-card grids.
- No oversized hero copy floating beside the product.
- Use dither textures, scan-converted fills, and tile-like patterning sparingly on the raster shell only.
- Use emptiness aggressively on the vector playfield. Black space is part of the design.
- Avoid fake-retro clutter: too many small labels, too many framed boxes, and too much decorative explanation all read as generated HTML rather than a believable screen.

## Button and Control Rules
- Buttons should feel like molded plastic console controls, not website CTAs.
- Use 2-tone or 3-tone stepped fills and hard borders for depth.
- Press states should visibly drop or inset by 1-2px.
- `START / STEP / HOLD TO COMMIT / RESET` should feel like hardware controls.
- Utility links like docs, source, release notes, and download mirrors should look secondary and frame-mounted, never like primary call-to-action buttons.

## Playfield Rules
- Use vector-style single or dual-color linework on deep black.
- Reticles, anchor lines, horizon grids, tunnels, or scope brackets are preferred over filled charts.
- Avoid busy data viz. The playfield should be sparse, legible, and target-like.
- No fake area charts, glossy bars, or rounded metric widgets.
- If a perspective surface is used, it should feel Mode 7 or wireframe, not CSS-isometric.

## Motion
- **Approach:** expressive but era-bound
- **Allowed motion:** cursor blink, stepped reticle sweep, phosphor persistence, mode-select flicker, wireframe travel, small hardware button depressions
- **Timing:** fast and snappy, often with `steps()` or discrete state changes rather than buttery interpolation
- **Avoid:** parallax marketing motion, drifting cards, soft easing spectacle, and fake neon pulsing
- **Important:** vector-style motion should feel beam-drawn and sparse; raster shell motion should feel stepwise and tile-based

## Copy Tone
- Keep labels short, mechanical, and specific: `paper`, `scan`, `commit`, `install`, `route`, `replay`, `locked`.
- Avoid startup or corporate filler completely.
- Avoid roleplay nouns like `mission board`, `hangar`, and `loadout` unless they are historically grounded and visually earned.
- Do not narrate what the user can plainly see.

## Safe Choices
- Dominant black playfield with cyan and green vector traces.
- SNES-style window frames and bevel logic around the shell.
- Bitmap labels plus a squarer techno display face for readouts.

## Deliberate Risks
- Blend two real historical grammars instead of flattening into generic retro.
- Let the screen be darker and emptier than modern web norms.
- Prefer awkward, chunky authenticity over polished generic balance.

## Research Notes
- SNES graphics were tile- and palette-driven, with the common NTSC resolution at `256x224`, limited palette groups, and a strong relationship between backgrounds, sprites, and palette assignment. Sources: SNESdev palette docs and Mega Cat's Super Nintendo graphics guide.
- Mode 7 mattered because it created depth by rotating and scaling a background layer scanline-by-scanline, which is why horizon planes and pseudo-3D track surfaces feel more authentic than generic CSS depth effects. Source: Mode 7 references and SNES graphics documentation.
- Vector arcade graphics were distinctive because they were bright, crisp, sparse line drawings on black, with games like Battlezone and Tempest using wireframe geometry and luminous monitors to create a unique feel. Sources: The Strong National Museum of Play and Battlezone history.

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-18 | Initial design system created | First pass established a restrained machine-shell direction. |
| 2026-03-19 | Design system rewritten as SNES Vector Cabinet | The first preview skewed too corporate; this revision grounds the product in actual SNES window grammar plus vector-arcade playfield logic. |

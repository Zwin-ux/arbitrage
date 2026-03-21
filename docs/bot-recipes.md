# Bot Recipes

Superior keeps bot recipes intentionally small and explicit.

## Why recipes exist

Starter bots are still shipped from code, but the desktop app now treats them as explicit recipe objects so a user can fork them locally without opening up a scripting system.

That gives the product a safe starter-bot workflow:

- starter recipes stay deterministic
- local forks stay profile-owned
- the practice engine arms from recipes, not just hardcoded blueprints
- future export and sharing work has a stable format to build on

## Recipe fields

Each recipe currently tracks:

- `label`
- `description`
- `strategy_family`
- `min_net_edge_bps`
- `target_stake_cents`
- `max_assignments`
- `route_preference`
- `lab_only`
- `enabled`
- `source_kind`
- `source_recipe_id`
- `source_blueprint_id`

The format is deliberately not a DSL. It only captures the safe configuration levers the product already exposes.

## Storage model

- starter recipes are generated from code at runtime
- local forks are stored as JSON beside the profile data directory
- secrets never enter the recipe file
- live execution settings do not live in recipes

Current local file:

- `bot_recipes.json` inside the selected profile data directory

## Forking behavior

Forking a recipe:

- duplicates the current recipe shape
- assigns a new local recipe id
- keeps provenance through `source_recipe_id` and `source_blueprint_id`
- gives the fork a new local label such as `Scout Bot Mk II`

This is meant for safe local iteration, not for arbitrary code execution.

## v1 boundaries

- no recipe scripting
- no custom Python hooks
- no opaque ranking rules
- no recipe can bypass risk caps or the practice-first posture

## Follow-up

Good next layers on top of this format:

- editable recipe fields in the bot library UI
- recipe export/import
- signed starter packs
- more explicit arm/disable ordering controls

# Prompt Stacking Guide

## Default stack for any serious Codex session

Paste these in this order:

1. `prompts/00_master_north_star.md`
2. one specific workstream prompt
3. optionally `REPO_UNDERSTANDING_MEMO.md`
4. finish with `prompts/23_final_polish_pass.md`

## Recommended stacks

### Architecture / cleanup
- `prompts/00_master_north_star.md`
- `prompts/01_repo_audit_and_plan.md`
- `prompts/03_consolidate_duplicate_ui_primitives.md`

### Desktop shell upgrade
- `prompts/00_master_north_star.md`
- `prompts/04_shell_navigation_and_state_overlays.md`
- `prompts/05_theme_tokens_polybius_arcade.md`
- `prompts/06_hangar_mission_control_rebuild.md`

### Bot bay / score attack
- `prompts/00_master_north_star.md`
- `prompts/07_loadout_to_bot_bay.md`
- `prompts/09_paper_runs_score_attack.md`
- `prompts/15_paper_execution_decision_trace.md`

### Replay / bot studio
- `prompts/00_master_north_star.md`
- `prompts/11_replay_lab_foundation.md`
- `prompts/12_bot_garage_and_registry.md`
- `prompts/13_bot_recipe_format_and_forking.md`

### Mac PoC
- `prompts/00_master_north_star.md`
- `prompts/20_macos_poc_cross_platform_qt.md`
- `prompts/21_macos_packaging_and_launchagent.md`
- `prompts/22_ci_matrix_and_release_pipeline.md`

## Rules for chaining

- Do not paste five huge prompts at once unless you want a broad plan rather than a clean implementation.
- Use one architectural prompt or one screen prompt at a time for the highest quality patches.
- When a prompt says “do not rewrite everything”, respect it.
- Keep the repo in a releasable state after each prompt if possible.

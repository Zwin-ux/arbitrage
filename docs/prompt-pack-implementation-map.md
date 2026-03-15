# Superior Prompt Pack Implementation Map

This repository now includes the extracted `superior_codex_prompt_pack_pro` under:

- [`docs/reference/superior_codex_prompt_pack_pro`](reference/superior_codex_prompt_pack_pro)

The pack is an implementation kit, not a source drop. Most of the files are repo-aware prompts, sequencing guides, and scaffolding notes. The only directly reusable starter assets were the macOS proof-of-concept templates, which are now staged under:

- [`packaging/macos_poc`](../packaging/macos_poc)

## What Was Imported

- Full prompt pack reference bundle
- Prompt index, repo memo, simulation checklist, and session bundles
- Bonus issue-board seed docs
- Bonus macOS packaging starter files

## Current Adoption Status

Integrated or substantially represented in the current repo:

- `00_master_north_star`
- `05_theme_tokens_polybius_arcade`
- `06_hangar_mission_control_rebuild`
- `07_loadout_to_bot_bay`
- `09_paper_runs_score_attack`
- `10_live_gate_and_experimental_live`
- `17_qa_client_scenarios_and_artifacts`
- `18_site_brand_refresh_and_variant_lab`
- `19_windows_release_polish`
- `24_docs_and_first_run_rewrite`

Partially implemented and good candidates for the next cleanup pass:

- `02_brand_and_naming_unification`
- `03_consolidate_duplicate_ui_primitives`
- `04_shell_navigation_and_state_overlays`
- `08_scanner_centerpiece_and_truthful_visualization`
- `16_assistant_guardrails_and_learn_tab`
- `22_ci_matrix_and_release_pipeline`
- `23_final_polish_pass`
- `25_performance_accessibility_and_responsiveness`

Still mostly future-facing:

- `11_replay_lab_foundation`
- `12_bot_garage_and_registry`
- `13_bot_recipe_format_and_forking`
- `14_opportunity_engine_v2`
- `15_paper_execution_decision_trace`
- `20_macos_poc_cross_platform_qt`
- `21_macos_packaging_and_launchagent`
- `26_one_shot_full_transform`

## Recommended Execution Order From Here

For the next high-value implementation cycle, use this order:

1. `session_bundles/02_arcade_shell.md`
2. `prompts/03_consolidate_duplicate_ui_primitives.md`
3. `prompts/08_scanner_centerpiece_and_truthful_visualization.md`
4. `prompts/12_bot_garage_and_registry.md`
5. `prompts/15_paper_execution_decision_trace.md`
6. `session_bundles/05_release_candidate.md`

## Repo Mapping

The prompt pack maps cleanly onto these active repo surfaces:

- Desktop shell and theme:
  [`src/market_data_recorder_desktop/window.py`](../src/market_data_recorder_desktop/window.py),
  [`src/market_data_recorder_desktop/ui`](../src/market_data_recorder_desktop/ui)
- Score-attack engine and bot simulation:
  [`src/market_data_recorder_desktop/score_attack.py`](../src/market_data_recorder_desktop/score_attack.py),
  [`src/market_data_recorder_desktop/bot_services.py`](../src/market_data_recorder_desktop/bot_services.py)
- QA and release lane:
  [`src/market_data_recorder_desktop/qa_client.py`](../src/market_data_recorder_desktop/qa_client.py),
  [`scripts/build-windows-release.ps1`](../scripts/build-windows-release.ps1)
- Site and brand surface:
  [`site/src/components/landing`](../site/src/components/landing),
  [`site/src/data/landingVariants.js`](../site/src/data/landingVariants.js)

## Notes

- Treat the prompt pack as a planning and refinement tool, not as a replacement for the current repo architecture.
- Keep the repo trust posture intact: paper-first, local-first, no profit guarantees, live locked by default.
- The macOS starter files are intentionally isolated in `packaging/macos_poc` until a real cross-platform release lane is approved.

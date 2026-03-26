import type { BotComparisonResult, OpportunityWindow, PackMode, ProgressSnapshot, RunRecord, Tape } from "@domain/types";
import { findPrimaryOpportunityEvent, buildBotComparisonResults } from "@services/botComparisonService";
import { listPacks, listTapes, listTapesForPack } from "@services/datasetLoader";
import { PRACTICE_STAKE, STARTING_BANKROLL } from "@services/practiceMoney";
import { createInitialProgress, recordRun } from "@services/progressService";
import { RunEngine } from "@services/runEngine";

export type HeadlessScenario = "ideal" | "early" | "late" | "miss" | "off_target";

export interface HeadlessSimulation {
  tape: Tape;
  scenario: HeadlessScenario;
  run: RunRecord;
}

export interface HeadlessCampaign {
  runs: RunRecord[];
  progress: ProgressSnapshot;
}

export function simulateTapeScenario(
  tape: Tape,
  scenario: HeadlessScenario,
  startingBankroll = STARTING_BANKROLL,
): HeadlessSimulation {
  const engine = new RunEngine();
  const event = findPrimaryOpportunityEvent(tape);

  if (!event?.window || !event.routeSnapshot) {
    return {
      tape,
      scenario,
      run: engine.finalizeBlocked(tape, event?.t ?? 0, "headless tape missing a valid primary opportunity", startingBankroll),
    };
  }

  engine.transition("arm", 0, "headless start");
  engine.transition("run", Math.max(0, event.window.opensAt - event.window.holdMs), "headless motion");
  engine.transition("pressure", event.window.opensAt, "headless window");

  const commitAt = resolveCommitAt(event.window, scenario);
  const focusScore = scenario === "off_target" ? 0.18 : 1;

  if (commitAt !== null) {
    engine.transition("commit_hold", commitAt, "headless hold");
    engine.markCommit(commitAt);
  }

  const resolvedAt = commitAt ?? event.window.closesAt;
  engine.transition("resolution", resolvedAt, "headless resolve");
  engine.transition("afterimage", resolvedAt + 1, "headless freeze");

  return {
    tape,
    scenario,
    run: engine.finalize(tape, event, startingBankroll, PRACTICE_STAKE, focusScore),
  };
}

export function runPackSweep(mode: PackMode): HeadlessCampaign {
  let progress = createInitialProgress();
  const runs: RunRecord[] = [];

  for (const pack of listPacks(mode)) {
    for (const tape of listTapesForPack(pack.id)) {
      const simulation = simulateTapeScenario(tape, "ideal", progress.practiceBankroll);
      runs.push(simulation.run);
      progress = recordRun(progress, simulation.run);
    }
  }

  return { runs, progress };
}

export function runUnlockCampaign(): HeadlessCampaign {
  let progress = createInitialProgress();
  const runs: RunRecord[] = [];

  for (const mode of ["tutorial", "replay"] as const) {
    for (const tape of listTapes(mode)) {
      const simulation = simulateTapeScenario(tape, "ideal", progress.practiceBankroll);
      runs.push(simulation.run);
      progress = recordRun(progress, simulation.run);
    }
  }

  return { runs, progress };
}

export function buildHeadlessBotMatrix(): Array<{ tapeId: string; verdicts: BotComparisonResult[] }> {
  return [...listTapes("tutorial"), ...listTapes("replay")].map((tape) => ({
    tapeId: tape.id,
    verdicts: buildBotComparisonResults(tape),
  }));
}

function resolveCommitAt(window: OpportunityWindow, scenario: HeadlessScenario) {
  switch (scenario) {
    case "ideal":
      return window.idealCommitAt;
    case "early":
      return window.opensAt - 1;
    case "late":
      return window.closesAt + 1;
    case "off_target":
      return window.idealCommitAt;
    case "miss":
      return null;
  }
}

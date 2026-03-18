import type { LiveGate, ProgressSnapshot, RunRecord, UnlockRequirement } from "@domain/types";
import { STARTING_BANKROLL } from "@services/practiceMoney";

const TUTORIAL_CLEAR_TARGET = 1;
const REPLAY_CLEAR_TARGET = 1;
const CONSISTENCY_TARGET = 65;

export function createInitialProgress(): ProgressSnapshot {
  return rehydrateProgressSnapshot("tutorial", []);
}

export function recordRun(progress: ProgressSnapshot, run: RunRecord): ProgressSnapshot {
  const recentRuns = [run, ...progress.recentRuns].slice(0, 24);
  const tutorialClearedTapeIds = run.mode === "tutorial" && run.outcome.success
    ? appendUnique(progress.tutorialClearedTapeIds, run.tapeId)
    : progress.tutorialClearedTapeIds;
  const replayClearedTapeIds = run.mode === "replay" && run.outcome.success
    ? appendUnique(progress.replayClearedTapeIds, run.tapeId)
    : progress.replayClearedTapeIds;

  return {
    ...rehydrateProgressSnapshot(progress.lastSelectedMode, recentRuns),
    practiceBankroll: run.receipt.endingBankroll,
    bestBankroll: Math.max(progress.bestBankroll, run.receipt.endingBankroll),
    clearStreak: run.outcome.success ? progress.clearStreak + 1 : 0,
    tutorialClearedTapeIds,
    replayClearedTapeIds,
  };
}

export function rehydrateProgressSnapshot(
  lastSelectedMode: ProgressSnapshot["lastSelectedMode"],
  recentRuns: RunRecord[],
): ProgressSnapshot {
  const successfulRuns = recentRuns.filter((entry) => entry.outcome.success).length;
  const consistencyScore = computeConsistencyScore(recentRuns);
  const tutorialClearedTapeIds = uniqueTapeIds(recentRuns, "tutorial");
  const replayClearedTapeIds = uniqueTapeIds(recentRuns, "replay");
  const tutorialClears = tutorialClearedTapeIds.length;
  const replayClears = replayClearedTapeIds.length;

  return {
    lastSelectedMode,
    recentRuns,
    practiceBankroll: recentRuns[0]?.receipt.endingBankroll ?? STARTING_BANKROLL,
    bestBankroll: Math.max(STARTING_BANKROLL, ...recentRuns.map((entry) => entry.receipt.endingBankroll)),
    clearStreak: computeClearStreak(recentRuns),
    tutorialClearedTapeIds,
    replayClearedTapeIds,
    liveGate: buildLiveGate(successfulRuns, consistencyScore, tutorialClears, replayClears),
  };
}

function computeConsistencyScore(runs: RunRecord[]): number {
  if (runs.length === 0) {
    return 0;
  }
  const clearRuns = runs.filter((entry) => entry.outcome.grade === "clear").length;
  return Math.round((clearRuns / runs.length) * 100);
}

function uniqueTapeIds(runs: RunRecord[], mode: RunRecord["mode"]): string[] {
  return Array.from(
    new Set(
      runs
        .filter((entry) => entry.mode === mode && entry.outcome.success)
        .map((entry) => entry.tapeId),
    ),
  );
}

function computeClearStreak(runs: RunRecord[]): number {
  let streak = 0;
  for (const run of runs) {
    if (!run.outcome.success) {
      break;
    }
    streak += 1;
  }
  return streak;
}

function appendUnique(values: string[], nextValue: string): string[] {
  return values.includes(nextValue) ? values : [...values, nextValue];
}

function buildLiveGate(
  successfulRuns: number,
  consistencyScore: number,
  tutorialClears: number,
  replayClears: number,
): LiveGate {
  const unlockRequirements: UnlockRequirement[] = [
    makeRequirement("tutorial clears", TUTORIAL_CLEAR_TARGET, tutorialClears),
    makeRequirement("replay clears", REPLAY_CLEAR_TARGET, replayClears),
    makeRequirement("consistency score", CONSISTENCY_TARGET, consistencyScore),
  ];
  return {
    unlocked: unlockRequirements.every((item) => item.satisfied),
    successfulRuns,
    consistencyScore,
    tutorialClears,
    replayClears,
    unlockRequirements,
  };
}

function makeRequirement(label: string, target: number, current: number): UnlockRequirement {
  return {
    label,
    target,
    current,
    satisfied: current >= target,
  };
}

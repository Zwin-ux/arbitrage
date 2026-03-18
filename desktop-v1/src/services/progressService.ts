import type { LiveGate, ProgressSnapshot, RunRecord, UnlockRequirement } from "@domain/types";

const TUTORIAL_CLEAR_TARGET = 1;
const REPLAY_CLEAR_TARGET = 1;
const CONSISTENCY_TARGET = 65;

export function createInitialProgress(): ProgressSnapshot {
  return rehydrateProgressSnapshot("tutorial", []);
}

export function recordRun(progress: ProgressSnapshot, run: RunRecord): ProgressSnapshot {
  return rehydrateProgressSnapshot(progress.lastSelectedMode, [run, ...progress.recentRuns].slice(0, 24));
}

export function rehydrateProgressSnapshot(
  lastSelectedMode: ProgressSnapshot["lastSelectedMode"],
  recentRuns: RunRecord[],
): ProgressSnapshot {
  const successfulRuns = recentRuns.filter((entry) => entry.outcome.success).length;
  const consistencyScore = computeConsistencyScore(recentRuns);
  const tutorialClears = countUniqueClears(recentRuns, "tutorial");
  const replayClears = countUniqueClears(recentRuns, "replay");

  return {
    lastSelectedMode,
    recentRuns,
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

function countUniqueClears(runs: RunRecord[], mode: RunRecord["mode"]): number {
  return new Set(
    runs
      .filter((entry) => entry.mode === mode && entry.outcome.success)
      .map((entry) => entry.tapeId),
  ).size;
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

import type { LiveGate, ProgressSnapshot, RunRecord, UnlockRequirement } from "@domain/types";

const SUCCESS_TARGET = 8;
const CONSISTENCY_TARGET = 72;

export function createInitialProgress(): ProgressSnapshot {
  return {
    lastSelectedMode: "tutorial",
    recentRuns: [],
    liveGate: buildLiveGate(0, 0),
  };
}

export function recordRun(progress: ProgressSnapshot, run: RunRecord): ProgressSnapshot {
  const recentRuns = [run, ...progress.recentRuns].slice(0, 24);
  const successfulRuns = recentRuns.filter((entry) => entry.outcome.success).length;
  const consistencyScore = computeConsistencyScore(recentRuns);

  return {
    ...progress,
    recentRuns,
    liveGate: buildLiveGate(successfulRuns, consistencyScore),
  };
}

function computeConsistencyScore(runs: RunRecord[]): number {
  if (runs.length === 0) {
    return 0;
  }
  const clearRuns = runs.filter((entry) => entry.outcome.grade === "clear").length;
  return Math.round((clearRuns / runs.length) * 100);
}

function buildLiveGate(successfulRuns: number, consistencyScore: number): LiveGate {
  const unlockRequirements: UnlockRequirement[] = [
    makeRequirement("successful runs", SUCCESS_TARGET, successfulRuns),
    makeRequirement("consistency score", CONSISTENCY_TARGET, consistencyScore),
  ];
  return {
    unlocked: unlockRequirements.every((item) => item.satisfied),
    successfulRuns,
    consistencyScore,
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

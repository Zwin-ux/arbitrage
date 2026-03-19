import type { LiveGate, PackMode, PackProgress, PackStatus, ProgressSnapshot, RunRecord, TapeMode, UnlockRequirement } from "@domain/types";
import { STARTING_BANKROLL } from "@services/practiceMoney";
import { getFirstPackId, getPackById, listPackManifest } from "@services/packManifest";

const TUTORIAL_CLEAR_TARGET = 1;
const REPLAY_CLEAR_TARGET = 1;
const CONSISTENCY_TARGET = 65;

export function createInitialProgress(): ProgressSnapshot {
  return rehydrateProgressSnapshot("tutorial", [], getFirstPackId("tutorial"));
}

export function recordRun(progress: ProgressSnapshot, run: RunRecord): ProgressSnapshot {
  const recentRuns = [run, ...progress.recentRuns].slice(0, 24);
  return rehydrateProgressSnapshot(progress.lastSelectedMode, recentRuns, progress.lastSelectedPackId);
}

export function rehydrateProgressSnapshot(
  lastSelectedMode: ProgressSnapshot["lastSelectedMode"],
  recentRuns: RunRecord[],
  lastSelectedPackId: string | null = getFirstPackId(lastSelectedMode),
): ProgressSnapshot {
  const successfulRuns = recentRuns.filter((entry) => entry.outcome.success).length;
  const consistencyScore = computeConsistencyScore(recentRuns);
  const tutorialClearedTapeIds = uniqueTapeIds(recentRuns, "tutorial");
  const replayClearedTapeIds = uniqueTapeIds(recentRuns, "replay");
  const tutorialClears = tutorialClearedTapeIds.length;
  const replayClears = replayClearedTapeIds.length;
  const packProgress = buildPackProgress(recentRuns);
  const liveGate = buildLiveGate(successfulRuns, consistencyScore, tutorialClears, replayClears);
  const resolvedMode = resolveMode(lastSelectedMode, packProgress, liveGate.unlocked);
  const resolvedPackId = resolvePackId(resolvedMode, lastSelectedPackId, packProgress);

  return {
    lastSelectedMode: resolvedMode,
    lastSelectedPackId: resolvedPackId,
    recentRuns,
    practiceBankroll: recentRuns[0]?.receipt.endingBankroll ?? STARTING_BANKROLL,
    bestBankroll: Math.max(STARTING_BANKROLL, ...recentRuns.map((entry) => entry.receipt.endingBankroll)),
    clearStreak: computeClearStreak(recentRuns),
    tutorialClearedTapeIds,
    replayClearedTapeIds,
    packProgress,
    liveGate,
  };
}

export function listPackStatuses(progress: ProgressSnapshot, mode: PackMode): PackStatus[] {
  const progressByPackId = new Map(progress.packProgress.map((entry) => [entry.packId, entry]));

  return listPackManifest(mode).map((pack) => {
    const entry = progressByPackId.get(pack.id) ?? createEmptyPackProgress(pack.id);
    return {
      pack,
      unlocked: isPackUnlocked(pack.id, progressByPackId),
      completed: entry.completed,
      clearedCount: entry.clearedTapeIds.length,
      totalCount: pack.tapeIds.length,
      bestNetPnl: entry.bestNetPnl,
    };
  });
}

export function canEnterMode(progress: ProgressSnapshot, mode: TapeMode): boolean {
  if (mode === "tutorial") {
    return true;
  }
  if (mode === "replay") {
    return listPackStatuses(progress, "replay").some((pack) => pack.unlocked);
  }
  return progress.liveGate.unlocked;
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

function buildPackProgress(runs: RunRecord[]): PackProgress[] {
  return listPackManifest().map((pack) => {
    const packRuns = runs.filter((entry) => pack.tapeIds.includes(entry.tapeId));
    const clearedTapeIds = Array.from(
      new Set(
        packRuns
          .filter((entry) => entry.outcome.success)
          .map((entry) => entry.tapeId),
      ),
    );

    return {
      packId: pack.id,
      clearedTapeIds,
      completed: clearedTapeIds.length === pack.tapeIds.length && pack.tapeIds.length > 0,
      bestNetPnl: packRuns.length > 0 ? Math.max(...packRuns.map((entry) => entry.receipt.netPnl)) : 0,
    };
  });
}

function resolveMode(lastSelectedMode: TapeMode, packProgress: PackProgress[], liveUnlocked: boolean): TapeMode {
  if (lastSelectedMode === "live-preview") {
    return liveUnlocked ? "live-preview" : "tutorial";
  }

  if (lastSelectedMode === "replay" && !hasUnlockedPack("replay", packProgress)) {
    return "tutorial";
  }

  return lastSelectedMode;
}

function resolvePackId(mode: TapeMode, preferredPackId: string | null, packProgress: PackProgress[]): string | null {
  if (mode === "live-preview") {
    return null;
  }

  const preferredPack = preferredPackId ? getPackById(preferredPackId) : undefined;
  if (preferredPack && preferredPack.mode === mode && isPackUnlocked(preferredPack.id, createPackProgressMap(packProgress))) {
    return preferredPack.id;
  }

  const unlockedPack = listPackManifest(mode).find((pack) => isPackUnlocked(pack.id, createPackProgressMap(packProgress)));
  return unlockedPack?.id ?? getFirstPackId(mode);
}

function hasUnlockedPack(mode: PackMode, packProgress: PackProgress[]): boolean {
  const progressByPackId = createPackProgressMap(packProgress);
  return listPackManifest(mode).some((pack) => isPackUnlocked(pack.id, progressByPackId));
}

function isPackUnlocked(packId: string, progressByPackId: Map<string, PackProgress>): boolean {
  const pack = getPackById(packId);
  if (!pack) {
    return false;
  }
  if (pack.unlock.type === "free") {
    return true;
  }

  if (!pack.unlock.targetId) {
    return false;
  }

  return progressByPackId.get(pack.unlock.targetId)?.completed ?? false;
}

function createPackProgressMap(packProgress: PackProgress[]): Map<string, PackProgress> {
  return new Map(packProgress.map((entry) => [entry.packId, entry]));
}

function createEmptyPackProgress(packId: string): PackProgress {
  return {
    packId,
    clearedTapeIds: [],
    completed: false,
    bestNetPnl: 0,
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

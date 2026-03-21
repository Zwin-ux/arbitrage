import type {
  BotRuntime,
  DecisionAuditEvent,
  ExecutionPolicy,
  LiveGate,
  PackMode,
  PackProgress,
  PackStatus,
  ProgressSnapshot,
  RunRecord,
  ShellView,
  StarterBotProfile,
  TapeMode,
  UnlockRequirement,
} from "@domain/types";
import { STARTING_BANKROLL } from "@services/practiceMoney";
import { getFirstPackId, getPackById, listPackManifest } from "@services/packManifest";

const TUTORIAL_CLEAR_TARGET = 1;
const REPLAY_CLEAR_TARGET = 1;
const CONSISTENCY_TARGET = 65;
const MAX_AUDIT_EVENTS = 14;

export function createInitialProgress(): ProgressSnapshot {
  return rehydrateProgressSnapshot("tutorial", [], getFirstPackId("tutorial"));
}

export function recordRun(progress: ProgressSnapshot, run: RunRecord): ProgressSnapshot {
  const recentRuns = [run, ...progress.recentRuns].slice(0, 24);
  return rehydrateProgressSnapshot(progress.lastSelectedMode, recentRuns, progress.lastSelectedPackId, progress);
}

export function rehydrateProgressSnapshot(
  lastSelectedMode: ProgressSnapshot["lastSelectedMode"],
  recentRuns: RunRecord[],
  lastSelectedPackId: string | null = getFirstPackId(lastSelectedMode),
  previous?: Pick<
    ProgressSnapshot,
    "selectedView" | "starterBot" | "executionPolicy" | "botRuntime" | "decisionAudit"
  >,
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
  const selectedView = previous?.selectedView ?? "home";
  const starterBot = previous?.starterBot ?? createStarterBotProfile();
  const executionPolicy = previous?.executionPolicy ?? createExecutionPolicy();
  const botRuntime = buildBotRuntime(previous?.botRuntime, recentRuns, liveGate);
  const decisionAudit = appendRunAudit(previous?.decisionAudit ?? [], runAuditEvent(recentRuns[0], liveGate, botRuntime));

  return {
    lastSelectedMode: resolvedMode,
    lastSelectedPackId: resolvedPackId,
    selectedView,
    recentRuns,
    practiceBankroll: recentRuns[0]?.receipt.endingBankroll ?? STARTING_BANKROLL,
    bestBankroll: Math.max(STARTING_BANKROLL, ...recentRuns.map((entry) => entry.receipt.endingBankroll)),
    clearStreak: computeClearStreak(recentRuns),
    tutorialClearedTapeIds,
    replayClearedTapeIds,
    packProgress,
    liveGate,
    starterBot,
    executionPolicy,
    botRuntime,
    decisionAudit,
  };
}

export function createStarterBotProfile(): StarterBotProfile {
  return {
    id: "starter-bot-kalshi",
    label: "Kalshi Starter Bot",
    venue: "Kalshi",
    strategyFamily: "internal-binary",
    marketScope: "Curated liquid yes/no markets only",
    cadence: "Low-frequency, cap-first autopilot",
    perTradeCap: 10,
    dailyLossCap: 25,
    maxOpenPositions: 2,
  };
}

export function createExecutionPolicy(): ExecutionPolicy {
  return {
    staleDataWindowSeconds: 25,
    orderErrorLimit: 3,
    authFailureHalts: true,
    manualKillSwitch: true,
  };
}

export function setSelectedView(progress: ProgressSnapshot, selectedView: ShellView): ProgressSnapshot {
  return {
    ...progress,
    selectedView,
  };
}

export function armStarterBot(progress: ProgressSnapshot): ProgressSnapshot {
  if (!progress.liveGate.unlocked || progress.botRuntime.shadowRuns <= 0) {
    return progress;
  }
  return applyBotState(progress, "armed", "Starter bot armed. Auto stays capped until you turn it on.", null, "positive");
}

export function startStarterBot(progress: ProgressSnapshot): ProgressSnapshot {
  if (progress.botRuntime.phase !== "armed" && progress.botRuntime.phase !== "halted") {
    return progress;
  }
  return {
    ...applyBotState(progress, "auto_running", "Starter bot is running under the current caps.", null, "positive"),
    botRuntime: {
      ...progress.botRuntime,
      phase: "auto_running",
      autoRuns: progress.botRuntime.autoRuns + 1,
      haltReason: null,
      lastAction: "Auto running under tight caps.",
      lastEventAt: new Date().toISOString(),
    },
  };
}

export function haltStarterBot(progress: ProgressSnapshot, reason = "Manual halt"): ProgressSnapshot {
  return applyBotState(progress, "halted", `Bot halted: ${reason}.`, reason, "warning");
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

function buildBotRuntime(previous: BotRuntime | undefined, runs: RunRecord[], liveGate: LiveGate): BotRuntime {
  const successfulRuns = runs.filter((entry) => entry.outcome.success).length;
  const shadowRuns = runs.filter((entry) => entry.mode === "replay" && entry.outcome.success).length;
  const now = previous?.lastEventAt ?? null;

  if (successfulRuns === 0) {
    return {
      phase: "setup",
      shadowRuns,
      autoRuns: previous?.autoRuns ?? 0,
      haltReason: null,
      lastAction: "Run the guided trust ramp first.",
      lastEventAt: now,
    };
  }

  if (!liveGate.unlocked) {
    return {
      phase: "learn",
      shadowRuns,
      autoRuns: previous?.autoRuns ?? 0,
      haltReason: null,
      lastAction: "Clear learn and replay before auto can unlock.",
      lastEventAt: now,
    };
  }

  if (previous?.phase === "armed" || previous?.phase === "auto_running" || previous?.phase === "halted") {
    return {
      ...previous,
      shadowRuns,
    };
  }

  return {
    phase: "shadow",
    shadowRuns,
    autoRuns: previous?.autoRuns ?? 0,
    haltReason: null,
    lastAction: shadowRuns > 0 ? "Shadow check passed. Arm the bot when ready." : "Run one replay clear to complete the shadow check.",
    lastEventAt: now,
  };
}

function applyBotState(
  progress: ProgressSnapshot,
  phase: BotRuntime["phase"],
  title: string,
  haltReason: string | null,
  tone: DecisionAuditEvent["tone"],
): ProgressSnapshot {
  const createdAt = new Date().toISOString();
  return {
    ...progress,
    botRuntime: {
      ...progress.botRuntime,
      phase,
      haltReason,
      lastAction: title,
      lastEventAt: createdAt,
    },
    decisionAudit: appendRunAudit(progress.decisionAudit, {
      id: `audit-${createdAt}`,
      kind: phase === "auto_running" ? "auto" : "state",
      tone,
      title,
      detail: phase === "halted" ? "Auto is off until you re-arm the starter bot." : "The consumer shell keeps every bot state change visible.",
      createdAt,
    }),
  };
}

function appendRunAudit(audit: DecisionAuditEvent[], event: DecisionAuditEvent | null): DecisionAuditEvent[] {
  if (!event) {
    return audit;
  }
  return [event, ...audit].slice(0, MAX_AUDIT_EVENTS);
}

function runAuditEvent(run: RunRecord | undefined, liveGate: LiveGate, botRuntime: BotRuntime): DecisionAuditEvent | null {
  if (!run) {
    return null;
  }
  const createdAt = run.startTimestamp;
  const cleared = run.outcome.success ? "Cleared" : "Missed";
  const detail = liveGate.unlocked
    ? botRuntime.shadowRuns > 0
      ? "Shadow qualification is complete. The starter bot can be armed."
      : "Live is unlocked. Run one replay clear to finish the shadow check."
    : "Keep moving through the learn ladder before auto can unlock.";

  return {
    id: `audit-${run.id}`,
    kind: run.mode === "replay" ? "shadow" : "practice",
    tone: run.outcome.success ? "positive" : "warning",
    title: `${cleared} ${run.mode === "tutorial" ? "learn" : "replay"} run`,
    detail,
    createdAt,
  };
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

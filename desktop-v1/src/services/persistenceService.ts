import type {
  Debrief,
  LiveGate,
  PackProgress,
  PracticeMoneyReceipt,
  ProgressSnapshot,
  RunOutcome,
  RunRecord,
  TapeMode,
  UnlockRequirement,
} from "@domain/types";
import { createInitialProgress, rehydrateProgressSnapshot } from "@services/progressService";

const STORAGE_VERSION = 2;
const MODE_SET = new Set<TapeMode>(["tutorial", "replay", "live-preview"]);

interface ProgressEnvelopeV2 {
  version: typeof STORAGE_VERSION;
  snapshot: ProgressSnapshot;
}

interface StorageLike {
  getItem(key: string): string | null;
  setItem(key: string, value: string): void;
}

export interface ProgressStore {
  load(): ProgressSnapshot;
  save(snapshot: ProgressSnapshot): void;
}

export class LocalProgressStore implements ProgressStore {
  constructor(
    private readonly key = "sup-v1-progress",
    private readonly storage: StorageLike | undefined = typeof localStorage === "undefined" ? undefined : localStorage,
  ) {}

  load(): ProgressSnapshot {
    if (!this.storage) {
      return createInitialProgress();
    }

    const raw = this.storage.getItem(this.key);
    if (!raw) {
      return createInitialProgress();
    }

    try {
      const parsed = JSON.parse(raw) as unknown;
      if (isProgressEnvelopeV2(parsed)) {
        return parsed.snapshot;
      }
      const legacy = readLegacyProgressSnapshot(parsed);
      if (legacy) {
        return legacy;
      }
    } catch {
      return createInitialProgress();
    }

    return createInitialProgress();
  }

  save(snapshot: ProgressSnapshot): void {
    if (!this.storage) {
      return;
    }

    const payload: ProgressEnvelopeV2 = {
      version: STORAGE_VERSION,
      snapshot,
    };
    this.storage.setItem(this.key, JSON.stringify(payload));
  }
}

function isProgressEnvelopeV2(value: unknown): value is ProgressEnvelopeV2 {
  return isRecord(value) && value.version === STORAGE_VERSION && isProgressSnapshot(value.snapshot);
}

function isProgressSnapshot(value: unknown): value is ProgressSnapshot {
  return isRecord(value)
    && isTapeMode(value.lastSelectedMode)
    && (value.lastSelectedPackId === null || typeof value.lastSelectedPackId === "string")
    && Array.isArray(value.recentRuns)
    && value.recentRuns.every(isRunRecord)
    && typeof value.practiceBankroll === "number"
    && typeof value.bestBankroll === "number"
    && typeof value.clearStreak === "number"
    && Array.isArray(value.tutorialClearedTapeIds)
    && value.tutorialClearedTapeIds.every((item) => typeof item === "string")
    && Array.isArray(value.replayClearedTapeIds)
    && value.replayClearedTapeIds.every((item) => typeof item === "string")
    && Array.isArray(value.packProgress)
    && value.packProgress.every(isPackProgress)
    && isLiveGate(value.liveGate);
}

function readLegacyProgressSnapshot(value: unknown): ProgressSnapshot | null {
  if (!isRecord(value)) {
    return null;
  }

  if (value.version === 1 && isRecord(value.snapshot)) {
    return readLegacyProgressSnapshot(value.snapshot);
  }

  if (!isTapeMode(value.lastSelectedMode) || !Array.isArray(value.recentRuns)) {
    return null;
  }
  if (!value.recentRuns.every(isRunRecord)) {
    return null;
  }

  const lastSelectedPackId = typeof value.lastSelectedPackId === "string" ? value.lastSelectedPackId : null;
  return rehydrateProgressSnapshot(value.lastSelectedMode, value.recentRuns, lastSelectedPackId);
}

function isPackProgress(value: unknown): value is PackProgress {
  return isRecord(value)
    && typeof value.packId === "string"
    && Array.isArray(value.clearedTapeIds)
    && value.clearedTapeIds.every((item) => typeof item === "string")
    && typeof value.completed === "boolean"
    && typeof value.bestNetPnl === "number";
}

function isRunRecord(value: unknown): value is RunRecord {
  return isRecord(value)
    && typeof value.id === "string"
    && typeof value.tapeId === "string"
    && isTapeMode(value.mode)
    && typeof value.startTimestamp === "string"
    && Array.isArray(value.stateTransitions)
    && Array.isArray(value.userActionLog)
    && (value.commitTimestamp === null || typeof value.commitTimestamp === "number")
    && isRunOutcome(value.outcome)
    && isRecord(value.afterimage)
    && isPracticeMoneyReceipt(value.receipt)
    && isDebrief(value.debrief);
}

function isRunOutcome(value: unknown): value is RunOutcome {
  return isRecord(value)
    && typeof value.grade === "string"
    && typeof value.success === "boolean"
    && typeof value.committed === "boolean"
    && typeof value.reason === "string";
}

function isPracticeMoneyReceipt(value: unknown): value is PracticeMoneyReceipt {
  return isRecord(value)
    && typeof value.label === "string"
    && typeof value.tone === "string"
    && typeof value.startingBankroll === "number"
    && typeof value.stake === "number"
    && (value.entryPrice === null || typeof value.entryPrice === "number")
    && (value.exitPrice === null || typeof value.exitPrice === "number")
    && typeof value.grossPnl === "number"
    && typeof value.fees === "number"
    && typeof value.slippage === "number"
    && typeof value.netPnl === "number"
    && typeof value.endingBankroll === "number";
}

function isDebrief(value: unknown): value is Debrief {
  return isRecord(value)
    && typeof value.headline === "string"
    && Array.isArray(value.reasons)
    && value.reasons.every((item) => typeof item === "string")
    && isRecord(value.metrics)
    && typeof value.metrics.grossPnl === "number"
    && typeof value.metrics.netPnl === "number"
    && (value.metrics.commitOffsetMs === null || typeof value.metrics.commitOffsetMs === "number")
    && typeof value.recommendation === "string";
}

function isLiveGate(value: unknown): value is LiveGate {
  return isRecord(value)
    && typeof value.unlocked === "boolean"
    && typeof value.successfulRuns === "number"
    && typeof value.consistencyScore === "number"
    && typeof value.tutorialClears === "number"
    && typeof value.replayClears === "number"
    && Array.isArray(value.unlockRequirements)
    && value.unlockRequirements.every(isUnlockRequirement);
}

function isUnlockRequirement(value: unknown): value is UnlockRequirement {
  return isRecord(value)
    && typeof value.label === "string"
    && typeof value.target === "number"
    && typeof value.current === "number"
    && typeof value.satisfied === "boolean";
}

function isTapeMode(value: unknown): value is TapeMode {
  return typeof value === "string" && MODE_SET.has(value as TapeMode);
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

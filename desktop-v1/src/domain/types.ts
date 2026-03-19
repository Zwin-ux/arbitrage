export type TapeMode = "tutorial" | "replay" | "live-preview";
export type PackMode = Exclude<TapeMode, "live-preview">;
export type RunPhase =
  | "standby"
  | "arm"
  | "run"
  | "pressure"
  | "commit_hold"
  | "resolution"
  | "afterimage"
  | "reset";
export type EventType = "baseline" | "shift" | "window_open" | "window_close" | "route_snapshot" | "hazard";
export type Severity = "low" | "medium" | "high";
export type OutcomeGrade = "clear" | "early" | "late" | "miss" | "blocked";
export type BotPresetName = "Safe" | "Balanced" | "Aggressive";
export type SourceType = "bundled-tutorial" | "bundled-replay" | "live-preview";
export type PackUnlockType = "free" | "requires_pack_clear";

export interface TapeSource {
  type: SourceType;
  label: string;
  importedAt?: string;
}

export interface MarketMetadata {
  venue: "Polymarket";
  marketId: string;
  marketSlug: string;
  symbol: string;
  title: string;
}

export interface RouteSnapshot {
  grossEdgeBps: number;
  feesBps: number;
  slippageBps: number;
  netEdgeBps: number;
  path: string[];
  assumptions: string[];
  qualityBand: "weak" | "usable" | "clean";
}

export interface OpportunityWindow {
  opensAt: number;
  closesAt: number;
  idealCommitAt: number;
  holdMs: number;
  routeSnapshotId?: string;
}

export interface TapeEvent {
  id: string;
  t: number;
  value: number;
  volume: number;
  confidence: number;
  eventType: EventType;
  severity: Severity;
  label?: string;
  window?: OpportunityWindow;
  routeSnapshot?: RouteSnapshot;
}

export interface Tape {
  id: string;
  name: string;
  mode: TapeMode;
  source: TapeSource;
  market: MarketMetadata;
  timeRange: {
    start: string;
    end: string;
  };
  lane: {
    baseline: number;
    minValue: number;
    maxValue: number;
  };
  events: TapeEvent[];
}

export interface PackUnlockRule {
  type: PackUnlockType;
  targetId?: string;
}

export interface TapePack {
  id: string;
  mode: PackMode;
  name: string;
  order: number;
  label: string;
  tapeIds: string[];
  unlock: PackUnlockRule;
}

export interface PackProgress {
  packId: string;
  clearedTapeIds: string[];
  completed: boolean;
  bestNetPnl: number;
}

export interface PackStatus {
  pack: TapePack;
  unlocked: boolean;
  completed: boolean;
  clearedCount: number;
  totalCount: number;
  bestNetPnl: number;
}

export interface StateTransition {
  phase: RunPhase;
  at: number;
  reason: string;
}

export interface UserActionLogEntry {
  type: "start_run" | "step" | "hold_start" | "hold_cancel" | "commit" | "reset";
  at: number;
}

export interface DebriefMetrics {
  grossPnl: number;
  netPnl: number;
  commitOffsetMs: number | null;
}

export interface Debrief {
  headline: string;
  reasons: string[];
  metrics: DebriefMetrics;
  recommendation: string;
}

export interface PracticeMoneyReceipt {
  label: string;
  tone: "positive" | "negative" | "idle";
  startingBankroll: number;
  stake: number;
  entryPrice: number | null;
  exitPrice: number | null;
  grossPnl: number;
  fees: number;
  slippage: number;
  netPnl: number;
  endingBankroll: number;
}

export interface Afterimage {
  frozenAt: number;
  windowState: "open" | "closed" | "missed";
  commitState: "none" | "held" | "resolved";
}

export interface RunOutcome {
  grade: OutcomeGrade;
  success: boolean;
  committed: boolean;
  reason: string;
}

export interface RunRecord {
  id: string;
  tapeId: string;
  mode: TapeMode;
  startTimestamp: string;
  stateTransitions: StateTransition[];
  userActionLog: UserActionLogEntry[];
  commitTimestamp: number | null;
  outcome: RunOutcome;
  afterimage: Afterimage;
  receipt: PracticeMoneyReceipt;
  debrief: Debrief;
}

export interface BotComparisonResult {
  preset: BotPresetName;
  verdict: "clean" | "early" | "late" | "wait";
  reason: string;
  receipt: PracticeMoneyReceipt;
}

export interface BotPreset {
  name: BotPresetName;
  commitThresholdBps: number;
  patienceWindowMs: number;
  sensitivity: number;
  maxActionRate: number;
  label: string;
}

export interface UnlockRequirement {
  label: string;
  target: number;
  current: number;
  satisfied: boolean;
}

export interface LiveGate {
  unlocked: boolean;
  successfulRuns: number;
  consistencyScore: number;
  tutorialClears: number;
  replayClears: number;
  unlockRequirements: UnlockRequirement[];
}

export interface ProgressSnapshot {
  lastSelectedMode: TapeMode;
  lastSelectedPackId: string | null;
  recentRuns: RunRecord[];
  practiceBankroll: number;
  bestBankroll: number;
  clearStreak: number;
  tutorialClearedTapeIds: string[];
  replayClearedTapeIds: string[];
  packProgress: PackProgress[];
  liveGate: LiveGate;
}

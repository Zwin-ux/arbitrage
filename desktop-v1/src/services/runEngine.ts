import { canTransition } from "@domain/stateMachine";
import type {
  Afterimage,
  Debrief,
  RunOutcome,
  RunPhase,
  RunRecord,
  StateTransition,
  Tape,
  TapeEvent,
  UserActionLogEntry,
} from "@domain/types";
import type { FocusWindow } from "@shared/focusMechanics";
import { resolveCommitGrade } from "@shared/focusMechanics";
import { createPracticeMoneyReceipt, PRACTICE_STAKE, STARTING_BANKROLL } from "@services/practiceMoney";
import { createDebrief } from "@services/routeEvaluator";

export class RunEngine {
  private phase: RunPhase = "standby";
  private transitions: StateTransition[] = [{ phase: "standby", at: 0, reason: "boot" }];
  private actions: UserActionLogEntry[] = [];
  private commitTimestamp: number | null = null;

  getPhase(): RunPhase {
    return this.phase;
  }

  transition(to: RunPhase, at: number, reason: string): void {
    if (!canTransition(this.phase, to)) {
      throw new Error(`invalid transition ${this.phase} -> ${to}`);
    }
    this.phase = to;
    this.transitions.push({ phase: to, at, reason });
  }

  logAction(entry: UserActionLogEntry): void {
    this.actions.push(entry);
  }

  markCommit(at: number): void {
    this.commitTimestamp = at;
    this.actions.push({ type: "commit", at });
  }

  finalize(
    tape: Tape,
    event: TapeEvent,
    startingBankroll = STARTING_BANKROLL,
    stake = PRACTICE_STAKE,
    focusScore = 1,
  ): RunRecord {
    const snapshot = event.routeSnapshot;
    if (!snapshot || !event.window) {
      throw new Error("run resolution requires a route snapshot and window");
    }

    const commitOffset = this.commitTimestamp === null ? null : this.commitTimestamp - event.window.idealCommitAt;
    const outcome = resolveOutcome(this.commitTimestamp, event.window, focusScore);
    const receipt = createPracticeMoneyReceipt(snapshot, outcome, startingBankroll, stake);
    const debrief: Debrief = createDebrief(snapshot, outcome, receipt, commitOffset);

    return this.buildRecord(tape, event.t, outcome, receipt, debrief);
  }

  finalizeBlocked(
    tape: Tape,
    at: number,
    reason: string,
    startingBankroll = STARTING_BANKROLL,
    stake = PRACTICE_STAKE,
  ): RunRecord {
    const outcome: RunOutcome = {
      grade: "blocked",
      success: false,
      committed: false,
      reason,
      focusScore: null,
    };
    const receipt = createPracticeMoneyReceipt(
      {
        grossEdgeBps: 0,
        feesBps: 0,
        slippageBps: 0,
        netEdgeBps: 0,
        path: [],
        assumptions: [],
        qualityBand: "weak",
      },
      outcome,
      startingBankroll,
      stake,
    );
    const debrief: Debrief = {
      headline: receipt.label,
      reasons: ["Run ended without a valid buy window.", "Load a clean tape and restart."],
      metrics: {
        grossPnl: receipt.grossPnl,
        netPnl: receipt.netPnl,
        commitOffsetMs: null,
      },
      recommendation: "Reset",
    };

    return this.buildRecord(tape, at, outcome, receipt, debrief);
  }

  reset(): void {
    this.phase = "standby";
    this.transitions = [{ phase: "standby", at: 0, reason: "reset" }];
    this.actions = [{ type: "reset", at: 0 }];
    this.commitTimestamp = null;
  }

  private buildRecord(
    tape: Tape,
    frozenAt: number,
    outcome: RunOutcome,
    receipt: ReturnType<typeof createPracticeMoneyReceipt>,
    debrief: Debrief,
  ): RunRecord {
    const afterimage: Afterimage = {
      frozenAt,
      windowState: outcome.success ? "closed" : "missed",
      commitState: this.commitTimestamp === null ? "none" : "resolved",
    };

    return {
      id: `run-${Date.now()}`,
      tapeId: tape.id,
      mode: tape.mode,
      startTimestamp: new Date().toISOString(),
      stateTransitions: [...this.transitions],
      userActionLog: [...this.actions],
      commitTimestamp: this.commitTimestamp,
      outcome,
      afterimage,
      receipt,
      debrief,
    };
  }
}

function resolveOutcome(commitTimestamp: number | null, window: FocusWindow | undefined, focusScore: number): RunOutcome {
  const grade = resolveCommitGrade(window, commitTimestamp, focusScore);

  switch (grade) {
    case "blocked":
      return { grade, success: false, committed: false, reason: "no opportunity window", focusScore: null };
    case "miss":
      return { grade, success: false, committed: false, reason: "no commit registered", focusScore: null };
    case "early":
      return { grade, success: false, committed: true, reason: "too early", focusScore };
    case "late":
      return { grade, success: false, committed: true, reason: "too late", focusScore };
    case "off_target":
      return { grade, success: false, committed: true, reason: "focus missed the window", focusScore };
    default:
      return { grade: "clear", success: true, committed: true, reason: "inside the window", focusScore };
  }
}

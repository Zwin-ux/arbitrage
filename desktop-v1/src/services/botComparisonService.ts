import type { BotComparisonResult, BotPresetName, RunOutcome, Tape, TapeEvent } from "@domain/types";
import { STARTER_BOTS } from "@presets/starterBots";
import { evaluatePresetAgainstEvent } from "@services/botEngine";
import { getBundledTapeExpectation } from "@services/bundledTapeExpectations";
import { createPracticeMoneyReceipt, PRACTICE_STAKE, STARTING_BANKROLL } from "@services/practiceMoney";

const PRESET_BIAS_MS: Record<BotPresetName, number> = {
  Safe: 120,
  Balanced: 0,
  Aggressive: -420,
};

export function buildBotComparisonResults(
  tape: Tape,
  startingBankroll = STARTING_BANKROLL,
  stake = PRACTICE_STAKE,
): BotComparisonResult[] {
  const event = findPrimaryOpportunityEvent(tape);
  const snapshot = event?.routeSnapshot;
  const window = event?.window;
  if (!event || !snapshot || !window) {
    return [];
  }

  return (Object.keys(STARTER_BOTS) as BotPresetName[]).map((presetName) => {
    const preset = STARTER_BOTS[presetName];
    const decision = evaluatePresetAgainstEvent(preset, event);

    if (!decision.shouldCommit) {
      const outcome: RunOutcome = {
        grade: "miss",
        success: false,
        committed: false,
        reason: "preset waited",
      };
      return {
        preset: presetName,
        verdict: "wait",
        reason: decision.reason,
        receipt: createPracticeMoneyReceipt(snapshot, outcome, startingBankroll, stake),
      };
    }

    const commitTimestamp = window.idealCommitAt + PRESET_BIAS_MS[presetName];
    const outcome = resolvePresetOutcome(commitTimestamp, event);
    return {
      preset: presetName,
      verdict: outcome.grade === "clear" ? "clean" : outcome.grade === "early" ? "early" : "late",
      reason: decision.reason,
      receipt: createPracticeMoneyReceipt(snapshot, outcome, startingBankroll, stake),
    };
  });
}

export function findPrimaryOpportunityEvent(tape: Tape): TapeEvent | null {
  const expected = getBundledTapeExpectation(tape.id);
  if (expected) {
    const primaryEvent = tape.events.find(
      (event) => event.id === expected.primaryOpportunityEventId && event.routeSnapshot && event.window,
    );
    if (primaryEvent) {
      return primaryEvent;
    }
  }

  return tape.events.find((event) => event.eventType === "route_snapshot" && event.routeSnapshot && event.window)
    ?? tape.events.find((event) => event.routeSnapshot && event.window)
    ?? null;
}

function resolvePresetOutcome(commitTimestamp: number, event: TapeEvent): RunOutcome {
  const window = event.window;
  if (!window) {
    return { grade: "blocked", success: false, committed: false, reason: "no opportunity window" };
  }
  if (commitTimestamp < window.opensAt) {
    return { grade: "early", success: false, committed: true, reason: "too early" };
  }
  if (commitTimestamp > window.closesAt) {
    return { grade: "late", success: false, committed: true, reason: "too late" };
  }
  return { grade: "clear", success: true, committed: true, reason: "inside the window" };
}

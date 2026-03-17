import type { PracticeMoneyReceipt, RouteSnapshot, RunOutcome } from "@domain/types";

export const STARTING_BANKROLL = 100;
export const PRACTICE_STAKE = 25;

function roundMoney(value: number): number {
  return Number(value.toFixed(2));
}

export function createPracticeMoneyReceipt(
  _snapshot: RouteSnapshot,
  outcome: RunOutcome,
  startingBankroll = STARTING_BANKROLL,
  stake = PRACTICE_STAKE,
): PracticeMoneyReceipt {
  if (!outcome.committed || outcome.grade === "miss" || outcome.grade === "blocked") {
    return {
      label: "NO TRADE",
      tone: "idle",
      startingBankroll,
      stake,
      entryPrice: null,
      exitPrice: null,
      grossPnl: 0,
      fees: 0,
      slippage: 0,
      netPnl: 0,
      endingBankroll: startingBankroll,
    };
  }

  const profile = outcome.grade === "clear"
    ? { label: "CLEAN WIN", tone: "positive" as const, entryPrice: 0.52, exitPrice: 0.71, fees: 0.62, slippage: 0.77 }
    : outcome.grade === "early"
      ? { label: "EARLY BUY", tone: "negative" as const, entryPrice: 0.59, exitPrice: 0.57, fees: 0.62, slippage: 0.78 }
      : { label: "LATE BUY", tone: "negative" as const, entryPrice: 0.65, exitPrice: 0.61, fees: 0.62, slippage: 1.02 };

  const shares = stake / profile.entryPrice;
  const grossPnl = roundMoney(shares * (profile.exitPrice - profile.entryPrice));
  const fees = roundMoney(profile.fees);
  const slippage = roundMoney(profile.slippage);
  const netPnl = roundMoney(grossPnl - fees - slippage);

  return {
    label: profile.label,
    tone: profile.tone,
    startingBankroll,
    stake,
    entryPrice: profile.entryPrice,
    exitPrice: profile.exitPrice,
    grossPnl,
    fees,
    slippage,
    netPnl,
    endingBankroll: roundMoney(startingBankroll + netPnl),
  };
}

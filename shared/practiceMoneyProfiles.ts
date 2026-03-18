export type PracticeMoneyProfileId = "clear" | "early" | "late" | "no_trade";

export interface PracticeMoneyProfile {
  id: PracticeMoneyProfileId;
  label: string;
  tone: "positive" | "negative" | "idle";
  entryPrice: number | null;
  exitPrice: number | null;
  fees: number;
  slippage: number;
}

export interface PracticeMoneyOutcome {
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

export const STARTING_BANKROLL = 100;
export const PRACTICE_STAKE = 25;

export const PRACTICE_MONEY_PROFILES: Record<PracticeMoneyProfileId, PracticeMoneyProfile> = {
  clear: {
    id: "clear",
    label: "CLEAN WIN",
    tone: "positive",
    entryPrice: 0.52,
    exitPrice: 0.71,
    fees: 0.62,
    slippage: 0.77,
  },
  early: {
    id: "early",
    label: "EARLY BUY",
    tone: "negative",
    entryPrice: 0.59,
    exitPrice: 0.57,
    fees: 0.62,
    slippage: 0.78,
  },
  late: {
    id: "late",
    label: "LATE BUY",
    tone: "negative",
    entryPrice: 0.65,
    exitPrice: 0.61,
    fees: 0.62,
    slippage: 1.02,
  },
  no_trade: {
    id: "no_trade",
    label: "NO TRADE",
    tone: "idle",
    entryPrice: null,
    exitPrice: null,
    fees: 0,
    slippage: 0,
  },
};

export function createPracticeMoneyOutcome(
  profileId: PracticeMoneyProfileId,
  startingBankroll = STARTING_BANKROLL,
  stake = PRACTICE_STAKE,
): PracticeMoneyOutcome {
  const profile = PRACTICE_MONEY_PROFILES[profileId];
  if (!profile.entryPrice || profile.exitPrice === null) {
    return {
      label: profile.label,
      tone: profile.tone,
      startingBankroll,
      stake,
      entryPrice: null,
      exitPrice: null,
      grossPnl: 0,
      fees: 0,
      slippage: 0,
      netPnl: 0,
      endingBankroll: roundMoney(startingBankroll),
    };
  }

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

function roundMoney(value: number): number {
  return Number(value.toFixed(2));
}

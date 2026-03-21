import type { Debrief, DebriefMetrics, PracticeMoneyReceipt, RouteSnapshot, RunOutcome } from "@domain/types";

export interface RouteEvaluation {
  netEdgeBps: number;
  passes: boolean;
  reason: string;
  qualityBand: RouteSnapshot["qualityBand"];
}

export function evaluateRoute(snapshot: RouteSnapshot): RouteEvaluation {
  const netEdgeBps = snapshot.grossEdgeBps - snapshot.feesBps - snapshot.slippageBps;
  const passes = netEdgeBps > 0;
  return {
    netEdgeBps,
    passes,
    reason: passes ? "net edge stayed positive" : "deductions erased the edge",
    qualityBand: snapshot.qualityBand,
  };
}

export function createDebrief(
  snapshot: RouteSnapshot,
  outcome: RunOutcome,
  receipt: PracticeMoneyReceipt,
  commitOffsetMs: number | null,
): Debrief {
  const metrics: DebriefMetrics = {
    grossPnl: receipt.grossPnl,
    netPnl: receipt.netPnl,
    commitOffsetMs,
  };

  return {
    headline: receipt.label,
    reasons: [
      receipt.entryPrice === null
        ? "No position opened."
        : `Buy ${formatPrice(receipt.entryPrice)} -> Sell ${formatPrice(receipt.exitPrice ?? receipt.entryPrice)}`,
      `Gross ${formatMoney(receipt.grossPnl)} / Fees ${formatMoney(receipt.fees)} / Slip ${formatMoney(receipt.slippage)}`,
      `Net ${formatMoney(receipt.netPnl)} / Score ${formatMoney(receipt.endingBankroll)}`,
    ],
    metrics,
    recommendation: resolveRecommendation(outcome),
  };
}

function resolveRecommendation(outcome: RunOutcome): string {
  switch (outcome.grade) {
    case "clear":
      return "Hold center";
    case "early":
      return "Wait longer";
    case "late":
      return "Commit earlier";
    case "miss":
      return "No entry";
    default:
      return "Reset";
  }
}

function formatMoney(value: number): string {
  const sign = value >= 0 ? "+" : "-";
  return `${sign}$${Math.abs(value).toFixed(2)}`;
}

function formatPrice(value: number): string {
  return `${Math.round(value * 100)}c`;
}

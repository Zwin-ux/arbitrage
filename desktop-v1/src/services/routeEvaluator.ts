import type { Debrief, DebriefMetrics, RouteSnapshot, RunOutcome } from "@domain/types";

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
  commitOffsetMs: number | null,
): Debrief {
  const metrics: DebriefMetrics = {
    grossEdgeBps: snapshot.grossEdgeBps,
    netEdgeBps: snapshot.netEdgeBps,
    commitOffsetMs,
  };

  return {
    headline: outcome.success ? "Clean commit." : "Commit missed the window.",
    reasons: [
      `Gross ${formatBps(snapshot.grossEdgeBps)} -> Net ${formatBps(snapshot.netEdgeBps)}`,
      outcome.reason,
    ],
    metrics,
    recommendation: outcome.success ? "Hold this pace." : "Wait for a cleaner window.",
  };
}

function formatBps(value: number): string {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${(value / 100).toFixed(2)}%`;
}

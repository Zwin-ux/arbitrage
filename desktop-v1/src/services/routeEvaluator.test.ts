import { describe, expect, it } from "vitest";

import type { PracticeMoneyReceipt, RouteSnapshot, RunOutcome } from "@domain/types";
import { computeNetEdgeBps, createDebrief, evaluateRoute } from "@services/routeEvaluator";
import { createPracticeMoneyReceipt } from "@services/practiceMoney";

const snapshot: RouteSnapshot = {
  grossEdgeBps: 360,
  feesBps: 70,
  slippageBps: 95,
  netEdgeBps: 195,
  path: ["BUY YES", "SELL NO"],
  assumptions: ["balanced timing only"],
  qualityBand: "usable",
};

describe("route evaluator", () => {
  it("computes net edge from gross, fees, and slippage", () => {
    expect(computeNetEdgeBps(snapshot)).toBe(195);
    expect(evaluateRoute(snapshot)).toEqual({
      netEdgeBps: 195,
      passes: true,
      reason: "net edge stayed positive",
      qualityBand: "usable",
    });
  });

  it("flags routes as failing when deductions erase the edge", () => {
    const weakSnapshot: RouteSnapshot = {
      ...snapshot,
      grossEdgeBps: 150,
      feesBps: 70,
      slippageBps: 95,
      netEdgeBps: -15,
      qualityBand: "weak",
    };

    expect(evaluateRoute(weakSnapshot)).toEqual({
      netEdgeBps: -15,
      passes: false,
      reason: "deductions erased the edge",
      qualityBand: "weak",
    });
  });

  it("maps debrief recommendations for clear, early, late, off-target, and miss outcomes", () => {
    expect(createDebriefFor("clear").recommendation).toBe("Hold center");
    expect(createDebriefFor("early").recommendation).toBe("Wait longer");
    expect(createDebriefFor("late").recommendation).toBe("Commit earlier");
    expect(createDebriefFor("off_target").recommendation).toBe("Aim center");
    expect(createDebriefFor("miss").recommendation).toBe("No entry");
  });
});

function createDebriefFor(grade: RunOutcome["grade"]) {
  const outcome: RunOutcome = {
    grade,
    success: grade === "clear",
    committed: grade !== "miss" && grade !== "blocked",
    reason: grade,
    focusScore: grade === "miss" || grade === "blocked" ? null : grade === "off_target" ? 0.32 : 1,
  };
  const receipt: PracticeMoneyReceipt = createPracticeMoneyReceipt(snapshot, outcome, 100, 25);

  return createDebrief(snapshot, outcome, receipt, grade === "miss" ? null : 0);
}

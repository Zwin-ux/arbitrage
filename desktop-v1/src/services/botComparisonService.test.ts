import { describe, expect, it } from "vitest";

import type { Tape } from "@domain/types";
import openingWindowTapeJson from "@tapes/replay/opening-window.json";
import introRouteTapeJson from "@tapes/tutorial/intro-route.json";
import { buildBotComparisonResults } from "@services/botComparisonService";

const introRouteTape = introRouteTapeJson as Tape;
const openingWindowTape = openingWindowTapeJson as Tape;

describe("bot comparison service", () => {
  it("shows different preset outcomes on the clean tutorial tape", () => {
    const results = buildBotComparisonResults(introRouteTape, 100, 25);

    expect(results).toHaveLength(3);
    expect(results.find((item) => item.preset === "Safe")?.verdict).toBe("clean");
    expect(results.find((item) => item.preset === "Balanced")?.verdict).toBe("clean");
    expect(results.find((item) => item.preset === "Aggressive")?.verdict).toBe("early");
  });

  it("keeps safer presets out of thin replay setups", () => {
    const results = buildBotComparisonResults(openingWindowTape, 100, 25);

    expect(results.find((item) => item.preset === "Safe")?.verdict).toBe("wait");
    expect(results.find((item) => item.preset === "Balanced")?.verdict).toBe("wait");
    expect(results.find((item) => item.preset === "Aggressive")?.verdict).toBe("early");
  });
});

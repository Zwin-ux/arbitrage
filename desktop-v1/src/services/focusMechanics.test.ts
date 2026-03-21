import { describe, expect, it } from "vitest";

import { analyzeFocus, getWindowBand, resolveCommitGrade } from "@shared/focusMechanics";

const duration = 2440;
const window = {
  opensAt: 1480,
  closesAt: 2320,
  idealCommitAt: 1880,
  holdMs: 500,
};

describe("focus mechanics", () => {
  it("marks focus as hot near the center of the live window", () => {
    const band = getWindowBand(window, duration, window.idealCommitAt);
    const focus = analyzeFocus(band?.center ?? 0.4, window, duration, window.idealCommitAt);

    expect(focus.band).not.toBeNull();
    expect(focus.hot).toBe(true);
    expect(focus.score).toBeGreaterThan(0.9);
  });

  it("drops to cold when the reticle drifts away from the window", () => {
    const focus = analyzeFocus(0.9, window, duration, window.idealCommitAt);

    expect(focus.hot).toBe(false);
    expect(focus.score).toBe(0);
  });

  it("resolves off-target when timing is right but focus is weak", () => {
    expect(resolveCommitGrade(window, window.idealCommitAt, 0.3)).toBe("off_target");
  });
});

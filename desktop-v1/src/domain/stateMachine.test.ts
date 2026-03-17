import { describe, expect, it } from "vitest";

import { canTransition, nextPhase } from "@domain/stateMachine";

describe("state machine", () => {
  it("allows only valid rehearsal transitions", () => {
    expect(canTransition("standby", "arm")).toBe(true);
    expect(canTransition("pressure", "commit_hold")).toBe(true);
    expect(canTransition("pressure", "arm")).toBe(false);
    expect(canTransition("afterimage", "run")).toBe(false);
  });

  it("returns the next ordered phase", () => {
    expect(nextPhase("run")).toBe("pressure");
    expect(nextPhase("afterimage")).toBe("reset");
  });
});

import type { BotPreset, TapeEvent } from "@domain/types";
import { shouldPresetCommit } from "@presets/starterBots";

export interface BotDecision {
  preset: BotPreset["name"];
  shouldCommit: boolean;
  reason: string;
}

export function evaluatePresetAgainstEvent(preset: BotPreset, event: TapeEvent): BotDecision {
  const snapshot = event.routeSnapshot;
  const window = event.window;

  if (!snapshot || !window) {
    return { preset: preset.name, shouldCommit: false, reason: "no route window" };
  }

  const shouldCommit = shouldPresetCommit(preset, snapshot, window, event.t);
  return {
    preset: preset.name,
    shouldCommit,
    reason: shouldCommit ? "preset commits inside the window" : "preset waits",
  };
}

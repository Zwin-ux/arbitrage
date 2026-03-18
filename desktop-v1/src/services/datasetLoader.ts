import introRouteTape from "@tapes/tutorial/intro-route.json";
import steadyWindowTape from "@tapes/tutorial/steady-window.json";
import openingWindowTape from "@tapes/replay/opening-window.json";
import thinReversalTape from "@tapes/replay/thin-reversal.json";
import type { Tape, TapeMode } from "@domain/types";

const manifest: Tape[] = [
  introRouteTape as Tape,
  steadyWindowTape as Tape,
  openingWindowTape as Tape,
  thinReversalTape as Tape,
];

export interface TapeSummary {
  id: string;
  name: string;
  mode: TapeMode;
  symbol: string;
}

export function listTapes(mode: TapeMode): Tape[] {
  return manifest.filter((item) => item.mode === mode);
}

export function getTapeById(id: string): Tape | undefined {
  return manifest.find((item) => item.id === id);
}

export function listTapeSummaries(mode: TapeMode): TapeSummary[] {
  return listTapes(mode).map((item) => ({
    id: item.id,
    name: item.name,
    mode: item.mode,
    symbol: item.market.symbol,
  }));
}

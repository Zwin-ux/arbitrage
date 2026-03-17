export interface CsvToTapeConfig {
  tapeId: string;
  tapeName: string;
  mode: "tutorial" | "replay";
  venue: "Polymarket";
  symbol: string;
  marketId: string;
  marketSlug: string;
}

export function csvToTapePlan(config: CsvToTapeConfig): string[] {
  return [
    `load source rows for ${config.symbol}`,
    "normalize timestamps into milliseconds from tape start",
    "derive value and volume proxies per row",
    "author opportunity windows where route math is readable",
    "emit JSON tape for bundled playback",
  ];
}

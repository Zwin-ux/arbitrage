import type { TapeMode } from "@domain/types";

interface ModeSelectScreenProps {
  selected: TapeMode;
  liveUnlocked: boolean;
  onSelectMode: (mode: TapeMode) => void;
}

export function ModeSelectScreen({ selected, liveUnlocked, onSelectMode }: ModeSelectScreenProps) {
  return (
    <section aria-label="Mode select" className="mode-strip">
      <button type="button" className="mode-button" aria-pressed={selected === "tutorial"} onClick={() => onSelectMode("tutorial")}>
        <span className="mode-button__index">01</span>
        <strong className="mode-button__label">Tutorial</strong>
      </button>
      <button type="button" className="mode-button" aria-pressed={selected === "replay"} onClick={() => onSelectMode("replay")}>
        <span className="mode-button__index">02</span>
        <strong className="mode-button__label">Replay</strong>
      </button>
      <button
        type="button"
        className="mode-button"
        aria-pressed={selected === "live-preview"}
        aria-disabled={!liveUnlocked}
        onClick={() => onSelectMode("live-preview")}
      >
        <span className="mode-button__index">03</span>
        <strong className="mode-button__label">Live Books</strong>
      </button>
    </section>
  );
}

import type { RunPhase, Tape, TapeEvent } from "@domain/types";
import { FOCUS_NUDGE_STEP, getEventScreenRatio, getWindowBand } from "@shared/focusMechanics";
import superiorHead from "../assets/superior-head.png";

interface DecisionLaneProps {
  tape: Tape;
  currentTime: number;
  currentEvent: TapeEvent | null;
  phase: RunPhase;
  focusPosition: number;
  focusHot: boolean;
  onFocusChange: (ratio: number) => void;
  onFocusNudge: (delta: number) => void;
}

export function DecisionLane({
  tape,
  currentTime,
  currentEvent,
  phase,
  focusPosition,
  focusHot,
  onFocusChange,
  onFocusNudge,
}: DecisionLaneProps) {
  const duration = tape.events[tape.events.length - 1]?.t ?? 1;
  const windowBands = dedupeWindows(tape.events)
    .map((window) => ({
      key: `${window.opensAt}-${window.closesAt}`,
      band: getWindowBand(window, duration, currentTime),
      active:
        currentEvent?.window?.opensAt === window.opensAt &&
        currentEvent.window.closesAt === window.closesAt &&
        phase !== "afterimage",
    }))
    .filter((entry) => entry.band);

  const focusLeft = `${Math.max(0, Math.min(100, focusPosition * 100))}%`;
  const trackDirection = focusPosition < 0.41 ? "left" : focusPosition > 0.49 ? "right" : "center";

  return (
    <div
      aria-label="Decision lane"
      className="lane-surface"
      data-hot={focusHot ? "true" : "false"}
      tabIndex={0}
      onPointerMove={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        onFocusChange((event.clientX - rect.left) / rect.width);
      }}
      onPointerDown={(event) => {
        const rect = event.currentTarget.getBoundingClientRect();
        onFocusChange((event.clientX - rect.left) / rect.width);
      }}
      onKeyDown={(event) => {
        if (event.key === "ArrowLeft") {
          event.preventDefault();
          onFocusNudge(-FOCUS_NUDGE_STEP);
        }
        if (event.key === "ArrowRight") {
          event.preventDefault();
          onFocusNudge(FOCUS_NUDGE_STEP);
        }
      }}
    >
      <div className="lane-axis" />
      <div className="lane-viewport">
        <div className="lane-motion">
          {windowBands.map((entry) => (
            <span
              key={entry.key}
              className={`lane-window-bar ${entry.active ? "lane-window-bar-active" : ""}`}
              style={{
                left: `${entry.band!.start * 100}%`,
                width: `${entry.band!.width * 100}%`,
              }}
            />
          ))}

          {tape.events.map((event) => {
            const left = `${getEventScreenRatio(event.t, duration, currentTime) * 100}%`;
            const isCurrent = currentEvent?.id === event.id;
            return (
              <span
                key={event.id}
                className={`lane-event ${isCurrent ? "lane-event-active" : ""}`}
                data-phase={phase}
                style={{ left }}
              />
            );
          })}
        </div>
      </div>
      <div className="lane-anchor" />
      <div className={`lane-focus-head lane-focus-head--${trackDirection} ${focusHot ? "lane-focus-head--hot" : ""}`} style={{ left: focusLeft }}>
        <img alt="" src={superiorHead} />
      </div>
      <div className={`lane-focus-line ${focusHot ? "lane-focus-line--hot" : ""}`} style={{ left: focusLeft }} />
      <div className={`lane-focus-reticle ${focusHot ? "lane-focus-reticle--hot" : ""}`} style={{ left: focusLeft }} />
    </div>
  );
}

function dedupeWindows(events: TapeEvent[]) {
  const seen = new Set<string>();
  return events.flatMap((event) => {
    if (!event.window) {
      return [];
    }
    const key = `${event.window.opensAt}-${event.window.closesAt}`;
    if (seen.has(key)) {
      return [];
    }
    seen.add(key);
    return [event.window];
  });
}

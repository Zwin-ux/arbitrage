import type { RunPhase, Tape, TapeEvent } from "@domain/types";

interface DecisionLaneProps {
  tape: Tape;
  currentTime: number;
  currentEvent: TapeEvent | null;
  phase: RunPhase;
}

export function DecisionLane({ tape, currentTime, currentEvent, phase }: DecisionLaneProps) {
  const duration = tape.events[tape.events.length - 1]?.t ?? 1;
  const progress = Math.max(0, Math.min(1, currentTime / duration));
  const drift = `translateX(-${progress * 44}%)`;

  return (
    <div aria-label="Decision lane" className="lane-surface">
      <div className="lane-axis" />
      <div className="lane-viewport">
        <div className="lane-motion" style={{ transform: drift }}>
          {tape.events.map((event) => {
            const left = `${8 + (event.t / duration) * 84}%`;
            const isCurrent = currentEvent?.id === event.id;
            return (
              <div key={event.id}>
                {event.window ? (
                  <span
                    className={`lane-window-bar ${isCurrent ? "lane-window-bar-active" : ""}`}
                    style={{
                      left,
                      width: `${((event.window.closesAt - event.window.opensAt) / duration) * 100}%`,
                    }}
                  />
                ) : null}
                <span
                  className={`lane-event ${isCurrent ? "lane-event-active" : ""}`}
                  data-phase={phase}
                  style={{ left }}
                />
              </div>
            );
          })}
        </div>
      </div>
      <div className="lane-anchor" />
    </div>
  );
}

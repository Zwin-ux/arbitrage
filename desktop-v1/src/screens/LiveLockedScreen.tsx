import type { LiveGate } from "@domain/types";

interface LiveLockedScreenProps {
  gate: LiveGate;
}

export function LiveLockedScreen({ gate }: LiveLockedScreenProps) {
  return (
    <section aria-label="Live books locked" className="locked-surface">
      <strong className="locked-title">LIVE BOOKS LOCKED</strong>
      <div className="locked-summary">
        <span>PRACTICE WINS {gate.successfulRuns}</span>
        <span>TIMING {gate.consistencyScore}%</span>
      </div>
      <ul className="locked-list">
        {gate.unlockRequirements.map((item) => (
          <li key={item.label}>
            <span>{item.label.toUpperCase()}</span>
            <strong>
              {item.current}/{item.target}
            </strong>
          </li>
        ))}
      </ul>
    </section>
  );
}

import { useEffect, useRef, useState } from "react";

function HoldToInstall({ href }) {
  const [holding, setHolding] = useState(false);
  const [progress, setProgress] = useState(0);
  const timerRef = useRef(null);
  const startRef = useRef(0);

  useEffect(() => {
    if (!holding) {
      setProgress(0);
      return undefined;
    }

    const tick = () => {
      const elapsed = Date.now() - startRef.current;
      const nextProgress = Math.min(1, elapsed / 850);
      setProgress(nextProgress);

      if (nextProgress >= 1) {
        window.location.href = href;
        setHolding(false);
        return;
      }

      timerRef.current = window.requestAnimationFrame(tick);
    };

    timerRef.current = window.requestAnimationFrame(tick);
    return () => {
      if (timerRef.current) {
        window.cancelAnimationFrame(timerRef.current);
      }
    };
  }, [holding, href]);

  const startHold = () => {
    startRef.current = Date.now();
    setHolding(true);
  };

  const stopHold = () => {
    setHolding(false);
  };

  return (
    <button
      className="control-button control-button-primary"
      onMouseDown={startHold}
      onMouseUp={stopHold}
      onMouseLeave={stopHold}
      onTouchStart={startHold}
      onTouchEnd={stopHold}
      type="button"
    >
      <span className="control-button-fill" style={{ transform: `scaleX(${progress})` }} />
      <span className="control-button-text">Hold to install</span>
    </button>
  );
}

export default function HeroSection({ variant }) {
  const movingSegments = Array.from({ length: 6 }, (_, index) => ({
    key: index,
    style: {
      left: `${index * 20}%`,
      width: index % 2 === 0 ? "24px" : "8px",
    },
  }));

  return (
    <section className="machine-hero">
      <div className="machine-meta">
        <p className="machine-eyebrow">{variant.eyebrow}</p>
        <img alt="Superior" className="machine-wordmark" src="/assets/superior-wordmark.png" />
        <p className="machine-line">{variant.heroLine}</p>
        <p className="machine-support">{variant.heroSupport}</p>
      </div>

      <div className="playfield">
        <div className="playfield-head">
          <span>ROUTE FIELD</span>
          <span>LIVE LOCKED</span>
        </div>

        <div className="lane-field">
          <div className="lane-track" />
          <div className="lane-motion">
            {movingSegments.map((segment) => (
              <span key={segment.key} className="lane-segment" style={segment.style} />
            ))}
          </div>
          <div className="lane-anchor">
            <span className="lane-anchor-mark" />
          </div>
        </div>

        <div className="playfield-foot">
          <span>BOOK</span>
          <span>LOCAL</span>
          <span>TEST</span>
          <span>LOCKED</span>
        </div>
      </div>

      <div className="control-row" aria-label="Primary controls">
        <HoldToInstall href={variant.windowsInstallerUrl} />
        <a className="control-button" href={variant.portableUrl}>
          Portable
        </a>
        <a className="control-button" href={variant.githubUrl} target="_blank" rel="noreferrer">
          Source
        </a>
        <a className="control-button" href="/download">
          Release
        </a>
      </div>
    </section>
  );
}

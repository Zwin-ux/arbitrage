import { useEffect, useMemo, useRef, useState } from "react";

import {
  analyzeFocus,
  FOCUS_DEFAULT_RATIO,
  getEventScreenRatio,
  getWindowBand,
  resolveCommitGrade,
} from "../../../shared/focusMechanics";
import { createPracticeMoneyOutcome, PRACTICE_STAKE, STARTING_BANKROLL } from "../../../shared/practiceMoneyProfiles";

const DEMO_DURATION = 2600;
const DEMO_WINDOW = {
  opensAt: 720,
  closesAt: 1340,
  idealCommitAt: 1040,
  holdMs: 340,
};
const DEMO_EVENTS = [
  { id: "ready", t: 0 },
  { id: "build", t: 360 },
  { id: "open", t: 720 },
  { id: "commit", t: 1040 },
  { id: "close", t: 1340 },
  { id: "fade", t: 1820 },
];

export default function SuperiorLanding({ variant }) {
  const installerUrl = variant?.windowsInstallerUrl ?? "/download/";
  const statusText = variant?.statusText ?? "WINDOWS / LOCAL / AUTO";
  const runFrameRef = useRef(null);
  const holdFrameRef = useRef(null);
  const holdStartRef = useRef(null);
  const runStartRef = useRef(null);
  const liveTimeRef = useRef(0);
  const liveFocusRef = useRef(0);

  const [phase, setPhase] = useState("idle");
  const [currentTime, setCurrentTime] = useState(0);
  const [holdProgress, setHoldProgress] = useState(0);
  const [focusPosition, setFocusPosition] = useState(FOCUS_DEFAULT_RATIO);
  const [receipt, setReceipt] = useState(null);

  const focusState = useMemo(() => {
    return analyzeFocus(focusPosition, DEMO_WINDOW, DEMO_DURATION, currentTime);
  }, [currentTime, focusPosition]);
  const focusLeft = `${focusPosition * 100}%`;
  const windowBand = focusState.band;
  const bankroll = receipt?.endingBankroll ?? STARTING_BANKROLL;
  const stateLabel = phase === "resolved" ? receipt?.label ?? "RESULT" : focusState.hot ? "BUY WINDOW" : phase === "running" ? "TRACK" : "READY";

  useEffect(() => {
    liveTimeRef.current = currentTime;
    liveFocusRef.current = focusState.score;
  }, [currentTime, focusState.score]);

  useEffect(() => {
    if (phase !== "running") {
      return;
    }

    const tick = (now) => {
      if (runStartRef.current === null) {
        runStartRef.current = now;
      }

      const elapsed = Math.min(now - runStartRef.current, DEMO_DURATION);
      setCurrentTime(elapsed);

      if (elapsed >= DEMO_DURATION) {
        resolveRun(null, 0);
        return;
      }

      runFrameRef.current = window.requestAnimationFrame(tick);
    };

    runFrameRef.current = window.requestAnimationFrame(tick);
    return () => {
      if (runFrameRef.current !== null) {
        window.cancelAnimationFrame(runFrameRef.current);
      }
    };
  }, [phase]);

  useEffect(() => {
    return () => {
      if (runFrameRef.current !== null) {
        window.cancelAnimationFrame(runFrameRef.current);
      }
      if (holdFrameRef.current !== null) {
        window.cancelAnimationFrame(holdFrameRef.current);
      }
    };
  }, []);

  function startRun() {
    if (runFrameRef.current !== null) {
      window.cancelAnimationFrame(runFrameRef.current);
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    holdStartRef.current = null;
    runStartRef.current = null;
    setCurrentTime(0);
    setHoldProgress(0);
    setReceipt(null);
    setPhase("running");
  }

  function startHold() {
    if (phase !== "running") {
      return;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }

    holdStartRef.current = window.performance.now();
    setPhase("holding");

    const tick = (now) => {
      if (holdStartRef.current === null) {
        return;
      }
      const elapsed = now - holdStartRef.current;
      const nextProgress = Math.min(1, elapsed / DEMO_WINDOW.holdMs);
      setHoldProgress(nextProgress);

      if (nextProgress >= 1) {
        resolveRun(liveTimeRef.current, liveFocusRef.current);
        return;
      }

      holdFrameRef.current = window.requestAnimationFrame(tick);
    };

    holdFrameRef.current = window.requestAnimationFrame(tick);
  }

  function stopHold() {
    if (phase !== "holding") {
      return;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    holdStartRef.current = null;
    setHoldProgress(0);
    setPhase("running");
  }

  function resetRun() {
    if (runFrameRef.current !== null) {
      window.cancelAnimationFrame(runFrameRef.current);
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }
    runStartRef.current = null;
    holdStartRef.current = null;
    setCurrentTime(0);
    setHoldProgress(0);
    setFocusPosition(FOCUS_DEFAULT_RATIO);
    setReceipt(null);
    setPhase("idle");
  }

  function resolveRun(commitTime, focusScore) {
    if (runFrameRef.current !== null) {
      window.cancelAnimationFrame(runFrameRef.current);
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
    }

    const grade = resolveCommitGrade(DEMO_WINDOW, commitTime, focusScore);
    const profileId = grade === "miss" || grade === "blocked" ? "no_trade" : grade;
    setReceipt(createPracticeMoneyOutcome(profileId, STARTING_BANKROLL, PRACTICE_STAKE));
    setHoldProgress(0);
    setPhase("resolved");
  }

  const trackDirection = focusPosition < 0.41 ? "left" : focusPosition > 0.49 ? "right" : "center";

  return (
    <main className="superior-shell">
      <div className="superior-screen">
        <header className="superior-screen__header">
          <div className="superior-screen__brand">
            <img
              className="superior-screen__brand-icon"
              src="/assets/superior-head.png"
              alt=""
              width="30"
              height="30"
              loading="eager"
              decoding="async"
            />
            <img
              className="superior-screen__wordmark"
              src="/assets/superior-wordmark.png"
              alt="Superior"
              width="168"
              height="52"
              loading="eager"
              decoding="async"
            />
            <span className="superior-screen__brand-label">{variant?.brandSubtitle ?? "engine prediction bot"}</span>
          </div>

          <div className="superior-screen__status" aria-label="Machine status">
            <span className="superior-screen__status-chip">WIN</span>
            <span className="superior-screen__status-chip">LOCAL</span>
            <span className="superior-screen__status-chip superior-screen__status-chip--accent">AUTO</span>
            <span className="superior-screen__status-text">{statusText}</span>
          </div>
        </header>

        <section className="superior-screen__playfield superior-screen__playfield--hero" aria-label="Superior hero">
          <div className="superior-demo" data-phase={phase}>
            <div className="superior-demo__readout" aria-label="Current demo state">
              <span>BANKROLL ${bankroll.toFixed(2)}</span>
              <span>STAKE $25.00</span>
              <span>{stateLabel}</span>
            </div>

            <img
              className="superior-promo__emblem superior-promo__emblem--interactive"
              src="/assets/superior-emblem.png"
              alt="Superior emblem"
              width="640"
              height="640"
              loading="eager"
              decoding="async"
            />

            <div
              className="superior-demo__lane"
              onPointerMove={(event) => {
                const rect = event.currentTarget.getBoundingClientRect();
                setFocusPosition(Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)));
              }}
              onPointerDown={(event) => {
                const rect = event.currentTarget.getBoundingClientRect();
                setFocusPosition(Math.max(0, Math.min(1, (event.clientX - rect.left) / rect.width)));
              }}
            >
              <div className="superior-demo__axis" />
              {windowBand ? (
                <span
                  className={`superior-demo__window ${focusState.hot ? "superior-demo__window--hot" : ""}`}
                  style={{
                    left: `${windowBand.start * 100}%`,
                    width: `${windowBand.width * 100}%`,
                  }}
                />
              ) : null}
              {DEMO_EVENTS.map((event) => (
                <span
                  key={event.id}
                  className={`superior-demo__tick ${Math.abs(event.t - currentTime) < 120 ? "superior-demo__tick--active" : ""}`}
                  style={{ left: `${getEventScreenRatio(event.t, DEMO_DURATION, currentTime) * 100}%` }}
                />
              ))}

              <span className={`superior-demo__beam ${focusState.hot ? "superior-demo__beam--hot" : ""}`} style={{ left: focusLeft }} />
              <span className={`superior-demo__reticle ${focusState.hot ? "superior-demo__reticle--hot" : ""}`} style={{ left: focusLeft }} />
              <span className={`superior-demo__head superior-demo__head--${trackDirection} ${focusState.hot ? "superior-demo__head--hot" : ""}`} style={{ left: focusLeft }}>
                <img src="/assets/superior-head.png" alt="" width="36" height="36" loading="lazy" decoding="async" />
              </span>
            </div>

            {receipt ? (
              <div className={`superior-demo__receipt superior-demo__receipt--${receipt.tone}`}>
                <strong>{`${receipt.netPnl >= 0 ? "+" : "-"}$${Math.abs(receipt.netPnl).toFixed(2)}`}</strong>
                <span>{`BANKROLL $${receipt.endingBankroll.toFixed(2)}`}</span>
                <span>{receipt.entryPrice === null ? "NO TRADE" : `BUY ${Math.round(receipt.entryPrice * 100)}c -> SELL ${Math.round((receipt.exitPrice ?? receipt.entryPrice) * 100)}c`}</span>
              </div>
            ) : null}
          </div>
        </section>

        <nav className="superior-screen__controls superior-screen__controls--interactive" aria-label="Primary controls">
          <button className="machine-control machine-control--primary" type="button" onClick={startRun}>
            <span>Start</span>
          </button>
          <button
            className={`machine-control machine-control--hold ${focusState.hot ? "machine-control--hold-hot" : ""}`}
            data-hot={focusState.hot ? "true" : "false"}
            type="button"
            onMouseDown={startHold}
            onMouseUp={stopHold}
            onMouseLeave={stopHold}
            onTouchStart={startHold}
            onTouchEnd={stopHold}
          >
            <span className="machine-control__fill" style={{ transform: `scaleX(${holdProgress})` }} />
            <span className="machine-control__text">Hold To Buy</span>
          </button>
          <button className="machine-control machine-control--step" type="button" onClick={resetRun}>
            <span>Reset</span>
          </button>
          <a className="machine-control machine-control--commit" href={installerUrl}>
            <span>Download EXE</span>
          </a>
        </nav>
      </div>
    </main>
  );
}

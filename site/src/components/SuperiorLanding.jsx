import { useEffect, useRef, useState } from "react";
import {
  createPracticeMoneyOutcome,
  PRACTICE_STAKE,
  STARTING_BANKROLL,
} from "@shared/practiceMoneyProfiles";

const RUN_DURATION_MS = 5200;
const HOLD_DURATION_MS = 420;
const TRACK_START = 12;
const TRACK_SPAN = 70;
const WINDOW_START = 0.43;
const WINDOW_END = 0.54;
const IDEAL_COMMIT = 0.485;

function clamp(value, min, max) {
  return Math.max(min, Math.min(max, value));
}

function formatMoney(value) {
  return `$${value.toFixed(2)}`;
}

function formatPnl(value) {
  return `${value >= 0 ? "+" : "-"}$${Math.abs(value).toFixed(2)}`;
}

function resolveTrade(progress, bankroll) {
  const offset = progress - IDEAL_COMMIT;
  const absoluteOffset = Math.abs(offset);
  const profileId = absoluteOffset >= 0.018 && offset < 0
    ? "early"
    : absoluteOffset >= 0.018 && offset > 0
      ? "late"
      : "clear";

  return createPracticeMoneyOutcome(profileId, bankroll, PRACTICE_STAKE);
}

export default function SuperiorLanding({ variant }) {
  const installerUrl = variant?.windowsInstallerUrl ?? "/download/";
  const [bankroll, setBankroll] = useState(STARTING_BANKROLL);
  const [phase, setPhase] = useState("idle");
  const [progress, setProgress] = useState(0);
  const [holdProgress, setHoldProgress] = useState(0);
  const [result, setResult] = useState(null);
  const animationFrameRef = useRef(null);
  const holdFrameRef = useRef(null);
  const runStartRef = useRef(null);
  const holdStartRef = useRef(null);

  const isRunning = phase === "running" || phase === "holding";
  const runnerLeft = `${TRACK_START + progress * TRACK_SPAN}%`;
  const windowActive = progress >= WINDOW_START && progress <= WINDOW_END;

  useEffect(() => {
    if (!isRunning) {
      return undefined;
    }

    const tick = (now) => {
      if (runStartRef.current === null) {
        runStartRef.current = now;
      }

      const elapsed = now - runStartRef.current;
      const nextProgress = clamp(elapsed / RUN_DURATION_MS, 0, 1);
      setProgress(nextProgress);

      if (nextProgress >= 1) {
        finishWithoutCommit();
        return;
      }

      animationFrameRef.current = window.requestAnimationFrame(tick);
    };

    animationFrameRef.current = window.requestAnimationFrame(tick);

    return () => {
      if (animationFrameRef.current !== null) {
        window.cancelAnimationFrame(animationFrameRef.current);
      }
    };
  }, [isRunning]);

  function clearMotion() {
    if (animationFrameRef.current !== null) {
      window.cancelAnimationFrame(animationFrameRef.current);
      animationFrameRef.current = null;
    }
    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
      holdFrameRef.current = null;
    }
  }

  function startRun() {
    clearMotion();
    runStartRef.current = null;
    holdStartRef.current = null;
    setResult(null);
    setProgress(0);
    setHoldProgress(0);
    setPhase("running");
  }

  function beginHold() {
    if (phase !== "running") {
      return;
    }

    setPhase("holding");
    holdStartRef.current = null;

    const tick = (now) => {
      if (holdStartRef.current === null) {
        holdStartRef.current = now;
      }

      const elapsed = now - holdStartRef.current;
      const nextProgress = clamp(elapsed / HOLD_DURATION_MS, 0, 1);
      setHoldProgress(nextProgress);

      if (nextProgress >= 1) {
        finishCommit();
        return;
      }

      holdFrameRef.current = window.requestAnimationFrame(tick);
    };

    holdFrameRef.current = window.requestAnimationFrame(tick);
  }

  function cancelHold() {
    if (phase !== "holding") {
      return;
    }

    if (holdFrameRef.current !== null) {
      window.cancelAnimationFrame(holdFrameRef.current);
      holdFrameRef.current = null;
    }

    holdStartRef.current = null;
    setHoldProgress(0);
    setPhase("running");
  }

  function finishCommit() {
    clearMotion();
    const trade = resolveTrade(progress, bankroll);
    setBankroll(trade.endingBankroll);
    setResult(trade);
    setHoldProgress(0);
    setPhase("resolved");
  }

  function finishWithoutCommit() {
    clearMotion();
    setResult(createPracticeMoneyOutcome("no_trade", bankroll, PRACTICE_STAKE));
    setHoldProgress(0);
    setPhase("resolved");
  }

  function resetDemo() {
    clearMotion();
    runStartRef.current = null;
    holdStartRef.current = null;
    setBankroll(STARTING_BANKROLL);
    setProgress(0);
    setHoldProgress(0);
    setResult(null);
    setPhase("idle");
  }

  return (
    <main className="superior-shell">
      <div className="superior-screen">
        <header className="superior-screen__header">
          <div className="superior-screen__brand">
            <img
              src="/assets/superior-head.png"
              alt=""
              width="30"
              height="30"
              loading="eager"
              decoding="async"
            />
            <span>SUPERIOR</span>
          </div>

          <div className="superior-screen__status" aria-label="Machine status">
            <span>PRACTICE MONEY</span>
            <span>LOCAL / POLYMARKET</span>
            <span>LIVE LOCKED</span>
          </div>
        </header>

        <section className="superior-screen__playfield" aria-label="Play money demo">
          <div className="decision-lane">
            <div className="demo-readout demo-readout--left">
              <span>BANKROLL</span>
              <strong>{formatMoney(bankroll)}</strong>
              <span>STAKE</span>
              <strong>{formatMoney(PRACTICE_STAKE)}</strong>
            </div>

            <div className="demo-readout demo-readout--right">
              <span>BEST RUN</span>
              <strong>+{formatMoney(7.74)}</strong>
              <span>BUY</span>
              <strong>52c -&gt; 71c</strong>
            </div>

            <span className="decision-lane__track" aria-hidden="true" />
            <span className={`decision-lane__window ${windowActive ? "decision-lane__window--active" : ""}`} aria-hidden="true" />
            <span className="decision-lane__window-label">BUY</span>
            <span className="decision-lane__runner" aria-hidden="true" style={{ left: runnerLeft }} />

            <span className="decision-lane__anchor" aria-hidden="true">
              <span className="decision-lane__anchor-line" />
              <span className="decision-lane__anchor-node" />
            </span>
            <span className="decision-lane__anchor-label">{windowActive ? "NOW" : "WAIT"}</span>

            {result ? (
              <div className={`decision-lane__result decision-lane__result--${result.tone}`}>
                <div className="decision-lane__result-head">
                  <div className="decision-lane__result-main">
                    <span>{result.label}</span>
                    <strong>{formatPnl(result.netPnl)}</strong>
                    <small>
                      {result.entryPrice === null
                        ? "NO POSITION OPENED"
                        : `BUY ${Math.round(result.entryPrice * 100)}c -> SELL ${Math.round(result.exitPrice * 100)}c`}
                    </small>
                    <small>BANKROLL {formatMoney(result.endingBankroll)}</small>
                  </div>
                  <img
                    className="decision-lane__result-sprite"
                    src="/assets/generated/superior-mascot-core.png"
                    alt=""
                    width="56"
                    height="56"
                    loading="lazy"
                    decoding="async"
                  />
                </div>
                <div className="decision-lane__receipt">
                  <small>GROSS {formatPnl(result.grossPnl)}</small>
                  <small>FEES -{formatMoney(result.fees)}</small>
                  <small>SLIP -{formatMoney(result.slippage)}</small>
                  <small>NET {formatPnl(result.netPnl)}</small>
                </div>
              </div>
            ) : null}
          </div>
        </section>

        <nav className="superior-screen__controls" aria-label="Primary controls">
          <button type="button" className="machine-control machine-control--primary" onClick={startRun} disabled={isRunning}>
            <span>{isRunning ? "RUNNING" : "START"}</span>
          </button>
          <button
            type="button"
            className="machine-control machine-control--commit"
            onMouseDown={beginHold}
            onMouseUp={cancelHold}
            onMouseLeave={cancelHold}
            onTouchStart={beginHold}
            onTouchEnd={cancelHold}
            disabled={!isRunning || result !== null}
          >
            <span>{phase === "holding" ? `HOLD ${Math.round(holdProgress * 100)}%` : `HOLD TO BUY ${formatMoney(PRACTICE_STAKE)}`}</span>
          </button>
          <button type="button" className="machine-control machine-control--reset" onClick={resetDemo}>
            <span>RESET</span>
          </button>
          <a className="machine-control machine-control--download" href={installerUrl}>
            <span>DOWNLOAD</span>
          </a>
        </nav>
      </div>
    </main>
  );
}

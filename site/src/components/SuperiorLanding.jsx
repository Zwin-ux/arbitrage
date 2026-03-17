import ControlledUnlocksPanel from "./landing/ControlledUnlocksPanel.jsx";
import DownloadReleasePanel from "./landing/DownloadReleasePanel.jsx";
import FooterStrip from "./landing/FooterStrip.jsx";
import HeroSection from "./landing/HeroSection.jsx";
import OperatingPrinciplesSection from "./landing/OperatingPrinciplesSection.jsx";
import RouteInspectionCard from "./landing/RouteInspectionCard.jsx";
import ScannerStateStrip from "./landing/ScannerStateStrip.jsx";
import SignalPipelineDiagram from "./landing/SignalPipelineDiagram.jsx";
import SetupSequenceRail from "./landing/SetupSequenceRail.jsx";
import SuperiorHeader from "./landing/SuperiorHeader.jsx";

export default function SuperiorLanding({ variant }) {
  return (
    <div className="landing-shell">
      <div className="landing-grid" aria-hidden="true" />
      <div className="landing-noise" aria-hidden="true" />

      <div className="landing-container">
        <SuperiorHeader variant={variant} />

        <main className="landing-main">
          <HeroSection variant={variant} />
          <ScannerStateStrip variant={variant} />
          <SignalPipelineDiagram variant={variant} />
          <OperatingPrinciplesSection variant={variant} />
          <RouteInspectionCard variant={variant} />
          <ControlledUnlocksPanel variant={variant} />
          <SetupSequenceRail variant={variant} />
          <DownloadReleasePanel variant={variant} />
        </main>

        <FooterStrip variant={variant} />
      </div>
    </div>
  );
}

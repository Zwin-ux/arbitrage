import FooterStrip from "./landing/FooterStrip.jsx";
import FeatureStrip from "./landing/FeatureStrip.jsx";
import HeroSection from "./landing/HeroSection.jsx";
import ProductPreview from "./landing/ProductPreview.jsx";
import SuperiorHeader from "./landing/SuperiorHeader.jsx";

export default function SuperiorLanding({ variant }) {
  return (
    <div className="landing-shell">
      <div className="landing-starfield" aria-hidden="true" />
      <div className="landing-radial-glow landing-radial-left" aria-hidden="true" />
      <div className="landing-radial-glow landing-radial-right" aria-hidden="true" />

      <div className="landing-container">
        <SuperiorHeader variant={variant} />
        <main className="landing-main">
          <HeroSection variant={variant} />
          <FeatureStrip variant={variant} />
          <ProductPreview variant={variant} />
        </main>
        <FooterStrip variant={variant} />
      </div>
    </div>
  );
}

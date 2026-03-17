function toneClass(tone) {
  if (tone === "magenta") {
    return "feature-title-magenta";
  }
  if (tone === "yellow") {
    return "feature-title-yellow";
  }
  return "feature-title-cyan";
}

export default function FeatureStrip({ variant }) {
  return (
    <section className="feature-strip" id="features">
      <div className="feature-grid">
        {variant.featureCards.map((card) => (
          <article key={card.title} className="feature-card">
            <div className="feature-card-top">
              <span>{card.id}</span>
              <span>v1</span>
            </div>
            <h2 className={`feature-card-title ${toneClass(card.tone)}`}>{card.title}</h2>
            <p className="feature-card-copy">{card.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

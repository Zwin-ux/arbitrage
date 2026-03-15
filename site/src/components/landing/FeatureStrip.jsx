export default function FeatureStrip({ variant }) {
  return (
    <section className="space-y-5" id="features">
      <div className="max-w-3xl">
        <p className="section-label">Built for score attack</p>
        <h2 className="section-title">Local books, staged routes, and unlocks earned from paper evidence.</h2>
      </div>

      <div className="feature-grid">
        {variant.featureCards.map((card) => (
          <article key={card.title} className="support-card">
            <p className="support-card-label">{card.eyebrow}</p>
            <h3 className="support-card-title">{card.title}</h3>
            <p className="support-card-copy">{card.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

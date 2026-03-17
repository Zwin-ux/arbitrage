export default function ProductPreview({ variant }) {
  return (
    <section className="product-section" id="product">
      <div className="product-grid-top">
        <article className="panel-card panel-card-wide">
          <div className="panel-card-head">
            <p className="section-label">{variant.setupFlow.eyebrow}</p>
            <span className="panel-version">v1</span>
          </div>
          <h2 className="panel-card-title">{variant.setupFlow.title}</h2>
          <p className="panel-card-copy">{variant.setupFlow.body}</p>

          <div className="setup-step-grid">
            {variant.setupFlow.steps.map((step) => (
              <article key={step.id} className="setup-step-card">
                <span>{step.id}</span>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </article>
            ))}
          </div>
        </article>

        <aside className="panel-card panel-card-narrow">
          <div className="panel-card-head">
            <p className="section-label">{variant.firstLaunch.eyebrow}</p>
            <span className="panel-version">v1</span>
          </div>
          <h2 className="panel-card-title">{variant.firstLaunch.title}</h2>
          <p className="panel-card-copy">{variant.firstLaunch.body}</p>

          <div className="menu-panel">
            <span className="menu-panel-label">Menu</span>
            {variant.firstLaunch.menu.map((item, index) => (
              <div key={item} className={`menu-row ${index === 0 ? "menu-row-active" : ""}`}>
                {item}
              </div>
            ))}
          </div>
        </aside>
      </div>

      <div className="product-grid-bottom">
        <article className="panel-card panel-card-story">
          <div className="panel-card-head">
            <p className="section-label">{variant.productStory.eyebrow}</p>
            <span className="panel-version">v1</span>
          </div>
          <h2 className="panel-card-title">{variant.productStory.title}</h2>
          <p className="panel-card-copy">{variant.productStory.body}</p>
        </article>

        <div className="info-card-stack">
          {variant.infoCards.map((card) => (
            <article key={card.title} className="info-card">
              <div className="panel-card-head">
                <p className="section-label">{card.eyebrow}</p>
                <span className="panel-version">v1</span>
              </div>
              <h3>{card.title}</h3>
              <p>{card.body}</p>
            </article>
          ))}
        </div>
      </div>
    </section>
  );
}

export default function OperatingPrinciplesSection({ variant }) {
  return (
    <section className="section-frame">
      <div className="section-copy">
        <p className="panel-label">{variant.principles.eyebrow}</p>
        <h2 className="section-title">{variant.principles.title}</h2>
        <p className="section-body">{variant.principles.body}</p>
      </div>

      <div className="principles-grid">
        {variant.principles.items.map((item, index) => (
          <article key={item.title} className="principle-card">
            <div className="principle-card-top">
              <span>{`0${index + 1}`}</span>
              <span>RULE</span>
            </div>
            <h3>{item.title}</h3>
            <p>{item.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

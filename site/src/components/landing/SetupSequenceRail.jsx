export default function SetupSequenceRail({ variant }) {
  return (
    <section className="section-frame">
      <div className="section-copy">
        <p className="panel-label">{variant.setupSequence.eyebrow}</p>
        <h2 className="section-title">{variant.setupSequence.title}</h2>
        <p className="section-body">{variant.setupSequence.body}</p>
      </div>

      <div className="sequence-rail" aria-label="Setup sequence">
        {variant.setupSequence.steps.map((step) => (
          <article key={step.id} className="sequence-step">
            <span>{step.id}</span>
            <h3>{step.title}</h3>
          </article>
        ))}
      </div>
    </section>
  );
}

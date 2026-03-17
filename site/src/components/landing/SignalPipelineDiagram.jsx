export default function SignalPipelineDiagram({ variant }) {
  return (
    <section className="section-frame" id="signal-pipeline">
      <div className="section-copy">
        <p className="panel-label">{variant.pipeline.eyebrow}</p>
        <h2 className="section-title">{variant.pipeline.title}</h2>
        <p className="section-body">{variant.pipeline.body}</p>
      </div>

      <div className="pipeline-diagram" aria-label="Signal pipeline">
        {variant.pipeline.stages.map((stage, index) => (
          <article key={stage.id} className="pipeline-stage">
            <div className="pipeline-stage-top">
              <span>{stage.id}</span>
              <span>{index < variant.pipeline.stages.length - 1 ? "->" : "OK"}</span>
            </div>
            <h3>{stage.label}</h3>
            <p>{stage.body}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

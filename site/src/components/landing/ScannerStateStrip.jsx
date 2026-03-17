export default function ScannerStateStrip({ variant }) {
  return (
    <section className="state-strip-frame">
      {variant.stateStrip.map((item) => (
        <article key={item.label} className="state-cell">
          <span>{item.label}</span>
          <strong>{item.value}</strong>
        </article>
      ))}
    </section>
  );
}

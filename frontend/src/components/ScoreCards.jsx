export function ScoreCards({ summary, attackRate, runs }) {
  const cards = [
    { label: 'Composite Score', value: summary ?? 0 },
    { label: 'Attack Success Rate', value: attackRate ?? 0 },
    { label: 'Total Runs', value: runs ?? 0, raw: true },
  ];

  return (
    <section className="card-grid">
      {cards.map((c) => (
        <article className="metric-card" key={c.label}>
          <p>{c.label}</p>
          <h2>{c.raw ? c.value : `${Math.round((c.value || 0) * 100)}%`}</h2>
        </article>
      ))}
    </section>
  );
}

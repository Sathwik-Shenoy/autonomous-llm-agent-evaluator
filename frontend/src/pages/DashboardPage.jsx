import { useMemo, useState } from 'react';
import { DifficultyProgressionChart } from '../components/DifficultyProgressionChart';
import { FailureLogTable } from '../components/FailureLogTable';
import { ModelComparisonChart } from '../components/ModelComparisonChart';
import { ScoreCards } from '../components/ScoreCards';
import { fetchBenchmarks, runQuickEvaluation } from '../services/api';

export function DashboardPage() {
  const [latest, setLatest] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const modelData = useMemo(() => {
    if (!latest?.metadata?.benchmark?.model_scores) return [];
    return Object.entries(latest.metadata.benchmark.model_scores).map(([model, score]) => ({ model, score }));
  }, [latest]);

  const difficultyData = useMemo(() => {
    if (!latest?.results) return [];
    return latest.results.map((r, idx) => ({ index: idx + 1, difficulty: r.difficulty }));
  }, [latest]);

  const failureRows = useMemo(() => {
    if (!latest?.results) return [];
    return latest.results.flatMap((r) =>
      (r.failures || []).map((f) => ({
        agent: r.agent.name,
        category: f.category,
        reason: f.reason,
        score: r.score.weighted_total,
      }))
    );
  }, [latest]);

  async function onRun() {
    setLoading(true);
    setError('');
    try {
      const data = await runQuickEvaluation();
      setLatest(data);
    } catch (e) {
      setError('Unable to run evaluation. Ensure backend is up.');
    } finally {
      setLoading(false);
    }
  }

  async function onLoadBenchmarks() {
    setLoading(true);
    setError('');
    try {
      const data = await fetchBenchmarks();
      if (data.length > 0) {
        const top = data[0];
        setLatest({
          metadata: { benchmark: top },
          results: [],
          overall_score: Object.values(top.model_scores || {}).reduce((a, b) => a + b, 0) / Math.max(1, Object.keys(top.model_scores || {}).length),
          attack_success_rate: Object.values(top.attack_success_rate || {}).reduce((a, b) => a + b, 0) / Math.max(1, Object.keys(top.attack_success_rate || {}).length),
        });
      }
    } catch (e) {
      setError('Unable to fetch benchmarks.');
    } finally {
      setLoading(false);
    }
  }

  return (
    <main className="layout">
      <header className="hero">
        <p className="kicker">Autonomous LLM Agent Evaluator</p>
        <h1>Adversarial Simulation Command Center</h1>
        <p>
          Red Team attacks, Blue Team defense scoring, and evolving scenario difficulty in a single operational view.
        </p>
        <div className="actions">
          <button onClick={onRun} disabled={loading}>{loading ? 'Running...' : 'Run Evaluation'}</button>
          <button className="secondary" onClick={onLoadBenchmarks} disabled={loading}>Load Stored Benchmarks</button>
        </div>
        {error && <p className="error">{error}</p>}
      </header>

      <ScoreCards
        summary={latest?.overall_score || 0}
        attackRate={latest?.attack_success_rate || 0}
        runs={latest?.results?.length || 0}
      />

      <section className="grid-2">
        <ModelComparisonChart data={modelData} />
        <DifficultyProgressionChart data={difficultyData} />
      </section>

      <FailureLogTable rows={failureRows} />
    </main>
  );
}

import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1',
  timeout: 10000,
});

export async function fetchBenchmarks() {
  const { data } = await api.get('/benchmarks');
  return data.benchmarks || [];
}

export async function runQuickEvaluation() {
  const payload = {
    environment: 'customer_support',
    agents: [
      { name: 'rule-safe-agent', model_provider: 'local', model_name: 'rule-based' },
      { name: 'vulnerable-agent', model_provider: 'local', model_name: 'rule-based' }
    ],
    config: {
      runs_per_agent: 2,
      initial_difficulty: 0.4,
      difficulty_step: 0.1,
      max_turns: 4,
      metric_weights: {
        correctness: 0.25,
        robustness: 0.2,
        hallucination: 0.2,
        consistency: 0.15,
        safety: 0.2
      },
      use_llm_judge: false
    }
  };
  const { data } = await api.post('/evaluations/run', payload);
  return data;
}

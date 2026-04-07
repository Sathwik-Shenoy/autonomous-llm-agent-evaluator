# Autonomous LLM Agent Evaluator via Adversarial Simulation

Production-grade framework for evaluating LLM agents in adversarial, multi-turn environments.

## What This System Does

- Simulates realistic evaluation environments:
  - Code Review
  - Financial Decision-Making
  - Customer Support
- Generates adversarial user inputs with mutation strategies:
  - Prompt injection
  - Conflicting instructions
  - Hidden constraints
  - Misleading facts
- Scores agent performance with normalized metrics (0-1):
  - Correctness
  - Robustness
  - Hallucination resistance
  - Consistency
  - Safety
- Supports Red Team vs Blue Team runs and attack success tracking
- Evolves scenario difficulty over time using failure-driven feedback
- Benchmarks multiple models/agents and stores historical summaries
- Provides a frontend dashboard for operational visibility
- Supports live model benchmarking through OpenAI and Hugging Face inference adapters

## Architecture

### Backend (FastAPI)

- `app/domain/environments/`: environment simulation engine (pluggable)
- `app/domain/adversarial/`: adversarial prompt generation and evolution
- `app/domain/evaluation/`: weighted scoring + optional LLM judge
- `app/domain/benchmark/`: model comparison aggregation
- `app/domain/failures/`: failure analysis and replay candidates
- `app/services/`: orchestration layer (clean architecture boundary)
- `app/storage/`: async SQLAlchemy persistence layer
- `app/workers/`: Celery async task workers
- `app/api/routes/`: REST endpoints

### Frontend (React + Vite)

- Real-time run trigger
- Score cards
- Model comparison chart
- Scenario difficulty progression chart
- Failure case logs

### Infra

- Redis for queue backend/cache
- Celery for async execution
- Docker Compose for full stack orchestration

## APIs

- `POST /api/v1/evaluations/run` - synchronous evaluation execution
- `POST /api/v1/evaluations/run-async` - enqueue async evaluation job
- `GET /api/v1/evaluations/{evaluation_id}` - fetch evaluation result
- `GET /api/v1/benchmarks` - latest model benchmark summaries
- `GET /api/v1/environments` - list registered and plugin-loaded environments
- `GET /health` - health check

## Red Team vs Blue Team Model

- Red Team: `AdversarialUserGenerator` creates attack variants each turn
- Blue Team: candidate agent/model responds in context
- Attack success is measured from safety breaches and policy override behavior

## Self-Improving Loop

- After each run, failure signals update difficulty distribution
- High failure rate increases adversarial intensity
- Low failure rate can reduce difficulty slightly to avoid saturation
- Replay candidates are automatically logged for targeted regression testing
- Strategy selection is guided by a Thompson-sampling curriculum bandit over adversarial mutation types
- Attack outcome feedback updates per-strategy posteriors and changes future attack mix probabilities

## Plugin Environments

Environment plugins can be added under:

`backend/app/domain/environments/plugins/`

Each plugin must subclass `BaseEnvironment`. It is auto-discovered at startup.

## Quick Start (Docker)

1. Copy env file

```bash
cp .env.example .env
```

2. Start full stack

```bash
docker compose up --build
```

3. Access services

- Backend API: http://localhost:8000/docs
- Frontend dashboard: http://localhost:5173

## Local Dev (without Docker)

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Worker

```bash
cd backend
celery -A app.workers.tasks worker --loglevel=info
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Example Evaluation Payload

```json
{
  "environment": "customer_support",
  "agents": [
    { "name": "rule-safe-agent", "model_provider": "local", "model_name": "rule-based" },
    { "name": "vulnerable-agent", "model_provider": "local", "model_name": "rule-based" }
  ],
  "config": {
    "runs_per_agent": 3,
    "initial_difficulty": 0.4,
    "difficulty_step": 0.1,
    "max_turns": 4,
    "metric_weights": {
      "correctness": 0.25,
      "robustness": 0.2,
      "hallucination": 0.2,
      "consistency": 0.15,
      "safety": 0.2
    },
    "use_llm_judge": false
  }
}
```

### OpenAI Agent Payload Example

```json
{
  "environment": "code_review",
  "agents": [
    { "name": "gpt4o-redteam-eval", "model_provider": "openai", "model_name": "gpt-4o-mini" }
  ],
  "config": {
    "runs_per_agent": 2,
    "initial_difficulty": 0.55,
    "max_turns": 4,
    "use_llm_judge": true
  }
}
```

### Hugging Face Agent Payload Example

```json
{
  "environment": "customer_support",
  "agents": [
    { "name": "hf-mistral-eval", "model_provider": "huggingface", "model_name": "mistralai/Mistral-7B-Instruct-v0.3" }
  ],
  "config": {
    "runs_per_agent": 2,
    "initial_difficulty": 0.5,
    "max_turns": 4,
    "use_llm_judge": false
  }
}
```

## Running Tests

```bash
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pytest -q
```

Current tests cover:

- Adversarial generator behavior
- Curriculum-bandit posterior updates
- Scoring normalization
- Model adapter fallback behavior

## Design Decisions

- Clean architecture with clear domain/service/storage boundaries
- Strong typing via Pydantic schemas for API stability
- Async-first backend for scale and queue-friendly workloads
- Pluggable environments for domain expansion
- Rule-based baseline metrics blended with optional LLM-judge scoring
- Persistent benchmark + failure artifacts for trend analysis and replay

## Next Hardening Steps

- Add authn/authz and tenant isolation
- Add LangGraph-based multi-agent evaluator graphs
- Add Prometheus metrics and OpenTelemetry traces
- Add policy-as-code safety checks
- Add RL-based curriculum policy for attack generation

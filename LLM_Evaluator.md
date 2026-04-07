# Interview-Ready Guide: Autonomous LLM Agent Evaluator

This document is designed to be your single-source interview prep for this project.

It covers:
- What problem this project solves
- Full architecture and data flow
- How each module works
- How to run and demo it confidently
- What technical tradeoffs were made
- What interviewers will challenge and how to respond
- How to extend it in real production settings

---

## 1. One-Line Pitch

Autonomous LLM Response Evaluation Framework is a production-style platform that stress-tests model responses in adversarial multi-turn simulations, scores behavior across safety and quality metrics, adapts attack difficulty based on observed failures, and benchmarks models side-by-side.

---

## 2. Problem Statement

Most LLM evaluations are static and optimistic.

Typical weaknesses:
- Single-turn tasks only
- Benchmark leakage and overfitting
- Weak coverage of prompt-injection and policy conflict attacks
- No feedback loop to increase attack sophistication
- No operational dashboard for trend tracking

This project solves those by combining:
- Multi-turn simulation environments
- Red Team adversarial generation
- Blue Team model execution
- Rule-based plus optional LLM-based judging
- Failure-driven curriculum adaptation
- Persistent benchmark history and failure logs

---

## 3. Core Capabilities

1. Simulated Environments
- Code Review
- Financial Decision-Making
- Customer Support
- Plugin system for adding new environments without core rewrites

2. Adversarial User Generation
- Mutation categories: prompt injection, conflicting instruction, hidden constraints, misleading facts, ambiguity, incomplete context
- Scenario randomization per turn
- Difficulty-dependent attack composition
- Strategy adaptation using a bandit-style curriculum

3. Evaluation Engine
- Scores normalized to 0-1
- Metrics: correctness, robustness, hallucination resistance, consistency, safety
- Weighted aggregation for overall score
- Optional LLM judge blending with rule-based metrics
- Robustness is computed from attacked-turn stability and volatility
- Consistency is computed from semantic overlap across turns (token-level set similarity)
- Hallucination heuristics penalize unsupported certainty and fabricated-evidence phrasing

4. Self-Improving Loop
- Attack outcomes update strategy posteriors
- Difficulty adapts from failure signals and strategy pressure
- Replay candidates include failing turn index, attack tags, and exact prompt/response context

5. Benchmarking and Failure Analysis
- Model-to-model score comparison
- Attack success rate comparison
- Failure category summaries
- Historical benchmark retrieval via API

6. Operational UX
- Dashboard shows composite score, attack rate, run count
- Charts for model comparison and difficulty progression
- Failure table for rapid diagnosis

---

## 4. Architecture (Clean, Layered)

### 4.1 Backend Layers

1. API Layer (FastAPI)
- Input validation
- Endpoint contracts
- Sync and async evaluation triggers

2. Service Layer
- Evaluation orchestration
- Environment registry and plugin loading
- Agent factory

3. Domain Layer
- Environment simulation logic
- Adversarial generation and curriculum
- Scoring and judging
- Benchmark aggregation
- Failure analysis

4. Storage Layer
- SQLAlchemy async persistence
- Evaluation records
- Benchmark snapshots
- Failure records

5. Worker Layer
- Celery worker for queued execution
- Redis broker/result backend

### 4.2 Frontend Layer

React + Vite dashboard:
- Trigger evaluations
- Load benchmark snapshots
- Display score cards and charts
- Show failure case logs

### 4.3 Infra

- Docker Compose orchestrates backend, frontend, worker, redis
- Environment variables via .env
- Local SQLite for fast setup; swappable for Postgres

---

## 5. End-to-End Request Lifecycle

### 5.1 Synchronous Run Path

1. Client sends POST /api/v1/evaluations/run.
2. FastAPI validates payload with Pydantic schemas.
3. EvaluationService resolves environment and model adapters.
4. Scenario is created at current difficulty.
5. For each turn:
- Red Team generates adversarial prompt
- Blue Team agent responds
- Environment computes per-turn correctness component
6. Evaluator computes final metric vector and weighted total.
7. Red Team success flag is inferred from safety breaches.
8. Curriculum observes outcome and updates future attack strategy probabilities.
9. Difficulty is evolved for next run.
10. Results are persisted and benchmark summary is generated.
11. Response returns full run artifacts plus metadata.

### 5.2 Async Run Path

1. Client sends POST /api/v1/evaluations/run-async.
2. API enqueues Celery task.
3. Worker executes same orchestration logic.
4. Worker handles async execution safely even if an event loop is already active.
5. Result is stored and retrievable by evaluation ID.

---

## 6. Data Model and Scoring Semantics

### 6.1 Key Runtime Objects

1. EvaluationRunRequest
- environment
- agents
- config (runs, max turns, weights, judge mode)

2. AgentRunResult
- scenario_id
- difficulty
- turn records
- score breakdown
- red_team_success
- failures

3. EvaluationRunResponse
- overall score
- global attack success rate
- per-agent results
- metadata (benchmark summary, replay candidates, strategy mix)

### 6.2 Score Math

Each metric is normalized to [0, 1].

Weighted total:

S = sum(w_i * m_i)

where:
- m_i are metric values
- w_i are normalized weights from request config

If LLM judge is enabled:
- Rule-based scores remain baseline
- LLM scores are blended by metric to reduce brittle single-judge behavior

---

## 7. Adversarial Curriculum (Interview-Critical)

This is not a static difficulty += 0.1 loop.

Implemented behavior:
1. Each mutation strategy has a posterior (alpha, beta).
2. Strategy selection uses Thompson sampling.
3. Attack success updates posteriors:
- success -> alpha++
- failure -> beta++
4. Difficulty adaptation uses:
- observed failure rate
- strategy pressure (mean posterior success)
- exploration entropy
5. Output includes strategy mix telemetry.

Interview framing:
- This approximates online curriculum adaptation without full RL infra.
- It is computationally cheap and easy to reason about.
- It supports progressive hardening and regression replay loops.

---

## 8. Model Provider Support

### 8.1 Local Baseline Agents

1. rule-safe-agent
- Safer policy behavior
- Good baseline for attack resistance

2. vulnerable-agent
- Intentionally weak behavior
- Useful as a control to verify evaluator sensitivity

### 8.2 OpenAI Adapter

- Async chat completions
- Uses configured model name
- Enables real-world model benchmarking

### 8.3 Hugging Face Inference Adapter

- Calls HF Inference API with token auth
- Supports evaluating open-source models through hosted inference

Interview framing:
- Local control agents validate evaluator calibration.
- External adapters validate real model behavior in the same harness.

---

## 9. APIs You Should Memorize

1. GET /health
- Health status

2. GET /api/v1/environments
- Registered environments including plugins

3. POST /api/v1/evaluations/run
- Synchronous evaluation

4. POST /api/v1/evaluations/run-async
- Queue-based evaluation

5. GET /api/v1/evaluations/{evaluation_id}
- Fetch stored evaluation result

6. GET /api/v1/benchmarks
- Retrieve benchmark snapshots

---

## 10. Dashboard Walkthrough (Demo Script)

Use this exact sequence in interviews:

1. Open dashboard and explain objective:
- Red Team attacks and Blue Team scoring in one control plane.

2. Click Run Evaluation:
- Mention this hits synchronous evaluation endpoint.

3. Explain score cards:
- Composite score, attack success rate, run count.

4. Explain model comparison chart:
- Side-by-side score by provider:model:agent key.

5. Explain difficulty progression:
- Shows curriculum trend over run index.

6. Explain failure logs:
- Categories: logic, hallucination, safety, robustness, consistency.

7. Open backend docs:
- Show typed API contracts and endpoints.

8. (Optional) show async path:
- Trigger /run-async and check worker logs.

---

## 11. How to Run Locally

### 11.1 Docker

1. Copy environment file.
2. docker compose up --build
3. Open:
- API docs at localhost:8000/docs
- Dashboard at localhost:5173

### 11.2 Backend only

1. Create venv and install requirements.
2. Run uvicorn app.main:app --reload
3. Start worker separately for async path.

### 11.3 Tests

Run pytest in backend.

Current suite covers:
- Scoring behavior
- Adversarial generator behavior
- Curriculum updates
- Model adapter fallback behavior
- Safety scoring behavior and breach attribution
- Replay candidate turn-level diagnostics

---

## 12. Why This Looks Production-Grade

1. Clear module boundaries and separation of concerns
2. Typed schemas and normalized outputs
3. Async processing support (API + worker)
4. Persistent records for audits and trend analysis
5. Pluggable environments
6. Real model provider adapters
7. Explicit safety-oriented metrics
8. Dashboard for non-technical stakeholders

---

## 13. Known Limitations (Say This Honestly)

1. Rule-based scoring still exists and can be gamed by lexical mimicry.
2. LLM judge reliability depends on prompt design and model stability.
3. SQLite is convenient for local/dev, not ideal for scaled concurrency.
4. No auth/tenant isolation yet.
5. No full observability stack yet (metrics/traces/log pipelines).

Interview framing:
- These are intentional scope boundaries for a first production-style iteration.
- Architecture already leaves clear extension points.

---

## 14. High-Value Next Steps

1. Replace SQLite with Postgres + Alembic migrations
2. Add authn/authz and tenant-scoped evaluation datasets
3. Add LangGraph workflow for evaluator pipelines
4. Add policy packs and external safety validators
5. Add richer replay harness and regression suite snapshots
6. Add OTel tracing + Prometheus metrics
7. Add automated report generation per benchmark run

---

## 15. Interview Q&A Prep

### Q1: Why not just use a benchmark dataset?
Because static datasets do not capture interactive failure modes like prompt injection escalation and conflicting constraints across turns.

### Q2: How do you prevent evaluator leakage?
By rotating scenario templates, randomizing adversarial mutations, and adapting strategy mix from outcomes.

### Q3: Is the self-improving loop real?
Yes. It updates mutation strategy posteriors online and evolves difficulty from observed outcomes and exploration pressure.

### Q4: How do you compare models fairly?
Same environment, same run config, same metric weighting, same orchestration path. Provider adapters are abstractions over identical interfaces.

### Q5: What makes this scalable?
Async-first design, queue workers, separable compute path, and persistent benchmark artifacts. Storage and model backends are swappable.

### Q6: How is safety measured?
Prompt injection and unsafe compliance are scored from behavioral signals (unsafe compliance language plus weak refusal patterns on attacked turns), and attack success rates are tracked per model with turn-level failure attribution.

### Q7: Is hallucination detection fact-grounded?
Not fully. Current implementation is a lightweight hallucination-risk proxy based on unsupported certainty and fabricated-evidence phrasing. It is explicitly documented as proxy scoring, not full retrieval-based fact verification.

### Q8: Accuracy of what?
Task accuracy is explicitly defined as mean reference-overlap exactness against benchmark dataset reference answers across repeated trials. Evaluator reliability is separately reported via Pearson/Spearman correlation against dataset human_score labels.

---

## 16. 60-Second Elevator Answer

I built an autonomous LLM evaluation platform that simulates adversarial multi-turn environments and benchmarks agents under stress. It uses a Red Team generator to craft prompt injections, conflicting instructions, and misleading constraints, and a Blue Team model adapter layer to test local, OpenAI, or Hugging Face models through one interface. Each run is scored on correctness, robustness, hallucination resistance, consistency, and safety, with normalized weighted metrics. The system has a feedback loop where attack outcomes update a bandit-based curriculum, changing future strategy distributions and difficulty. Results are persisted, benchmarked over time, and visualized in a React dashboard with failure logs and model comparison charts. The architecture is modular, async-capable, dockerized, and designed for extension to enterprise-grade evaluation workflows.

The latest version also hardens weak spots by replacing length-based proxies with behavior-aware scoring heuristics, adding adversarial phrase diversification, and surfacing replay-ready turn context for failure-driven debugging.

---

## 17. Final Interview Checklist

Before interview:
1. Ensure docker compose stack is running.
2. Verify /health and /docs.
3. Run one live evaluation from dashboard.
4. Show benchmark retrieval endpoint.
5. Be ready to explain bandit curriculum and metric weighting.
6. Be transparent about current limitations and next steps.

If you can explain sections 3, 5, 7, 10, and 15 clearly, you are interview-ready for this project.

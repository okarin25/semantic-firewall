# 🛡️ Semantic Firewall

> **Enterprise AI Gateway Platform for Cost Optimization, Semantic Caching, AI Governance & Observability**

Semantic Firewall is an enterprise-grade AI Gateway that sits between your applications and Large Language Model (LLM) providers such as OpenAI, Azure OpenAI, Anthropic, Gemini, Groq, DeepSeek, Ollama, and OpenRouter.

Instead of sending every request directly to an LLM, Semantic Firewall intelligently intercepts, analyzes, caches, routes, audits, and monitors every AI request to dramatically reduce costs while improving latency, governance, and operational visibility.

---

# Why Semantic Firewall?

Enterprise organizations are rapidly adopting Generative AI, but face several common challenges:

- 💰 Escalating LLM API costs
- ⚡ High response latency
- 🔁 Duplicate prompts across teams
- 🔒 Lack of AI governance
- 📊 Poor observability into AI usage
- 🔍 No centralized audit trail
- 🔄 Vendor lock-in with a single LLM provider

Semantic Firewall solves these challenges through intelligent middleware that optimizes every AI request before it reaches an LLM.

---

# Key Features

## Semantic Caching

Uses local embeddings and vector similarity search to detect semantically equivalent prompts.

Example:

> "How do I request PTO?"

and

> "Procedure for applying vacation leave"

are recognized as the same intent.

Instead of paying twice, the cached response is returned in milliseconds.

---

## Enterprise AI Gateway

Provides an OpenAI-compatible API endpoint allowing existing applications to migrate with **zero code changes**.

Simply replace:

```
https://api.openai.com/v1
```

with

```
http://semantic-firewall/api/v1
```

---

## Multi-Provider Routing

Supports multiple AI providers through a common abstraction layer.

Current / Planned Providers

- OpenAI
- Azure OpenAI
- Anthropic Claude
- Google Gemini
- Groq
- Ollama
- OpenRouter
- DeepSeek

---

## AI Observability

Track every AI request.

Metrics include:

- Total Requests
- Cache Hit Ratio
- Latency
- Provider Usage
- Token Consumption
- Cost Savings
- API Spend
- Request Timeline

---

## Enterprise Audit Logging

Every request is recorded with:

- Request ID
- Timestamp
- User
- Provider
- Model
- Cache Status
- Similarity Score
- Token Usage
- Estimated Cost
- Response Time

---

## Cost Optimization

Semantic Firewall automatically:

- eliminates duplicate requests
- reduces token usage
- minimizes API spend
- improves latency

Typical enterprise savings:

- 30–60% reduction in LLM API cost
- Up to 80× faster repeated responses

---

# Architecture

```text
                            +-------------------------+
                            |     React Dashboard     |
                            |  Analytics & Monitoring |
                            +------------+------------+
                                         |
                                         |
                         +---------------v----------------+
                         |     Semantic Firewall API      |
                         |        FastAPI Gateway         |
                         +---------------+----------------+
                                         |
         +-------------------------------+-------------------------------+
         |                               |                               |
         |                               |                               |
+--------v--------+            +---------v---------+            +--------v--------+
|  Redis Hot Cache |           |  Qdrant Vector DB |            | PostgreSQL      |
| Exact Prompt Hit |           | Semantic Matching |            | Audit & Metrics |
+------------------+           +-------------------+            +-----------------+
                                         |
                                         |
                                 +-------v--------+
                                 | Provider Layer |
                                 +-------+--------+
                                         |
              +-------------+------------+-------------+--------------+
              |             |                          |              |
          OpenAI      Azure OpenAI                Gemini         Anthropic
```

---

# Technology Stack

## Backend

- Python
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic v2
- AsyncIO

---

## AI Stack

- FastEmbed
- ONNX Runtime
- Qdrant
- OpenAI SDK
- Sentence Transformers (optional)

---

## Infrastructure

- PostgreSQL
- Redis
- Docker
- Docker Compose

---

## Frontend

- Next.js 15
- React 19
- TypeScript
- Tailwind CSS
- Recharts
- Zustand
- TanStack Query
- shadcn/ui

---

## Logging & Observability

- Loguru
- Prometheus
- OpenTelemetry (Roadmap)

---

# Repository Structure

```text
semantic-firewall/

├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── analytics/
│   │   ├── cache/
│   │   ├── core/
│   │   ├── database/
│   │   ├── domain/
│   │   ├── embeddings/
│   │   ├── middleware/
│   │   ├── providers/
│   │   ├── schemas/
│   │   ├── security/
│   │   ├── services/
│   │   └── main.py
│   └── tests/
│
├── frontend/
│
├── docker-compose.yml
│
├── README.md
│
└── .env.example
```

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/yourusername/semantic-firewall.git

cd semantic-firewall
```

---

## Backend Setup

```bash
cd backend

python -m venv venv

# Windows
venv\Scripts\activate

# Linux / macOS
source venv/bin/activate

pip install -r requirements.txt

cp .env.example .env

uvicorn app.main:app --reload
```

---

## Frontend Setup

```bash
cd frontend

npm install

npm run dev
```

---

## Running with Docker

```bash
docker compose up --build
```

---

# Enterprise Use Cases

## Internal Enterprise Chatbot

Reduce duplicate employee questions and API spend.

---

## AI Helpdesk

Cache repetitive IT support requests.

---

## HR Assistant

Answer repeated HR policy questions with semantic matching.

---

## Customer Support AI

Reduce inference cost for repetitive customer interactions.

---

## Banking & Financial Services

Provide AI governance, audit trails, and observability for regulated environments.

---

## Insurance

Accelerate claims and policy assistance while reducing LLM costs.

---

## Healthcare

Centralized AI gateway with compliance-focused logging and analytics.

---

# Roadmap

## Phase 1

- Semantic Cache
- FastAPI Gateway
- OpenAI Compatibility
- Analytics Dashboard

---

## Phase 2

- Redis Hot Cache
- Multi-Provider Support
- Streaming Responses
- Cost Calculator

---

## Phase 3

- RBAC
- JWT Authentication
- Multi-Tenant Support
- Prompt Templates

---

## Phase 4

- Prompt Injection Detection
- PII Detection
- AI Guardrails
- Provider Failover
- Kubernetes Deployment
- Helm Charts

---

# Business Value

Semantic Firewall enables organizations to:

- Reduce AI operational costs
- Improve response latency
- Centralize AI governance
- Gain complete visibility into AI usage
- Standardize LLM access
- Avoid vendor lock-in

---

# License

This project is licensed under the MIT License.

---

# Author

**Arpit Vishwakarma**

AI Engineer | Full Stack Developer | Enterprise AI & Automation

---

⭐ If you find this project useful, consider giving it a star.
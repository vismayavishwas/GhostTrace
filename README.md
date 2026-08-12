# GhostTrace AI - Autonomous Process Intelligence Platform

GhostTrace AI is an autonomous, agentic Process Intelligence and Workflow Automation platform built using Python, FastAPI, LangGraph, Next.js 15, and Google Cloud Vertex AI (Gemini 2.5 / 3.0).

Unlike traditional RPA tools that require manual recording or fragile scripting, GhostTrace AI observes human UI interactions, compresses low-level telemetry into high-level **Workflow DNA**, synthesizes executable Python/Playwright automation code, and features a real-time **self-healing engine** to fix broken UI selectors and schema changes automatically.

---

## 🏗️ Architecture Overview

The platform operates on a 10-state deterministic state machine orchestrated by **LangGraph**:

```
IDLE ➔ OBSERVING ➔ PATTERN_DISCOVERY ➔ INTENT_VALIDATION ➔ WORKFLOW_DNA
  ➔ CODE_GENERATION ➔ SANDBOX ➔ SELF_HEAL ➔ EXECUTION ➔ CONTINUOUS_OBSERVATION
```

### Core Architecture Layers:
1. **Perception Layer**: Shadow observation capturing DOM events, mouse clicks, keystrokes, and application focus.
2. **Intelligence Core (Orchestration)**: LangGraph state machine orchestrating Pattern Mining, Scoring, Intent Disambiguation (HITL), and Workflow DNA Extraction via Vertex AI (Gemini).
3. **Automation Factory**: Code compilation into Python/Playwright scripts, isolated sandbox testing, and automated self-healing.
4. **Execution & Governance**: Production workflow execution, human-in-the-loop approval, and continuous background observation.

---

## 📁 Repository Structure

```
ghosttrace-ai/
├── backend/                  # FastAPI & LangGraph Orchestration Engine
│   ├── app/
│   │   ├── api/              # HTTP Routes & WebSocket Endpoints
│   │   ├── core/             # Configuration & Structured Logging
│   │   ├── graph/            # LangGraph State Machine & Node Definitions
│   │   └── main.py           # FastAPI Application Entrypoint
│   ├── requirements.txt      # Python Dependencies
│   └── .env.example          # Backend Environment Template
│
├── frontend/                 # Next.js 15 Real-time Dashboard
│   ├── src/
│   │   ├── app/              # App Router Pages & Layouts
│   │   ├── components/       # React Flow, Monaco Editor, & UI Widgets
│   │   └── lib/              # Constants & Utility Helpers
│   ├── package.json          # Node Dependencies & Build Scripts
│   └── tailwind.config.ts    # Styling & Design Tokens
│
├── package.json              # Workspace Root Scripts
└── README.md                 # Project Setup & Documentation
```

---

## ⚡ Quick Start

### Prerequisites
* **Python**: 3.11+
* **Node.js**: 18.x or 20.x+
* **npm** or **yarn** / **pnpm**

---

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create environment config
cp .env.example .env

# Run FastAPI Development Server
uvicorn app.main:app --reload --port 8000
```

The backend health check endpoint will be available at `http://localhost:8000/health`.

---

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install Node dependencies
npm install

# Create environment config
cp .env.example .env.local

# Run Next.js Development Server
npm run dev
```

The frontend dashboard will be available at `http://localhost:3000`.

---

## 🛠️ Phase Status

| Phase | Description | Status |
| :--- | :--- | :--- |
| **Phase 1** | Project Foundation, Scaffolding & WebSockets Skeleton | **COMPLETE** |
| **Phase 2** | Perception Layer & Telemetry Ingestion Engine | **COMPLETE** |
| **Phase 3** | Intelligence Core (LangGraph + Vertex AI Gemini) | **COMPLETE** |
| **Phase 4** | Automation Factory (Compiler & Playwright Sandbox) | **COMPLETE** |
| **Phase 5** | Self-Healing Engine & Production Runner | **COMPLETE** |

---

## 🚀 Newly Finished Features & Bug Fixes

The platform has been fully hardened with key production-level enhancements:

### 1. 🤖 Dynamic Ghost Auto-Fill & Replay Engine
- Fixed dynamic record progression: Ghost now auto-fills all 8 sample records sequentially from the current index (instead of hardcoded skips).
- Synchronized record counters: Record numbers (`Record X of Y`) track accurately using active references to prevent state latency.
- State isolation: Fully reset execution triggers (`remainingCount`, `autoStarted`) on domain transitions.

### 2. 🔌 Chrome Extension Detection & Installation
- Direct connection confirmation: Extension `content.js` broadcasts custom ping signals on load.
- User onboarding: The command center automatically shows an installation Call-to-Action banner if the extension is not detected within 4 seconds.

### 3. 🌐 WebSocket Heartbeat & Connection Stability
- Handled heartbeats (`PING`/`PONG` frames) on both back-end and front-end to prevent connections from dropping under Render's idle limits.
- Configured clean disconnect headers (close code `1000`) for graceful teardown.

### 🧪 Testing & CI/CD Validation
- **Front-end**: Full unit testing suite via `Vitest` (`npm run test`).
- **Back-end**: Functional/integration test suite via `pytest` testing telemetry mapping logic and API endpoints.
- **CI/CD**: GitHub Actions pipeline (`.github/workflows/ci.yml`) runs linting, type-checks, tests, and validates Docker builds on every commit.

### ☁️ Production Deployments
- **Front-end Hosting**: Deployed to Firebase Hosting: [https://ghost-trace-4c783.web.app](https://ghost-trace-4c783.web.app)
- **Back-end API & WS**: Deployed and active on Render.


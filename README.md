# Refund Shield AI — AI Customer Support Agent

> Built for the **Workpodd Technical Challenge** — AI Customer Support Agent with LLM-powered refund policy enforcement, real-time reasoning logs, and a voice pipeline.

![Tech Stack](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat-square&logo=fastapi) ![LLM](https://img.shields.io/badge/LLM-Llama%203.3%2070B-purple?style=flat-square) ![Frontend](https://img.shields.io/badge/Frontend-Vanilla%20JS-yellow?style=flat-square) ![Voice](https://img.shields.io/badge/Voice-Web%20Speech%20API-blue?style=flat-square)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     FRONTEND (Port 3000)                    │
│  ┌──────────────────┐  ┌─────────────────────────────────┐  │
│  │   Chat Panel     │  │     Admin Dashboard (CRM)       │  │
│  │ ┌──────────────┐ │  │  ┌──────────┐  ┌────────────┐  │  │
│  │ │ Voice Input  │ │  │  │  Stats   │  │  Orders DB │  │  │
│  │ │ (Web Speech) │ │  │  │  KPIs    │  │  30 entries│  │  │
│  │ └──────────────┘ │  │  └──────────┘  └────────────┘  │  │
│  │  Agent Messages  │  │  Filter | Search | Click-to-refund│ │
│  └──────────────────┘  └─────────────────────────────────┘  │
│  ┌───────────────────────────────────────────────────────┐   │
│  │           Reasoning Logs Sidebar (Slide-out)          │   │
│  │    Timeline: USER_INPUT → TOOL_CALL → TOOL_RESULT →   │   │
│  │             TOOL_CALL → TOOL_RESULT → FINAL_ANSWER    │   │
│  └───────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                         │ HTTP REST API
┌─────────────────────────────────────────────────────────────┐
│                   BACKEND (Port 8000)                       │
│  FastAPI  ←→  Agent Loop  ←→  OpenRouter (Llama 3.3 70B)   │
│                   ↕                                         │
│            Tool Execution Layer                             │
│  ┌────────────────┐  ┌─────────────────────────────────┐   │
│  │  lookup_order  │  │  check_refund_eligibility       │   │
│  │  approve_refund│  │  deny_refund | get_policy       │   │
│  └────────────────┘  └─────────────────────────────────┘   │
│                   ↕                                         │
│            CRM Database (30 profiles, in-memory)            │
└─────────────────────────────────────────────────────────────┘
```

---

## Features

- **LLM Agent Loop** — Function calling via OpenRouter (meta-llama/llama-3.3-70b-instruct), falls back to deterministic simulation if no API key is set
- **5 Tool Capabilities** — `lookup_order`, `check_refund_eligibility`, `approve_refund`, `deny_refund`, `get_policy`
- **Admin Dashboard** — Real-time CRM table with 30 profiles, live status updates, KPI metrics
- **Reasoning Logs** — Step-by-step agent decision timeline in a collapsible sidebar
- **Voice Pipeline** — Web Speech API for voice input + browser TTS for agent spoken responses
- **Policy Modal** — In-app refund policy viewer with color-coded eligible/ineligible rules
- **Live Mode Badge** — Header indicator showing Live LLM vs Simulation mode
- **Quick Test Scenarios** — 8 pre-loaded scenarios covering all policy edge cases
- **Message Queue** — Multiple rapid messages are queued and processed sequentially

---

## Setup & Installation

### Prerequisites
- Python 3.10+
- Node.js (for `npm run dev`)

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd ai-refund-agent

# Activate virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r backend/requirements.txt
```

### 2. Configure API Key

The app works in two modes:

**Mode A: Live LLM (Recommended for demo)**
```env
# .env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```
Get a free key at [openrouter.ai](https://openrouter.ai) — Llama 3.3 70B is very affordable.

**Mode B: Simulation (No API key needed)**  
Remove or leave `OPENROUTER_API_KEY` blank. The agent will run deterministic tool calls with realistic responses.

### 3. Run the App

```bash
npm run dev
```

| Service | URL |
|---------|-----|
| Frontend Dashboard | http://localhost:3000 |
| Backend API | http://localhost:8000 |
| API Docs (Swagger) | http://localhost:8000/docs |

---

## Test Scenarios

### Quick Demo Scenarios (Click the Quick Test buttons in the UI)

| Order ID | Product | Scenario | Expected Decision |
|----------|---------|----------|-------------------|
| **ORD001** | Wireless Headphones | Damaged item, Gold tier, within 45 days | **APPROVED** |
| **ORD002** | Python Course (Digital) | Digital product | **DENIED** — Digital products excluded |
| **ORD003** | Running Shoes | Used item, window expired | **DENIED** — Used item + expired window |
| **ORD005** | Clearance T-Shirt | Sale/clearance item | **DENIED** — Final sale |
| **ORD006** | Smart Watch | Wrong item delivered, Gold tier | **APPROVED** |
| **ORD007** | Coffee Maker | Standard tier, 112 days ago | **DENIED** — Refund window expired |
| **ORD008** | Gaming Mouse | Defective but refunded 81 days ago | **DENIED** — Within 90-day refund limit |
| **ORD011** | Air Purifier | Defective, Gold tier, 11 days | **APPROVED** |

### Additional Order Scenarios

| Order ID | Scenario | Decision |
|----------|----------|----------|
| ORD004 | Not Delivered | DENIED — Delivery pending |
| ORD009 | Yoga Mat, Platinum, Damaged, 42 days | APPROVED |
| ORD015 | Laptop Stand, Gold, Damaged, 72 days | DENIED — Window expired (72 > 45) |
| ORD017 | Winter Jacket, Platinum, Damaged, 50 days | APPROVED (within 45-day Platinum window) |
| ORD018 | SaaS Subscription, Digital | DENIED — Digital |
| ORD020 | Dumbbells, Wrong Item | APPROVED |
| ORD021 | Mechanical Keyboard, Defective, refunded 42 days ago | DENIED — 90-day window |
| ORD023 | Earbuds, Platinum, Damaged, refunded Feb | APPROVED (>90 days since last refund) |
| ORD025 | Designer Shoes, Used | DENIED — Used item |
| ORD029 | Air Fryer, Gold, Defective | APPROVED |

---

## Voice Feature

1. Click the **microphone button** in the chat input
2. Speak your refund request (e.g., "I want a refund for order ORD001")
3. The agent will process and **speak the response aloud** using the browser's TTS
4. Works best in **Chrome or Edge** (Web Speech API support)
5. Voice preferences: Google Neural voices → Microsoft Neural → macOS Siri voices

---

## Project Structure

```
ai-refund-agent/
├── backend/
│   ├── main.py              # FastAPI server, REST endpoints
│   ├── agent.py             # Agent loop (OpenRouter + simulation fallback)
│   ├── tools.py             # 5 tool implementations + schemas
│   ├── crm_data.py          # 30 CRM customer profiles
│   ├── refund_policy.py     # Structured refund policy document
│   └── requirements.txt     # Python dependencies
├── frontend/
│   ├── app.html             # Main SPA — chat + dashboard
│   └── app.css              # Premium dark theme UI
├── .env                     # API keys (not committed)
├── .gitignore               # Excludes .env, venv, __pycache__
├── package.json             # npm scripts for dev server
└── README.md                # This file
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat` | Send message to AI agent |
| `GET` | `/orders` | Get all CRM orders |
| `GET` | `/orders/{id}` | Get specific order |
| `GET` | `/policy` | Get refund policy document |
| `GET` | `/status` | Agent mode, model, session count |
| `POST` | `/reset` | Reset session + CRM state |
| `GET` | `/health` | Health check |

---

## Agent Tool Orchestration

The agent follows this mandatory tool call sequence for every refund request:

```
User Message
     ↓
lookup_order(order_id)          ← Verify order exists in CRM
     ↓
check_refund_eligibility(order_id) ← Validate ALL policy rules
     ↓
[eligible?]
   YES → approve_refund(order_id) → Confirm + timeline to customer
   NO  → deny_refund(order_id, reason) → Explain specific policy violation
```

The LLM **cannot** approve a refund without calling `check_refund_eligibility` first, enforced by the system prompt and tool dependency chain.

---

## Tech Stack

| Component | Technology |
|-----------|-----------|
| LLM | Llama 3.3 70B (via OpenRouter) |
| Agent Framework | Raw function calling / agent loop |
| Backend | FastAPI (Python) |
| Frontend | Vanilla HTML + CSS + JS |
| Voice Input | Web Speech API (SpeechRecognition) |
| Voice Output | Web Speech API (SpeechSynthesis) |
| Fonts | Outfit + Plus Jakarta Sans + JetBrains Mono |
| Icons | Bootstrap Icons |

---

## Notes for Reviewers

- **Simulation Mode**: If no API key is configured, the agent runs a deterministic tool-calling simulation that demonstrates the full flow with realistic responses — all tool calls are real (CRM lookup, eligibility check, approve/deny), only the LLM reasoning step is skipped.
- **Date handling**: All CRM purchase dates are set in June 2026 to match current real-date eligibility windows.
- **Policy enforcement**: The `check_refund_eligibility` tool enforces all 7 policy rules in code — the LLM cannot override them.
- **90-day limit**: ORD008 and ORD021 demonstrate the 90-day refund cooling period edge case.

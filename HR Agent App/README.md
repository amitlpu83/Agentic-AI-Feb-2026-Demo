# HR Management Agent

An AI-powered HR assistant built with **LangGraph**, **FastMCP**, and **GPT-4o-mini**. It classifies employee requests by intent, routes them to specialised tools, and fetches HR policies from a dedicated **MCP server**.

---

## Architecture

```
                    ┌─────────────────────────────┐
                    │      hr_mcp_server.py        │
                    │  (FastMCP — stdio transport) │
                    │                              │
                    │  Resources:                  │
                    │    hr://policies             │
                    │    hr://policies/{topic}     │
                    │                              │
                    │  Tools:                      │
                    │    get_hr_policy()           │
                    │    list_hr_policies()        │
                    └──────────────┬───────────────┘
                                   │ MCP stdio
                    ┌──────────────▼───────────────┐
                    │         hr_agent.py           │
                    │      (LangGraph Agent)        │
                    │                              │
                    │  START                       │
                    │    │                         │
                    │    ▼                         │
                    │  classify_intent             │
                    │    │                         │
                    │    ▼                         │
                    │  hr_agent ──► tools ──┐      │
                    │    ◄────────────────┘      │
                    │    │                         │
                    │    ▼                         │
                    │   END                        │
                    └──────────────┬───────────────┘
                                   │
               ┌───────────────────┼───────────────────┐
               │                   │                   │
    ┌──────────▼──────┐  ┌─────────▼──────┐  ┌────────▼────────┐
    │    api.py        │  │     ui.py       │  │  Claude Code    │
    │  (FastAPI)       │  │  (Streamlit)    │  │  (MCP Client)   │
    │  :8001           │  │  :8502          │  │  via claude mcp │
    └─────────────────┘  └────────────────┘  └─────────────────┘
```

### LangGraph Nodes

| Node | Role |
|---|---|
| `classify_intent` | Structured-output LLM — detects intent and extracts employee ID |
| `hr_agent` | Tool-calling LLM with an intent-specific system prompt |
| `tools` | LangGraph `ToolNode` — executes whichever tools the LLM requested |

### Intents

| Intent | Triggers on |
|---|---|
| `leave_management` | PTO, vacation, sick days, leave requests and balances |
| `policy_question` | Remote work, conduct, compensation, leave rules |
| `onboarding` | New-hire checklists, first-week guides, account setup |
| `recruitment` | Interview questions, job descriptions, hiring advice |
| `performance_review` | Review process, ratings, PIPs, feedback frameworks |
| `general` | Anything that doesn't fit the above |

---

## Project Structure

```
HR Agent App/
├── hr_mcp_server.py   # FastMCP server — HR policies as resources & tools
├── hr_agent.py        # LangGraph agent — state, tools, nodes, graph
├── api.py             # FastAPI server  →  POST /hr/chat
├── ui.py              # Streamlit chat UI
├── requirements.txt   # Python dependencies
└── README.md
```

---

## HR Tools

| Tool | Source | Description |
|---|---|---|
| `get_hr_policy` | MCP server | Fetches policy text via MCP stdio client |
| `check_leave_balance` | hr_agent.py | Returns annual / sick / personal day balances |
| `submit_leave_request` | hr_agent.py | Validates and submits a leave request |
| `get_employee_info` | hr_agent.py | Returns employee profile |
| `generate_onboarding_checklist` | hr_agent.py | Week-by-week checklist with dept-specific items |
| `generate_interview_questions` | hr_agent.py | Behavioral / technical / cultural Qs by role |

### MCP Policy Topics

| Topic | Covers |
|---|---|
| `remote_work` | Remote days, core hours, equipment allowance |
| `leave` | Annual, sick, personal, parental, bereavement |
| `performance` | Review cycle, rating scale, PIPs, merit increases |
| `code_of_conduct` | Respect, harassment, conflicts of interest |
| `compensation` | Equity, health insurance, 401(k), L&D budget |

---

## Setup

### 1. Install dependencies

```bash
cd "HR Agent App"
pip install -r requirements.txt
```

### 2. Environment variables

The agent loads `.env` from the **project root** (one level up):

```
OPENAI_API_KEY=sk-...
```

---

## Running the App

Run each component in a **separate terminal**, in this order:

### Step 1 — MCP Policy Server

The MCP server must be running before the agent can fetch policies.

```bash
cd "HR Agent App"
python hr_mcp_server.py
```

The server starts in **stdio mode** — it stays alive and waits for connections.

### Step 2 — FastAPI Server (REST API)

```bash
cd "HR Agent App"
python api.py
# → http://localhost:8001
```

**Endpoints:**

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Health check |
| `POST` | `/hr/chat` | Submit an HR request |

**Request body:**
```json
{
  "message": "What is the remote work policy?",
  "employee_id": "E001"
}
```

**Response:**
```json
{
  "answer": "The remote work policy allows up to 3 days per week...",
  "intent": "policy_question",
  "tools_used": ["get_hr_policy"],
  "employee_id": "E001"
}
```

### Step 3 — Streamlit Chat UI

```bash
cd "HR Agent App"
streamlit run ui.py --server.port 8502
```

Open [http://localhost:8502](http://localhost:8502)

**Sidebar features:**
- Select an employee context (E001 – E004) to auto-pass the employee ID
- Quick-prompt buttons for common HR tasks
- Expandable "Tools used" panel on each response

---

## MCP Inspector (Debugging)

Use the MCP Inspector to test the policy server interactively — browse resources, call tools, and inspect protocol messages.

```bash
# Clear inspector ports and launch (run from HR Agent App folder)
lsof -ti :6274,:6277 | xargs kill -9 2>/dev/null; mcp dev hr_mcp_server.py
```

Inspector opens at **[http://localhost:6274](http://localhost:6274)**

| Inspector Tab | What you can do |
|---|---|
| **Resources** | Read `hr://policies` and `hr://policies/{topic}` |
| **Tools** | Test `get_hr_policy` and `list_hr_policies` live |
| **Notifications** | View server logs and protocol messages |

---

## Claude Code Integration

The MCP server is registered with Claude Code for this project:

```bash
# Already configured — verify with:
claude mcp list
```

Configuration stored in `~/.claude.json` under this project:
```json
"hr-policies": {
  "type": "stdio",
  "command": "python3",
  "args": ["/Users/trainer/Agentic AI Feb 2026/HR Agent App/hr_mcp_server.py"]
}
```

Claude Code can now call `get_hr_policy` and `list_hr_policies` directly without the Streamlit UI or FastAPI server.

---

## Example Queries

| Query | Intent | Tools Called |
|---|---|---|
| `What is my leave balance?` | `leave_management` | `check_leave_balance` |
| `Submit annual leave for E001 from 2024-04-01 to 2024-04-05` | `leave_management` | `submit_leave_request` |
| `What is the remote work policy?` | `policy_question` | `get_hr_policy` (via MCP) |
| `Generate an onboarding checklist for a new engineer starting 2024-03-01` | `onboarding` | `generate_onboarding_checklist` |
| `Give me behavioral interview questions for a Senior Software Engineer` | `recruitment` | `generate_interview_questions` |
| `How does the performance review process work?` | `performance_review` | `get_hr_policy` (via MCP) |

---

## Mock Employee Data

| ID | Name | Role | Department |
|---|---|---|---|
| E001 | Alice Johnson | Senior Engineer | Engineering |
| E002 | Bob Smith | Marketing Manager | Marketing |
| E003 | Carol White | VP Engineering | Engineering |
| E004 | David Brown | CMO | Marketing |

---

## Tech Stack

| Component | Library |
|---|---|
| Agent framework | `langgraph` |
| MCP server | `mcp[cli]` (FastMCP) |
| LLM | `langchain-openai` (GPT-4o-mini) |
| API server | `fastapi` + `uvicorn` |
| Chat UI | `streamlit` |
| Env management | `python-dotenv` |

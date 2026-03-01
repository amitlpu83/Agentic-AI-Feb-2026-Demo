# Phidata Agent Demo

A collection of AI agent examples using [Phidata](https://www.phidata.com/) and OpenAI GPT-4o.

## Prerequisites

- Python 3.8+
- An OpenAI API key

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file with your API key:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

> **Note:** `tmp/` (LanceDB vector store) and `.env` are excluded from git via `.gitignore`.

---

## Examples

### 1. `basic.py` — Simple conversational agent

A minimal agent named Jarvis that answers questions directly.

```bash
python basic.py
```

---

### 2. `agent_with_websearch.py` — Web search + scraping agent

Jarvis extended with three tools:

| Tool | Purpose |
|------|---------|
| `DuckDuckGo` | Search the web for snippets and URLs |
| `Newspaper4k` | Extract full article text from a URL |
| `scrape_webpage` | Custom scraper — fetches raw visible text from any HTTP/HTTPS URL using stdlib only |
| `get_current_datetime` | Returns the current date/time for time-sensitive queries |

```bash
python agent_with_websearch.py
```

#### Tool Interaction Sequence

```mermaid
sequenceDiagram
    actor User
    participant Agent as Jarvis (Phidata Agent)
    participant LLM as GPT-4o (OpenAI)
    participant DateTime as get_current_datetime
    participant DDG as DuckDuckGo
    participant News as Newspaper4k
    participant Scraper as scrape_webpage

    User->>Agent: Submit query (e.g. "new Hollywood movies")
    Agent->>LLM: Forward query + tool definitions + instructions
    LLM-->>Agent: Tool call: get_current_datetime()
    Agent->>DateTime: Execute get_current_datetime()
    DateTime-->>Agent: "2026-03-01 10:45:00"
    Agent->>LLM: Return current date/time
    LLM-->>Agent: Tool call: DuckDuckGo.search(query)
    Agent->>DDG: Execute web search
    DDG-->>Agent: Search results (titles, snippets, URLs)
    Agent->>LLM: Return search results
    LLM-->>Agent: Tool call: Newspaper4k.read_article(url)
    Agent->>News: Scrape full article from URL
    News-->>Agent: Full article content
    Agent->>LLM: Return article content
    LLM-->>Agent: Tool call: scrape_webpage(url) [fallback]
    Agent->>Scraper: Fetch raw page text
    Scraper-->>Agent: Visible text (up to 8,000 chars)
    Agent->>LLM: Return scraped text
    LLM-->>Agent: Final synthesised response (streamed)
    Agent-->>User: Stream formatted markdown response
```

---

### 3. `agent_with_kb.py` — Knowledge base (RAG) agent

Loads a local text file into a LanceDB vector store and answers questions using retrieval-augmented generation.

```bash
python agent_with_kb.py
```

**How it works:**
- Chunks `data/sample_article.txt` into 512-token pieces (64-token overlap)
- Embeds chunks using `text-embedding-3-small`
- Stores vectors in `tmp/lancedb/` (gitignored)
- Agent searches the KB before answering (`search_knowledge=True`)

> **Known compatibility issue:** `SearchType.hybrid` requires `pylance`, which conflicts with `lancedb 0.29.2`. Use `SearchType.vector` (the current default) to avoid this.

---

### 4. `agent_team.py` — Multi-agent team

A team of specialised agents coordinated by a Team Leader:

| Agent | Role | Tools |
|-------|------|-------|
| Jarvis (web agent) | Research & web search | DuckDuckGo |
| Financial Analyst | Market & stock analysis | YFinanceTools |
| Team Leader | Delegates tasks, synthesises answers | — |

```bash
python agent_team.py
```

---

## Files

| File | Description |
|------|-------------|
| `basic.py` | Minimal conversational agent |
| `agent_with_websearch.py` | Web search, scraping, and datetime tools |
| `agent_with_kb.py` | RAG agent with LanceDB knowledge base |
| `agent_team.py` | Multi-agent team with web + finance specialists |
| `data/sample_article.txt` | Sample article loaded into the knowledge base |
| `requirements.txt` | Python dependencies |
| `.gitignore` | Excludes `tmp/` (LanceDB) and `.env` |

---

## Dependencies

| Package | Used by |
|---------|---------|
| `phidata` | All — agent framework |
| `openai` | All — GPT-4o LLM + embeddings |
| `python-dotenv` | All — load API keys from `.env` |
| `duckduckgo-search` | `agent_with_websearch.py`, `agent_team.py` |
| `newspaper4k` | `agent_with_websearch.py` |
| `yfinance` | `agent_team.py` |
| `lancedb` | `agent_with_kb.py` — vector store |
| `sqlalchemy` | `agent_with_kb.py` — lancedb dependency |

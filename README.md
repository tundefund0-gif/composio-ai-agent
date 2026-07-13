# 🤖 Zen Agent

An AI agent with access to **23,790+ tools** via Composio, powered by the OpenCode AI API.

## ✨ Features

- **🧠 AI Agent** — Streaming chat with reasoning, tool calling, and code execution
- **🔧 23,790+ Tools** — GitHub, Gmail, Slack, Notion, Google Sheets, Linear, Jira, and more
- **💻 Web Dashboard** — Beautiful chat UI with dark/light theme, mobile responsive
- **⌨️ CLI Mode** — Interactive terminal chat with commands
- **🔌 REST API + WebSocket** — Full API for programmatic access
- **🐍 Code Sandbox** — Execute Python code remotely via Composio

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- An OpenCode API key
- A Composio API key

### 1. Clone & Install
```bash
git clone https://github.com/tundefund0-gif/zen-agent.git
cd zen-agent
pip install -r requirements.txt
```

### 2. Set API Keys
```bash
# Either export them:
export OPENGATE_API_KEY="your-key"
export COMPOSIO_API_KEY="your-composio-key"

# Or copy .env.example to .env and fill in
cp .env.example .env
```

### 3. Run Web Dashboard
```bash
./start.sh
# OR: python3 -m server.main
# OR: python3 run.py web
# Open http://localhost:8000
```

### 4. Run CLI Mode
```bash
# Interactive chat
python3 -m cli.main

# One-shot question
python3 -m cli.main --oneshot "What can you do?"

# Search for tools
python3 -m cli.main tools "manage github issues"
```

## 🖥️ Web Dashboard

The dashboard features:
- **Dark/Light theme** — Toggle with the 🌓 button
- **Chat history** — Stored in browser (localStorage)
- **Streaming responses** — Real-time token streaming via WebSocket
- **Tool call cards** — Collapsible tool execution details
- **Thinking indicator** — See the AI's reasoning process
- **Mobile responsive** — Works on phones and tablets

## 📡 API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check |
| `/api/chat` | POST | Send a message |
| `/api/session/{user_id}` | GET | Get session info |
| `/api/session/{user_id}/reset` | POST | Reset conversation |
| `/api/tools/list` | GET | List Composio tools |
| `/api/tools/search` | GET | Search tools |
| `/ws/chat/{user_id}` | WS | Streaming chat |
| `/` | GET | Dashboard UI |

## 🧪 Running Tests

```bash
# Run all tests
python3 -m pytest tests/ -v

# Run specific test
python3 -m pytest tests/test_agent.py -v

# Stress test (41 tests)
python3 tests/stress_test.py
```

## 📁 Project Structure

```
zen-agent/
├── core/                  # Core engine
│   ├── agent.py            # AI agent orchestration
│   ├── llm_client.py       # OpenCode/OpenAI API client
│   └── composio_client.py  # Composio REST API wrapper
├── cli/                   # CLI interface
│   └── main.py             # Typer-based interactive CLI
├── server/                # Web server
│   ├── main.py             # FastAPI app (REST + WebSocket)
│   └── static/index.html   # Dashboard (single-file SPA)
├── tests/                 # Test suite (29+ tests)
├── config.py              # Environment-based configuration
├── start.sh               # One-command launcher
├── run.py                 # Unified launcher
└── requirements.txt       # Python dependencies
```

## 🔌 Composio Integration

The agent uses the Composio v3/v3.1 REST API directly (no SDK required):

- **Sessions** — Create, retrieve, reuse per user
- **Meta tools** — SEARCH, EXECUTE, MANAGE_CONNECTIONS, WORKBENCH, BASH
- **Tool execution** — Execute any of 23,790+ tools by slug
- **Sandbox** — Run Python code in a remote sandbox
- **Multi-execute** — Run several tools in parallel
- **Proxy** — Make HTTP requests through connected accounts

## 🤝 Need Help?

- Open an issue on GitHub
- Check the Composio docs for tool-specific questions
- The dashboard health page shows system status

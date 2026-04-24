# ⚡ ForgeAI — Autonomous Agentic Intelligence

> *Built by humans. Thinks for itself.*

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue?style=flat-square&logo=python)](https://python.org)
[![Flask](https://img.shields.io/badge/Framework-Flask-black?style=flat-square&logo=flask)](https://flask.palletsprojects.com)
[![LLM Powered](https://img.shields.io/badge/LLM-Tool--Calling%20Agent-orange?style=flat-square)]()
[![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)]()
[![License](https://img.shields.io/badge/License-MIT-lightgrey?style=flat-square)]()

---

## 🧠 What is ForgeAI?

**⚡ ForgeAI** is a custom-built Agentic AI system — not a chatbot, not a wrapper around ChatGPT — a fully autonomous agent that receives a high-level goal, reasons about it, selects the right tools, executes actions, observes outcomes, and iterates until the task is complete.

Most people interact with AI reactively: you prompt, it responds, the conversation ends. ForgeAI is different. It operates in a **Perceive → Think → Act → Observe** loop, making it capable of handling complex, multi-step workflows without human intervention at each step.

Think of it this way:
> *ChatGPT gives you the plan. ForgeAI executes it.*

---

## 🚀 Key Features

- ⚡ **Autonomous Reasoning Loop** — Agent iterates through tasks using the ReAct (Reasoning + Acting) pattern until the goal is achieved
- 🛠️ **Tool-Augmented Intelligence** — Equip the agent with any tool: web search, file I/O, APIs, calculators, databases
- 🔁 **Dynamic Decision Making** — Unlike fixed chains, ForgeAI decides at runtime which action to take next based on live observations
- 🌐 **Browser-Accessible Interface** — Interact with the agent through a clean web UI served locally on Chrome
- 🔌 **LLM Agnostic** — Swap the underlying model (OpenAI, Anthropic, local LLMs) without touching agent logic
- 💰 **Cost-Controlled Execution** — You define exactly when and how many LLM calls are made via max iteration limits
- 🔐 **Secure Config** — API keys and secrets managed via `.env`, never hardcoded
- 🧩 **Modular Architecture** — Clean separation between server logic, agent reasoning, and tool definitions

---

## 📁 Project Structure

```
forgeai/
│
├── app.py              # 🏗️ Core application — server init, LLM loader, tool registry, API endpoints
├── logic.py            # 🧠 Agent reasoning loop — ReAct pattern, tool dispatch, observation handling
│
├── tools/              # 🛠️ Individual tool definitions (web search, file reader, API caller, etc.)
├── templates/          # 🌐 Frontend HTML served to the browser
├── static/             # 🎨 CSS, JS, and UI assets
│
├── requirements.txt    # 📦 All Python dependencies
├── .env                # 🔐 API keys and environment secrets (never committed to git)
├── config.yaml         # ⚙️ Agent configuration — model name, max iterations, tool toggles
└── README.md           # 📖 You are here
```

---

## 🏗️ Architecture Deep Dive

### `app.py` — The Engine
This is the heart of ForgeAI. It does five things:
1. **Initializes the LLM** — loads the model with your chosen provider and parameters
2. **Registers Tools** — builds the JSON schema descriptions that tell the LLM what tools are available and how to call them
3. **Boots the Web Server** — Flask/FastAPI instance that keeps the application alive and listening
4. **Exposes the API Endpoint** — the `/run` route receives user goals from the browser and passes them to the agent
5. **Returns structured responses** — streams or returns the final agent output back to the frontend

### `logic.py` — The Brain
This is where intelligence lives. It implements the **ReAct loop**:
- Accepts a goal and available tools
- Prompts the LLM to reason about the next action
- Parses the LLM's tool-call output
- Executes the tool and captures the observation
- Feeds the observation back into context and repeats
- Exits when the agent signals task completion or max iterations is hit

### The ReAct Pattern — How ForgeAI Thinks

```
User Goal
    │
    ▼
[THOUGHT]  →  LLM reasons: "I need to search for X first"
    │
    ▼
[ACTION]   →  Agent calls: search_tool("X")
    │
    ▼
[OBSERVATION] → Tool returns: "Result: ..."
    │
    ▼
[THOUGHT]  →  LLM reasons: "Now I have enough to answer"
    │
    ▼
[FINAL ANSWER] → Returned to user
```

This loop is what separates ForgeAI from a standard LLM call. The agent is grounded in real tool outputs at every step.

---

## ⚙️ Setup & Installation

### Prerequisites
- Python 3.10 or higher
- PowerShell (Windows) or Terminal (Mac/Linux)
- Google Chrome browser
- API key for your chosen LLM provider

### Step 1 — Clone the Repository
```powershell
git clone https://github.com/yourusername/forgeai.git
cd forgeai
```

### Step 2 — Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\Activate     # Windows PowerShell
# source venv/bin/activate  # Mac/Linux
```

### Step 3 — Install Dependencies
```powershell
pip install -r requirements.txt
```

### Step 4 — Configure Environment Variables
Create a `.env` file in the root directory:
```env
LLM_API_KEY=your_api_key_here
LLM_MODEL=gpt-4o          # or claude-3-5-sonnet, etc.
MAX_ITERATIONS=10
PORT=5000
```

### Step 5 — Run ForgeAI
```powershell
python app.py
```

### Step 6 — Open in Chrome
```
http://localhost:5000
```

Enter your goal in the interface and watch ⚡ ForgeAI work autonomously.

---

## 🔑 Why ForgeAI Over GPT / Claude / Gemini Directly?

| Capability | ChatGPT / Claude UI | ⚡ ForgeAI |
|---|---|---|
| Multi-step autonomous execution | ❌ | ✅ |
| Real tool integration | Limited | ✅ Full control |
| Custom reasoning logic | ❌ | ✅ |
| LLM provider flexibility | ❌ Locked in | ✅ Swap freely |
| Cost per task control | ❌ | ✅ |
| Domain-specific memory | ❌ | ✅ |
| Deployable on your infra | ❌ | ✅ |
| Full execution auditability | ❌ | ✅ |

Off-the-shelf LLM interfaces are **reactive** — they respond to a single prompt. ForgeAI is **proactive** — it takes a goal and figures out everything needed to complete it.

---

## 🧪 Technical Concepts Used

- **ReAct Pattern** — Interleaved reasoning and tool-acting for reliable task completion
- **JSON Schema Tool Descriptions** — Structured tool definitions the LLM uses to generate valid, parseable calls
- **Observation Injection** — Tool results are fed back into LLM context each iteration
- **Max Iteration Guard** — Prevents infinite loops; agent exits gracefully with partial results
- **Environment-Based Config** — `.env` + `config.yaml` separation for secrets vs. settings
- **REST API Design** — Flask server exposes clean endpoints consumed by the browser frontend

---

## 🛡️ Safety & Reliability

- All tool calls are validated before execution
- Agent loop has a hard iteration ceiling defined in `config.yaml`
- Tool failures are caught and passed back as observations — the agent re-reasons rather than crashing
- API keys are never exposed in code or logs

---

## 🔮 What's Next — Roadmap

- [ ] Long-term memory via vector database (FAISS / Pinecone)
- [ ] Multi-agent orchestration — agents spawning sub-agents
- [ ] Voice input/output interface
- [ ] Task history and audit log dashboard
- [ ] Support for local LLMs (Ollama integration)
- [ ] Docker containerization for one-click deployment

---

## 👥 Built By

| Builder | Role |
|---|---|
| **MANAS SAHU** | Core Architecture, Agent Logic, Backend |
| **DEVSHRI DAMAHE** | Tool Integration, Frontend Interface, Testing |

---

## 📄 License

This project is licensed under the MIT License. See `LICENSE` for details.

---

<div align="center">

**⚡ ForgeAI** — *Where goals become actions.*

*Made with obsession by Manas & Devshri*

</div>

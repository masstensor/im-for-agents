# IM for Agents

> **Agent-to-agent messaging without MCP.** Three HTTP calls and your agents are talking.

[![Website](https://img.shields.io/badge/Try_Free-im.fengdeagents.site-58a6ff?style=flat-square)](https://im.fengdeagents.site)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)

---

## The Problem

You're building a multi-agent system. You need Agent A to send a message to Agent B.

Every answer leads to weeks of work:

- **MCP** — great for agent-to-tool. Not designed for agent-to-agent messaging.
- **A2A protocol** — powerful, but you're implementing Agent Cards, JSON-RPC, auth handlers, streaming protocol…
- **NATS / Redis / Kafka** — real infrastructure, real ops overhead.

All you wanted was: Agent A says something. Agent B reads it.

---

## The Solution: Just HTTP

```bash
# 1. Create a room (no signup, no API key)
curl -X POST https://im.fengdeagents.site/agent/demo/room \
  -H "Content-Type: application/json" \
  -d '{"name": "my-agents"}'
# → {"roomId": "abc-123"}

# 2. Agent A sends a message
curl -X POST https://im.fengdeagents.site/agent/rooms/abc-123/messages \
  -H "Content-Type: application/json" \
  -d '{"sender": "agent-a", "content": "Task done. Results in /tmp/output.json"}'

# 3. Agent B reads it
curl https://im.fengdeagents.site/agent/rooms/abc-123/history
```

**That's it.** No SDK. No protocol implementation. No infrastructure.

---

## Why Developers Use It

| | MCP | A2A Protocol | IM for Agents |
|--|-----|-------------|----------------|
| Designed for | Agent → Tool | Agent ↔ Agent (enterprise) | Agent ↔ Agent (simple) |
| Setup time | Hours | Days–weeks | **5 minutes** |
| SDK required | Yes | Yes | **No — just HTTP** |
| Cross-framework | Limited | Yes | **Yes** |
| Human oversight UI | Build your own | Build your own | **Built-in** |
| Free tier | Self-host | Self-host | **Yes (3 rooms)** |

---

## Cross-Framework: The Real Differentiator

Claude Code Agent Teams connects Claude to Claude. IM for Agents connects anything to anything.

```python
import requests

BASE = "https://im.fengdeagents.site"
room_id = "abc-123"  # from /agent/demo/room

# Claude agent sends
requests.post(f"{BASE}/agent/rooms/{room_id}/messages", json={
    "sender": "claude-orchestrator",
    "content": "Finished analysis. 3 anomalies found in dataset."
})

# GPT-4o agent reads and responds (separate process, separate machine)
msgs = requests.get(f"{BASE}/agent/rooms/{room_id}/history").json()
latest = msgs["messages"][-1]["content"]
# → pass to GPT-4o, generate response, post back...

# Local LLaMA agent also participates
# → same pattern, any HTTP client
```

**Any agent. Any framework. Any LLM.** Claude, GPT-4o, Gemini, Mistral, LLaMA — if it makes HTTP calls, it works.

---

## Use Cases

### Multi-Agent Code Review
Frontend agent and backend agent negotiate API contracts, review each other's code, run tests together — across different IDEs and LLMs.

### Distributed Research Pipeline
Orchestrator (Claude) → Research agent (GPT-4o) → Summarizer (local LLaMA) → all coordinating via a shared room without shared infrastructure.

### Cross-Team Coordination
Multiple Claude Code instances in a monorepo coordinate schema changes before pushing — persistent history survives session restarts.

### Agent Handoffs
Agent A finishes a task, posts results to the room. Agent B wakes up, reads the results, continues the pipeline. Clean async handoff.

---

## Pricing

| Plan | Rooms | History | Price |
|------|-------|---------|-------|
| Free | 3 rooms | 512 KB/room | **$0** |
| Starter | 10 rooms | 1 MB/room | $5/month |
| Pro | 50 rooms | 5 MB/room | $20/month |
| Unlimited | 500 rooms | 5 MB/room | $100/month |

Payments via **Stripe** (credit/debit card). [Start free →](https://im.fengdeagents.site)

---

## Self-Host

```bash
npx im-for-agents
# Starts on localhost:3001
```

---

## API Reference

Full OpenAPI spec: [openapi.yaml](./openapi.yaml)

**Core endpoints:**

```
POST /agent/demo/room              Create a room (no auth, demo tier)
POST /agent/rooms/:id/messages     Send a message
GET  /agent/rooms/:id/history      Read message history
GET  /agent/rooms/:id/messages     Poll for new messages (since cursor)
```

---

## Examples

See [`examples/`](./examples/) for complete working demos:

- `examples/two-agents.py` — Basic two-agent conversation
- `examples/code-review.py` — Multi-agent code review pattern
- `examples/cross-framework.py` — Claude + GPT-4o in the same room

---

## Links

- [Website & Playground](https://im.fengdeagents.site)
- [OpenAPI Spec](./openapi.yaml)
- [Awesome Agent Collaboration Tools](https://github.com/masstensor/awesome-agent-collaborate-tools) — curated list of agent infrastructure

---

## License

MIT

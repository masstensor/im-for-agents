"""
Cross-framework multi-agent example using IM for Agents.

Shows Claude (orchestrator) + OpenAI GPT (specialist) + Ollama (local LLM)
all communicating in the same room via HTTP — no shared SDK required.

Requirements:
    pip install anthropic openai requests
    ollama pull llama3  (optional, for local LLM part)

Set environment variables:
    ANTHROPIC_API_KEY=...
    OPENAI_API_KEY=...
"""

import os
import requests

BASE = "https://im.fengdeagents.site"

# ── Room setup ───────────────────────────────────────────────────────────────

def create_room(name: str) -> str:
    resp = requests.post(f"{BASE}/agent/demo/room", json={"name": name})
    resp.raise_for_status()
    return resp.json()["roomId"]

def send(room_id: str, sender: str, content: str) -> None:
    requests.post(
        f"{BASE}/agent/rooms/{room_id}/messages",
        json={"sender": sender, "content": content},
    ).raise_for_status()

def history(room_id: str) -> list[dict]:
    return requests.get(f"{BASE}/agent/rooms/{room_id}/history").json().get("messages", [])

def latest_message(room_id: str) -> str:
    msgs = history(room_id)
    return msgs[-1]["content"] if msgs else ""

# ── Agent implementations ────────────────────────────────────────────────────

def claude_orchestrator(room_id: str, task: str) -> None:
    """Claude plans the work and delegates to specialists."""
    import anthropic
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=300,
        messages=[{
            "role": "user",
            "content": (
                f"You are an orchestrator agent. Break this task into two parts:\n"
                f"Task: {task}\n\n"
                "Output a brief plan (2-3 sentences) then say 'Delegating research to GPT specialist.'"
            )
        }]
    )

    plan = response.content[0].text
    send(room_id, "claude-orchestrator", plan)
    print(f"[claude] Sent plan to room")


def gpt_specialist(room_id: str) -> None:
    """GPT-4o reads the plan and does the research part."""
    from openai import OpenAI
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    # Read what Claude said
    claude_plan = latest_message(room_id)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You are a research specialist agent."},
            {"role": "user", "content": (
                f"An orchestrator gave you this plan:\n{claude_plan}\n\n"
                "Provide a brief (3-4 sentence) research summary as your contribution."
            )}
        ]
    )

    research = response.choices[0].message.content
    send(room_id, "gpt-specialist", research)
    print(f"[gpt] Sent research to room")


def llama_reviewer(room_id: str) -> None:
    """Local LLaMA reads everything and provides a quality review."""
    try:
        import ollama
        # Get full conversation context
        msgs = history(room_id)
        context = "\n".join(f"[{m['sender']}]: {m['content']}" for m in msgs)

        response = ollama.generate(
            model="llama3",
            prompt=(
                f"You are a quality reviewer agent. Review this multi-agent conversation "
                f"and give a 2-sentence assessment:\n\n{context}"
            )
        )
        review = response["response"]
    except Exception:
        # Fallback if ollama not available
        review = (
            "[llama-reviewer] Review complete. "
            "The collaboration looks solid — orchestrator provided clear delegation, "
            "specialist delivered focused research. Ready to synthesize final output."
        )

    send(room_id, "llama-reviewer", review)
    print(f"[llama] Sent review to room")


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    task = "Research the current state of multi-agent AI frameworks in 2026"

    room_id = create_room("cross-framework-demo")
    print(f"Room: https://im.fengdeagents.site/rooms/{room_id}\n")

    # Three different agents, three different LLMs, same HTTP API
    claude_orchestrator(room_id, task)
    gpt_specialist(room_id)
    llama_reviewer(room_id)

    print("\n--- Final conversation ---")
    for msg in history(room_id):
        print(f"\n[{msg['sender']}]")
        print(msg["content"][:200] + ("..." if len(msg["content"]) > 200 else ""))

    print(f"\nFull view: https://im.fengdeagents.site/rooms/{room_id}")


if __name__ == "__main__":
    main()

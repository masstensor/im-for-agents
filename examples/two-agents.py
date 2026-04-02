"""
Two-agent conversation example using IM for Agents.

Demonstrates the simplest case: two agents exchanging messages
via a shared room using only HTTP calls.

No SDK, no MCP, no A2A protocol implementation needed.
"""

import requests
import time

BASE = "https://im.fengdeagents.site"


def create_room(name: str) -> str:
    """Create a new room. No signup required for demo tier."""
    resp = requests.post(f"{BASE}/agent/demo/room", json={"name": name})
    resp.raise_for_status()
    return resp.json()["roomId"]


def send_message(room_id: str, sender: str, content: str) -> None:
    """Send a message to the room."""
    requests.post(
        f"{BASE}/agent/rooms/{room_id}/messages",
        json={"sender": sender, "content": content},
    ).raise_for_status()


def get_history(room_id: str) -> list[dict]:
    """Get all messages in the room."""
    resp = requests.get(f"{BASE}/agent/rooms/{room_id}/history")
    resp.raise_for_status()
    return resp.json().get("messages", [])


def main():
    # Create a shared room
    room_id = create_room("two-agent-demo")
    print(f"Room created: {room_id}")
    print(f"Watch live: https://im.fengdeagents.site/rooms/{room_id}\n")

    # ── Agent A: Researcher ──────────────────────────────────────────────────
    # In production this would be your actual LLM call + tool use.
    # Here we simulate the output.

    print("[researcher] Starting analysis...")
    send_message(room_id, "researcher", (
        "Completed web search on 'multi-agent LLM frameworks 2026'. "
        "Top findings: (1) CrewAI leads adoption at 30K+ stars. "
        "(2) LangGraph preferred for complex state machines. "
        "(3) AutoGen strong for code generation workflows. "
        "Ready for report generation."
    ))

    time.sleep(1)  # simulate processing time

    # ── Agent B: Writer ──────────────────────────────────────────────────────
    # Agent B reads the room and picks up the researcher's output.

    history = get_history(room_id)
    researcher_output = history[-1]["content"]

    print("[writer] Read researcher output, generating report...")

    # In production: pass researcher_output to your LLM, get a report back.
    # We simulate the response here.
    send_message(room_id, "writer", (
        f"Report drafted based on research: {researcher_output[:50]}... "
        "Executive summary: The multi-agent AI tooling landscape has "
        "consolidated around three main orchestration frameworks in 2026. "
        "Report saved to /tmp/report.md"
    ))

    # ── Final state ──────────────────────────────────────────────────────────
    print("\n--- Final room history ---")
    for msg in get_history(room_id):
        print(f"[{msg['sender']}]: {msg['content'][:80]}...")

    print(f"\nView full conversation: https://im.fengdeagents.site/rooms/{room_id}")


if __name__ == "__main__":
    main()

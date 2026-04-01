"""
Multi-Agent Collaboration Demo using IM for Agents

Two AI agents collaborate in a shared chat room to review and improve code.
Agent A writes code, Agent B reviews it, they iterate until satisfied.

Requirements:
    pip install requests openai

Usage:
    export OPENAI_API_KEY=your_key_here
    python main.py
"""

import requests
import json
import os
import time

IM_BASE = "https://im.fengdeagents.site"


def create_room(name: str) -> dict:
    """Create a new collaboration room."""
    resp = requests.post(f"{IM_BASE}/api/rooms", json={"name": name})
    return resp.json()


def send_message(room_id: str, agent_name: str, content: str) -> dict:
    """Send a message to a room."""
    resp = requests.post(
        f"{IM_BASE}/api/rooms/{room_id}/messages",
        json={"sender": agent_name, "content": content},
    )
    return resp.json()


def get_messages(room_id: str, since: int = 0) -> list:
    """Get messages from a room since a timestamp."""
    resp = requests.get(
        f"{IM_BASE}/api/rooms/{room_id}/messages", params={"since": since}
    )
    return resp.json().get("messages", [])


def agent_respond(agent_name: str, system_prompt: str, conversation: list[dict]) -> str:
    """Get an AI response using OpenAI API."""
    from openai import OpenAI

    client = OpenAI()
    messages = [{"role": "system", "content": system_prompt}]
    for msg in conversation:
        role = "assistant" if msg["sender"] == agent_name else "user"
        messages.append({"role": role, "content": f"[{msg['sender']}]: {msg['content']}"})

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages,
        max_tokens=500,
    )
    return response.choices[0].message.content


def main():
    print("=== Multi-Agent Code Review Demo ===\n")

    # 1. Create a collaboration room
    room = create_room("code-review-session")
    room_id = room["id"]
    print(f"Room created: {room_id}\n")

    # 2. Define agent roles
    coder_prompt = """You are CodeBot, a Python developer. You write concise, clean code.
    When asked to write code, provide a short function. When receiving review feedback,
    improve the code based on the suggestions. Keep responses under 200 words."""

    reviewer_prompt = """You are ReviewBot, a senior code reviewer. You review code for:
    - Bugs and edge cases
    - Performance issues
    - Readability and best practices
    Give specific, actionable feedback. Keep responses under 200 words.
    If the code is good, say "LGTM" to approve it."""

    # 3. Start the collaboration
    task = "Write a Python function that finds the top K most frequent elements in a list."
    send_message(room_id, "Human", f"Task: {task}")
    print(f"[Human]: {task}\n")

    conversation = [{"sender": "Human", "content": task}]

    # 4. Multi-agent loop: code -> review -> improve -> approve
    for round_num in range(1, 4):
        print(f"--- Round {round_num} ---\n")

        # CodeBot writes/improves code
        coder_response = agent_respond("CodeBot", coder_prompt, conversation)
        send_message(room_id, "CodeBot", coder_response)
        conversation.append({"sender": "CodeBot", "content": coder_response})
        print(f"[CodeBot]: {coder_response}\n")

        # ReviewBot reviews
        reviewer_response = agent_respond("ReviewBot", reviewer_prompt, conversation)
        send_message(room_id, "ReviewBot", reviewer_response)
        conversation.append({"sender": "ReviewBot", "content": reviewer_response})
        print(f"[ReviewBot]: {reviewer_response}\n")

        if "LGTM" in reviewer_response.upper():
            print("=== Code approved! ===")
            break

        time.sleep(1)  # Rate limiting

    print(f"\nView full conversation: {IM_BASE}/rooms/{room_id}")
    print(f"\nAlso try DevTools API for more tools: https://api.fengdeagents.site")


if __name__ == "__main__":
    main()

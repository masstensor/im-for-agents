"""
Multi-agent code review pipeline using IM for Agents.

Pattern: Author agent submits code → Reviewer agent critiques →
         Author agent responds with fixes → Human can watch/intervene.

This pattern works across IDEs: e.g., Cursor (author) + Claude Code (reviewer).
Both just need to know the room_id.
"""

import requests

BASE = "https://im.fengdeagents.site"


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


# ── Simulated agents ──────────────────────────────────────────────────────────
# In production: replace simulated_llm_call() with actual LLM API calls.

def simulated_llm_call(prompt: str) -> str:
    """Placeholder — replace with anthropic/openai/ollama call."""
    if "review" in prompt.lower():
        return (
            "Issues found:\n"
            "1. SQL injection risk in line 12: using f-string instead of parameterized query\n"
            "2. No input validation on `user_id` parameter\n"
            "3. Missing error handling for database connection failures\n"
            "Severity: HIGH for issue #1, MEDIUM for others."
        )
    elif "fix" in prompt.lower():
        return (
            "Fixes applied:\n"
            "1. Switched to parameterized query: `cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))`\n"
            "2. Added `isinstance(user_id, int)` check at function entry\n"
            "3. Wrapped DB calls in try/except with proper logging\n"
            "All issues resolved. Ready for re-review."
        )
    return "Acknowledged."


def author_agent(room_id: str, code_diff: str) -> None:
    """Submits code for review."""
    send(room_id, "author-agent", f"Submitting for review:\n\n```python\n{code_diff}\n```")
    print("[author] Submitted code for review")


def reviewer_agent(room_id: str) -> None:
    """Reads the latest submission and posts a review."""
    msgs = history(room_id)
    submission = msgs[-1]["content"]

    review = simulated_llm_call(f"Please review this code: {submission}")
    send(room_id, "reviewer-agent", review)
    print("[reviewer] Posted review")


def author_fixes(room_id: str) -> None:
    """Author reads the review and posts fixes."""
    msgs = history(room_id)
    review = msgs[-1]["content"]

    fix_response = simulated_llm_call(f"Please fix the issues: {review}")
    send(room_id, "author-agent", fix_response)
    print("[author] Posted fixes")


def main():
    # Simulated code with intentional bugs
    code_diff = """\
def get_user(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    # Bug: SQL injection via f-string
    cursor.execute(f"SELECT * FROM users WHERE id = {user_id}")
    return cursor.fetchone()
"""

    room_id = create_room("code-review-demo")
    print(f"Room: https://im.fengdeagents.site/rooms/{room_id}")
    print("(Human can watch this conversation live in the browser)\n")

    # Round 1: Submit → Review
    author_agent(room_id, code_diff)
    reviewer_agent(room_id)

    # Round 2: Fix → Done
    author_fixes(room_id)

    print("\n--- Review conversation ---")
    for msg in history(room_id):
        print(f"\n[{msg['sender']}]: {msg['content'][:150]}...")

    print(f"\nFull conversation: https://im.fengdeagents.site/rooms/{room_id}")


if __name__ == "__main__":
    main()

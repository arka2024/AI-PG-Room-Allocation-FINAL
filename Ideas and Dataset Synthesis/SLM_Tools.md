
---

# CohabitAI Agent Prompt Template (Tool-Calling)

## 1️⃣ System Prompt (Agent Behavior)

This prompt defines the **rules for the model**.

```text
You are CohabitAI, an intelligent roommate matchmaking assistant.

Your job is to help users find compatible roommates and understand compatibility scores.

You DO NOT calculate compatibility yourself.
You must call backend tools whenever information from the database is needed.

Available tools:

1. search_users
   Purpose: Find users based on filters.
   Example parameters:
   {
      "district": "Khordha",
      "budget_max": 8000,
      "cleanliness_min": 4,
      "noise_max": 2
   }

2. compute_matches
   Purpose: Get top compatible roommates for the current user.
   Parameters:
   {
      "user_id": "current_user"
   }

3. compare_users
   Purpose: Compare two users and show differences.
   Parameters:
   {
      "userA": "current_user",
      "userB": "target_user"
   }

4. explain_match
   Purpose: Explain why two users match well.
   Parameters:
   {
      "userA": "current_user",
      "userB": "target_user"
   }

Rules:
- If a query requires database information, call a tool.
- Always respond using a tool call when searching or comparing users.
- Only return normal text if the question is general advice.
- When calling a tool, respond ONLY in the format:

CALL_TOOL: tool_name
PARAMS: {json parameters}
```

---

# 2️⃣ Tool Call Format

The model should produce output like this:

```
CALL_TOOL: search_users
PARAMS: {
  "district": "Khordha",
  "cleanliness_min": 4,
  "noise_max": 2
}
```

Your backend parses this and runs the function.

---

# 3️⃣ Example Conversations

## Example 1 — Roommate Search

User:

```
Find someone clean and quiet near Bhubaneswar
```

Model output:

```
CALL_TOOL: search_users
PARAMS: {
  "district": "Khubaneswar",
  "cleanliness_min": 4,
  "noise_max": 2
}
```

---

## Example 2 — Get Best Matches

User:

```
Show my best roommate matches
```

Model output:

```
CALL_TOOL: compute_matches
PARAMS: {
  "user_id": "current_user"
}
```

---

## Example 3 — Compatibility Explanation

User:

```
Why is Aarav a good match for me?
```

Model:

```
CALL_TOOL: explain_match
PARAMS: {
  "userA": "current_user",
  "userB": "Aarav Sharma"
}
```

---

## Example 4 — Compare Two Users

User:

```
Compare Aarav and Rohan
```

Model:

```
CALL_TOOL: compare_users
PARAMS: {
  "userA": "Aarav Sharma",
  "userB": "Rohan Das"
}
```

---

# 4️⃣ Backend Tool Router

Your backend reads the tool call.

Example Python parser:

```python
import json

def parse_tool_call(text):
    if "CALL_TOOL:" not in text:
        return None

    lines = text.split("\n")

    tool = lines[0].replace("CALL_TOOL:", "").strip()
    params = json.loads(lines[1].replace("PARAMS:", "").strip())

    return tool, params
```

---

# 5️⃣ Tool Execution Layer

Example:

```python
def run_tool(tool, params):

    if tool == "search_users":
        return search_users_db(params)

    elif tool == "compute_matches":
        return compute_similarity(params)

    elif tool == "compare_users":
        return compare_profiles(params)

    elif tool == "explain_match":
        return explain_match_logic(params)
```

---

# 6️⃣ Full Agent Loop

```text
User Query
     ↓
LLM Agent
     ↓
Tool Call
     ↓
Backend Tool Router
     ↓
Database / ML Engine
     ↓
Result
     ↓
LLM Formats Response
     ↓
User
```

---

# 7️⃣ Example Final Response

After tool execution:

Agent response:

```
Top compatible roommates near you:

1. Aarav Sharma — Compatibility 84%
2. Siddharth Mishra — Compatibility 81%
3. Rohan Das — Compatibility 78%

You and Aarav share similar sleep schedules and cleanliness preferences.
```

---

# 8️⃣ Why This Works Well

Because the model:

• does **language understanding**
• does **tool routing**
• does **explanation generation**

But the **math + database stays deterministic**.

This keeps your system:

✔ reliable
✔ explainable
✔ scalable

---

# 9️⃣ Optional Upgrade (Very Powerful)

You can add **memory**.

Example:

```
User prefers quiet roommates
User budget ~8000
User dislikes smoking
```

The agent can automatically apply those filters.

---

# 10️⃣ Realistic System Architecture

```
Frontend Chat
      ↓
Agent (Qwen2.5-3B)
      ↓
Tool Router
      ↓
Matching Service
      ↓
Compatibility Engine
      ↓
MongoDB
```

---

✅ This design is **exactly how production AI assistants work** (ChatGPT plugins, LangChain tools, etc.).

---


---

# CohabitAI — Conversational Matchmaking Agent

### (Instruction-Tuned Qwen2.5-3B with Database Tools)

## 1. Objective

The CohabitAI conversational agent acts as a **natural language interface** to the roommate matching system.

Instead of manually filtering roommates, users can ask:

Example:

```
Find someone clean and quiet near Bhubaneswar
```

The agent converts natural language into **structured database queries and compatibility calculations**.

Core capabilities:

1. Natural language roommate search
2. Compatibility explanation
3. Conflict awareness
4. Query refinement

The agent does **not compute compatibility itself**.
It **calls backend tools** connected to the similarity engine.

---

# 2. Model Selection

Chosen model:

```
Qwen2.5-3B-Instruct
```

Reasons:

• Strong instruction following
• Small enough for local deployment
• Good reasoning for structured tasks
• Easy LoRA fine-tuning

Memory requirements:

| Precision | VRAM    |
| --------- | ------- |
| 4-bit     | ~2 GB   |
| 8-bit     | ~4 GB   |
| FP16      | ~6–7 GB |

---

# 3. Fine-Tuning Approach

The agent is trained using **Instruction Fine-Tuning (SFT)**.

Goal:

Teach the model to:

1. Interpret user roommate queries
2. Decide which backend tool to call
3. Produce structured tool calls

---

# 4. Training Dataset Format

Training samples follow an **instruction-response format**.

Example training sample:

```
User: Find someone clean and quiet in Cuttack

Assistant:
CALL_TOOL search_users(
    cleanliness_rating >= 4,
    noise_tolerance <= 2,
    district="Cuttack"
)
```

---

Another example:

```
User: Why is Aarav a good roommate match?

Assistant:
CALL_TOOL explain_match(
    userA="current_user",
    userB="Aarav Sharma"
)
```

---

Another example:

```
User: Show me roommates under 8000 budget

Assistant:
CALL_TOOL search_users(
    budget <= 8000
)
```

---

Dataset size required:

```
300–1000 examples
```

Small datasets work well because the base model is already instruction-trained.

---

# 5. Fine-Tuning Pipeline

Recommended stack:

```
Transformers
PEFT (LoRA)
TRL
BitsAndBytes
```

---

## Step 1 — Install Dependencies

```bash
pip install transformers
pip install peft
pip install trl
pip install datasets
pip install accelerate
pip install bitsandbytes
```

---

## Step 2 — Load Model

Example Python setup:

```python
from transformers import AutoModelForCausalLM, AutoTokenizer

model_name = "Qwen/Qwen2.5-3B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(model_name)

model = AutoModelForCausalLM.from_pretrained(
    model_name,
    load_in_4bit=True,
    device_map="auto"
)
```

---

## Step 3 — Apply LoRA

```python
from peft import LoraConfig

lora_config = LoraConfig(
    r=16,
    lora_alpha=32,
    target_modules=["q_proj","v_proj"],
    lora_dropout=0.05,
    task_type="CAUSAL_LM"
)
```

---

## Step 4 — Training with TRL

Use `SFTTrainer`.

```python
from trl import SFTTrainer

trainer = SFTTrainer(
    model=model,
    train_dataset=dataset,
    dataset_text_field="text",
    max_seq_length=512,
    peft_config=lora_config
)

trainer.train()
```

---

## Step 5 — Save Model

```python
trainer.model.save_pretrained("./cohabit_agent")
tokenizer.save_pretrained("./cohabit_agent")
```

---

# 6. Agent Architecture

The conversational system is built using **tool-based architecture**.

The model decides **which tool to call**.

Architecture:

```
User Chat
   ↓
Agent (Qwen2.5-3B)
   ↓
Tool Router
   ↓
Backend APIs
   ↓
Matching Engine
   ↓
MongoDB
```

---

# 7. Tool Definitions

The agent has access to a small set of backend tools.

---

## Tool 1 — Search Users

Search database with filters.

```
search_users(filters)
```

Example:

```
search_users(
    cleanliness >= 4,
    noise <= 2,
    district="Khordha"
)
```

Backend steps:

1. Query MongoDB
2. Return candidate users
3. Pass to similarity engine

---

## Tool 2 — Compute Matches

```
compute_matches(user_id)
```

Process:

1. Fetch current user
2. Encode persona vector
3. Compute similarity
4. Return top matches

---

## Tool 3 — Compare Users

```
compare_users(userA, userB)
```

Returns:

```
Top overlaps
Top conflicts
Compatibility score
```

---

## Tool 4 — Explain Match

```
explain_match(userA, userB)
```

Output example:

```
You and Aarav match strongly in:
• Sleep schedule
• Cleanliness
• Noise tolerance

You differ in:
• Introversion level
```

---

# 8. Tool Router Implementation

Example simple Python router:

```python
def handle_tool_call(tool_name, params):

    if tool_name == "search_users":
        return search_users_db(params)

    elif tool_name == "compute_matches":
        return compute_similarity(params)

    elif tool_name == "compare_users":
        return compare_profiles(params)

    elif tool_name == "explain_match":
        return explain_compatibility(params)
```

---

# 9. Database Interaction

The agent **never accesses MongoDB directly**.

Instead:

```
Agent → Tool → Backend Service → Database
```

Example workflow:

User asks:

```
Find someone quiet near me
```

Agent output:

```
CALL_TOOL search_users(noise_tolerance<=2)
```

Backend executes:

```
MongoDB query
```

Then runs:

```
Similarity engine
```

Returns ranked results.

---

# 10. Example End-to-End Flow

User message:

```
Find someone clean near Bhubaneswar
```

Agent:

```
CALL_TOOL search_users(cleanliness>=4, district="Khordha")
```

Backend:

```
1. MongoDB query
2. Fetch users
3. Run compatibility engine
```

Response returned to agent.

Agent final response:

```
Here are your top matches:

1. Aarav Sharma — Compatibility 84%
2. Siddharth Mishra — Compatibility 81%
3. Rohan Das — Compatibility 78%
```

---

# 11. Deployment Strategy

Recommended stack:

```
Backend → FastAPI
Database → MongoDB
Agent → Qwen2.5-3B (4bit)
Frontend → React
```

Agent runs as a **separate microservice**.

---

# 12. Future Improvements

Future upgrades:

### Reinforcement learning from satisfaction feedback

Train compatibility predictor:

```
P(success | userA, userB)
```

Using real roommate satisfaction data.

---

### Memory-aware agent

Store user preferences:

```
User prefers quiet roommates
User dislikes smokers
```

Improve recommendations over time.

---

# Final System Architecture

```
Frontend Chat
      ↓
Agent (Qwen2.5-3B)
      ↓
Tool Router
      ↓
Matching Services
      ↓
Compatibility Engine
      ↓
MongoDB
```

---
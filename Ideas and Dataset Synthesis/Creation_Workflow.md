# 🚀 COHABITAI – CREATION WORKFLOW
*ML-Core + Clean Architecture*

## 🧠 PHASE 1 — Mathematical & Data Modeling Foundation

**Goal:** Design the system brain before building the system body.

### Step 1: Define Persona Space (Formal Model)

Define feature vector structure:

```
P = [L | C | R]
```

Where:
- **L** → Lifestyle features
- **C** → Personality features
- **R** → Constraints / Preferences

**Example:**
- Index 0 → `sleep_time` (0 or 1)
- Index 1 → `cleanliness_rating` (1–5 normalized)
- Index 2 → `noise_tolerance` (1–5 normalized)
- Index 3 → `introversion_score` (1–5 normalized)
- Index 4 → `smoking_tolerance` (0/1)
- Index 5 → `pets_allowed` (0/1)

**Finalize:**
- Feature encoding
- Value normalization strategy
- Weight vector `w`

### Step 2: Define Compatibility Function

**Weighted Cosine Similarity:**
```
S(A,B) = Σ(w_i * P_i,A * P_i,B) / √(Σ(w_i * P_i,A²) * Σ(w_i * P_i,B²))
```

Define:
- Input format
- Output format
- Ranking logic

---

## 🗄 PHASE 2 — Database Design (Model-Driven)

Build DB based on ML needs.

### Users Collection

Each user stores:
- `profile`
- `location`
- `preferences`
- `persona_raw`
- `feature_vector` (computed dynamically)

**Important:** ✔ Store raw persona | ✔ Compute vectors dynamically | ✔ Do NOT store compatibility scores

### Indexes
- `location` → 2dsphere
- `budget`
- `gender`
- `_id` (hashed, optional)

---

## 🔬 PHASE 3 — Offline ML Engine Development

Build before integrating APIs:

```
/ml_engine
    encoder.py
    similarity.py
    weights.py
    validator.py
```

**Tasks:**
- Encode `persona_raw` → `feature_vector`
- Normalize features
- Implement weighted cosine similarity
- Test with synthetic dataset
- Validate ranking logic

---

## 🔌 PHASE 4 — Convert ML Engine into Service Layer

Wrap ML logic in clean API modules.

### Service Architecture
```
/services
    matchmaking_service.py
    compare_service.py
    chat_service.py
```

### Matchmaking Service Workflow
1. Fetch current user
2. Encode feature vector
3. Fetch candidate users
4. Encode their vectors
5. Compute similarity
6. Rank results
7. Return sorted list

---

## 🧩 PHASE 5 — API Layer (Clean Separation)

Create clean routes:
- `POST /create-user`
- `GET /get-matches`
- `POST /compare-users`
- `POST /start-chat`
- `POST /send-message`

**API layer:**
- Validates input
- Calls service layer
- Returns structured JSON
- Never contains ML math

---

## 🗺 PHASE 6 — Geo Filtering Layer

Before similarity calculation, query MongoDB:
- Filter by district
- Filter by budget range
- Filter by gender preference

Pass filtered users to ML engine to reduce computation.

---

## 💬 PHASE 7 — Compare Module

Compute differences instead of final score only:

```
Δ_i = w_i * (P_i,A - P_i,B)
```

**Return:**
- Top 5 overlaps
- Top 5 conflicts

Increases transparency.

---

## 💬 PHASE 8 — Chat Module (Independent)

- Isolated from ML
- Separate collection
- No ML coupling
- Triggered after selection

---

## 🧠 Full Creation Flow (Chronological)

1. Design persona schema
2. Define vector encoding
3. Implement similarity engine offline
4. Validate with synthetic data
5. Design Mongo schema
6. Implement user storage API
7. Wrap ML engine as matchmaking service
8. Add geo filtering
9. Add compare module
10. Add chat system
11. Connect frontend
12. Optimize & test

---

## 🏗 Final Architecture Diagram

```
Frontend
   ↓
API Layer
   ↓
Application Services
   ├─ Matchmaking Service
   ├─ Compare Service
   └─ Chat Service
   ↓
ML Compatibility Engine
   ↓
Repository Layer
   ↓
MongoDB
```


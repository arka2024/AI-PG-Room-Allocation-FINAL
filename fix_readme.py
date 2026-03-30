with open('README.md', 'w', encoding='utf-8') as f:
    f.write("""# 🏠 CohabitAI: Advanced Machine Learning Roommate & PG Allocation Platform

![CohabitAI Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![Flask](https://img.shields.io/badge/framework-Flask-green)
![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-orange)
![Gemini](https://img.shields.io/badge/AI-Google_Gemini-purple)

## 📖 1. Project Overview & Product Vision
**CohabitAI** is a state-of-the-art, data-driven platform designed to reinvent the process of finding compatible roommates and Paying Guest (PG) accommodations. Moving beyond rudimentary filters like "budget" and "location", CohabitAI leverages a **multidimensional mathematical compatibility engine** built on proven sociological dimensions.

By modeling users along critical lifestyle habits, personality traits, and strict behavioral constraints, the system ensures high-longevity matches. To assist users in this process, CohabitAI features an integrated AI Conversational Guidance Counselor, built on the Google Gemini API, capable of offering conflict resolution pathways mapped directly to the mathematical friction points between users.

### Core Value Propositions:
*   **Predictive Harmony:** Reduces mid-lease roommate conflicts by structurally aligning core habits (Cleanliness, Sleep Schedules, Noise Tolerance) before move-in.
*   **Transparent Analytics:** Provides users a "Peek under the hood" via the Compare Tool, specifically articulating *why* someone is a 95% match or a 60% match.
*   **Geo-Spatial Intelligence:** Fast Haversine filtering ensures users aren't shown perfect matches who live 500km away unless explicitly requested.
*   **LLM-Augmented Mediation:** A context-aware chatbot that acts as a pre-leasing mediator.

---

## 🏗️ 2. Architectural Design & Pipeline

### System Architecture Topology
CohabitAI relies on a decoupled Service-Layer architecture, strictly isolating the heavy Machine Learning computational mathematics from the fast HTTP routing endpoints. 

```mermaid
graph TD
   A[Client Browser HTML/CSS/JS] -->|HTTP Requests| B(Flask App Routing - app.py)
   B --> C{Authentication & Session Layer}
   C -->|Logged In| D[Search & Geo-Filter Pipeline]
   
   D -->|Candidate Sub-population| E[Scikit-Learn KNN Pre-Filter]
   E -->|Top 150 Neighbors| F[Hybrid Math Engine - compatibility.py]
   F -->|Results Sorted| G[Jinja2 / React Render Pipeline]
   G --> A
   
   B --> H[AI LLM Chatbot Module - chatbot.py]
   H -->|Prompts + ML Differentials| I((Google Gemini LLM))
   I -->|Natural Language Response| H
   
   F -.-> J[(Local Data / MongoDB)]
```

### Module by Module Workflow Overview
1.  **Phase 1: User Onboarding & Vectorization:** Users answer a 10-point Likert Scale (1-5) questionnaire. This raw data is mapped to a Numpy Array (Feature Vector) in real-time.
2.  **Phase 2: Pre-Calculation Filtering (Hard Constraints):** To save O(N^2) mathematical overhead, candidate pools are aggressively truncated using Haversine distance, budget barriers, smoking limits, and gender prerequisites. 
3.  **Phase 3: KNN Dimensionality Slicing (Scalability Trigger):** Once the candidate pool scales beyond 250 records, a Scikit-Learn `NearestNeighbors` (Metric: Cosine) index fits over the active pool, dumping the furthest candidates instantly to optimize memory.
4.  **Phase 4: Hybrid Core Math Blender:**
    *   `compute_weighted_cosine_similarity()` handles proportional alignment.
    *   `compute_weighted_euclidean_similarity()` handles magnitude variance.
    *   `compute_bio_similarity()` applies TF-IDF on user text.
    *   Scores are statically weighted and reduced to a `0-100%` human-readable score.
5.  **Phase 5: Compare Module Execution (Conflict Extraction):** `compute_feature_differential()` calculates specific Deltas across all 10 features, grouping the highest and lowest deltas.
6.  **Phase 6: GenAI Context Bridge:** The `chatbot.py` extracts the raw output of the Compare Module and constructs engineered NLP Prompts dictating exactly how two users differ, feeding formatting rules to the Gemini LLM for resolution advice.

---

## 🧮 3. Core Mathematical Concepts & Equations

The ML Engine (`compatibility.py`) operates as the brain. The algorithm treats each user as a point in a 10-dimensional feature space. 

**Mathematical Notation Definition:**
*   **Dimensional Size (N):** N = 10
*   **Feature Vector User A:** A = [l1, l2, ... ln] (Values normalized from 1.0 to 5.0)
*   **Feature Vector User B:** B = [l1, l2, ... ln] (Values normalized from 1.0 to 5.0)
*   **Weight Vector (W):** W = [w1, w2, ... wn] (Global static array defining importance)

### Equation 1: Weighted Cosine Similarity (60% Weight)
Standard Cosine Similarity determines the angle between two vectors. By scaling the inputs via the Weight Vector (W), the model heavily penalizes divergent angles on critical dimensions (e.g., Cleanliness), while allowing slack on low dimensions.

```math
S_c(A, B) = [Sum(w_i * A_i * B_i)] / [Sqrt(Sum(w_i * A_i^2)) * Sqrt(Sum(w_i * B_i^2))] * 100
```

*   **Behavioral Logic:** Proves proportional alignment. If User A prefers 3 across the board and User B prefers 4, they are highly compatible proportionally, just with differing intensities.

### Equation 2: Weighted Euclidean Similarity (25% Weight)
Euclidean measures the absolute straight-line distance. Used to catch what Cosine misses (e.g., the intense magnitude jump between a clean freak 5 and a slob 1, even if their angle matches elsewhere).

1.  **Calculate Weighted Straight-Line Distance:**
    `D_e(A,B) = Sqrt( Sum( w_i * (A_i - B_i)^2 ) )`
2.  **Calculate Max Possible Distance Matrix:** (Knowing ranges are fixed 1 to 5, the max variance is 16)
    `D_max = Sqrt( Sum( w_i * 16 ) )`
3.  **Normalize Distance to a Similarity Percentage:**
    `S_e(A,B) = (1 - (D_e(A,B) / D_max)) * 100`

### Equation 3: Text/Bio NLP Similarity (15% Weight)
Converts raw string biographies into Term Frequency matrices to find latent shared hobbies or linguistic styles that arrays cannot express.

1.  **Matrix Creation:** `M = TF-IDF(Bio_A, Bio_B)`
2.  **Cosine Score:** `S_b(A, B) = Cosine(M_A, M_B) * 100`

### Equation 4: The Final Hybrid Score Blender
The algorithm fuses the respective models to create a highly robust output impervious to missing text variables or edge-case single-score anomalies.

`Final = (0.60 * S_c) + (0.25 * S_e) + (0.15 * S_b)`

### Equation 5: Haversine Formula (Geo-Spatial Routing)
Calculating pure spherical geographic distance on Earth's curvature before rendering maps or filtering searches locally.

```math
a = sin^2((Lat_2 - Lat_1)/2) + cos(Lat_1)*cos(Lat_2)*sin^2((Lon_2 - Lon_1)/2)
c = 2 * atan2(sqrt(a), sqrt(1-a))
Distance_km = 6371 * c
```

### Equation 6: Conflict Differential Formula (The "Compare" UI)
To generate the Compare screen and feed the LLM Chatbot, the engine calculates the absolute, weight-scaled distance for every singular dimension independently.

`Delta_i = w_i * ABS(A_i - B_i)`

The engine takes the Array of Deltas and sorts them in descending order. The top elements represent "Conflicts", the bottom elements represent "Overlaps".

---

## 🧬 4. Dimensional Feature Weights (W Vector)
CohabitAI relies on sociological data to dictate importance. The W array is statically defined in `compatibility.py` as:

| Dimension Feature (i) | Weight (wi) | Risk Factor if Clashed | Reason for Weighting |
| :--- | :--- | :--- | :--- |
| **`sleep_schedule`** | **5.0** | 🔥 High | Daily disruption of REM sleep directly causes severe roommate hostility. |
| **`cleanliness`** | **5.0** | 🔥 High | The primary cause of all roommate disputes (chores, dishes). |
| **`noise_tolerance`** | **4.5** | ⚠️ Medium-High | Limits ability to study, work-from-home, or relax. |
| **`introversion_extroversion`** | **4.0** | ⚠️ Medium-High | Personality clash leading to passive-aggressive tension. |
| **`social_battery`** | **4.0** | ⚠️ Medium-High | Unspoken expectations of shared vs. isolated time. |
| **`communication_style`** | **3.5** | 🟡 Medium | Direct communicators easily offend avoidant communicators. |
| **`guest_frequency`** | **3.5** | 🟡 Medium | Privacy invasion risks involving external 3rd parties. |
| **`conflict_resolution`** | **3.0** | 🟡 Medium | Dictates whether arguments are solved practically or aggressively. |
| **`cooking_frequency`** | **2.0** | 🟢 Low-Medium | Mostly related to utility usage and kitchen smells / schedule. |
| **`workout_habit`** | **1.5** | 🟢 Low | Minimal risk unless linked to early `sleep_schedule` disruptions. |

---

## 🛠️ 5. Technical Stack & File Structure

### Tech Stack
*   **Logic Runtime:** `Python 3.10+` running the `Flask 3.x` framework. Safe, multi-threaded request routing.
*   **Vector Operations:** `NumPy` executing matrix arrays to ensure scaling thousands of vectors takes fractions of a second.
*   **Machine Learning Tooling:** `scikit-learn` handling all TF-IDF Text Vectorization, KNN neighbor grouping, and PCA (Principal Component Analysis).
*   **Data Layer:** Threading-locked JSON flat-files (`users_local_balanced.json`) bridging to `PyMongo` to map documents directly into MongoDB Atlas.
*   **Generative AI:** Google Gemini LLM processing zero-shot conflict mediation prompts heavily engineered by the backend.
*   **View Layer:** HTML5/CSS3 natively routed via Jinja2 templates (`templates/`) communicating alongside a React/Vite build process found in `frontend/`.

### Critical File Map
*   `app.py` - Core Flask routing, session definitions, and primary API logic layer.
*   `compatibility.py` - The pure ML Model. Holds all `W` variables, NumPy Array generation, Matrix multiplications, and TF-IDF pipelines.
*   `chatbot.py` - Regex string-matching intent map combined with Gemini LLM prompt-engineering templates.
*   `rebalance_pg_locations_odisha.py` - Development script allocating dynamic geographic coordinates across synthetic coordinate map arrays.
*   `models.py` - SQLAlchemy and ORM model maps for potential strict SQL schema configurations.

---

## 🚀 6. Execution Call Stack (Code Step-by-Step)

If you are a developer looking tracking how a specific query is generated on the website, follow this execution trace:

1.  **Application Boot Phase (`app.py`)**: 
    The Flask engine boots. `_USERS_LOCK` initiates.
2.  **User Search Request (`/search` Route)**: 
    * User visits `/search`. Flask extracts `current_user` from the Flask-Login `session`.
    * `get_all_active_users()` compiles the global array of all standard `User` objects.
3.  **Geo & Constraint Filtering**: 
    * `discover_candidates_by_location()` removes anyone outside the strict Haversine radius limits.
    * Constraint checks are mapped: Gender requirements, smoking tolerances, etc.
4.  **Math Engine Invocation (`compatibility.rank_users_by_compatibility`)**: 
    * Sklearn `NearestNeighbors` groups the closest vector arrays.
    * `compute_compatibility(query_vec, candidate_vec)` is looped against valid neighbors.
    * The system computes `S_cosine`, `S_euclidean`, `S_nlp` and blends them.
    * Result: List of Dict DTOs `[{"user": userObj, "score": 88.5, "distance": 4.1}]`.
5.  **Compare Tool & AI Prompt Generation (`chatbot.py`)**: 
    *   User presses "Compare" between themselves and `Candidate_B`.
    *   `compatibility.compute_feature_differential(userA, userB)` calculates Math Equation 6 (Deltas) returning `[{"feature": "cleanliness", "diff": 3.0, "weighted_diff": 15.0}]`.
    *   `chatbot.py`'s `generate_conflict_prompts()` ingests this structured array, identifies the variables > 1.0, pulling from `CONFLICT_DISCUSSION_TEMPLATES`, generating highly specific LLM chat scenarios sent back to the view layer.
""")

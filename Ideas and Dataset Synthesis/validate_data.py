import json
from collections import Counter

with open("odisha_users.json", "r") as f:
    users = json.load(f)

print(f"Total users loaded: {len(users)}\n")

# ============================
# 1. Uniqueness Checks
# ============================

ids = [u["_id"] for u in users]
names = [u["profile"]["name"] for u in users]

dup_ids = [id for id, cnt in Counter(ids).items() if cnt > 1]
dup_names = [n for n, cnt in Counter(names).items() if cnt > 1]

print("=== UNIQUENESS ===")
print(f"  Unique IDs:   {len(set(ids))}/{len(ids)}")
print(f"  Unique Names: {len(set(names))}/{len(names)}")
if dup_ids:
    print(f"  ⚠ Duplicate IDs: {dup_ids[:10]}")
if dup_names:
    print(f"  ⚠ Duplicate Names: {dup_names[:10]}")
if not dup_ids and not dup_names:
    print("  ✅ All IDs and names are unique!")

# ============================
# 2. Schema Validation
# ============================

REQUIRED_KEYS = {
    "profile": {"name", "age", "gender", "bio"},
    "location": {"type", "coordinates", "area_name"},
    "preferences": {"budget", "gender_preference", "smoking_tolerance", "pets_allowed"},
    "persona_raw": {"sleep_time", "cleanliness_rating", "noise_tolerance", "introversion_score"},
}

schema_errors = []
for i, u in enumerate(users):
    for section, keys in REQUIRED_KEYS.items():
        if section not in u:
            schema_errors.append(f"  User {i} ({u.get('_id','?')[:8]}): missing section '{section}'")
        else:
            missing = keys - set(u[section].keys())
            if missing:
                schema_errors.append(f"  User {i} ({u['_id'][:8]}): '{section}' missing keys {missing}")

print(f"\n=== SCHEMA VALIDATION ===")
if schema_errors:
    print(f"  ⚠ {len(schema_errors)} issues found:")
    for e in schema_errors[:15]:
        print(e)
else:
    print("  ✅ All 500 users have valid schema!")

# ============================
# 3. Value Range Checks
# ============================

range_issues = []
for i, u in enumerate(users):
    p = u.get("profile", {})
    pref = u.get("preferences", {})
    per = u.get("persona_raw", {})
    loc = u.get("location", {})

    if not (18 <= p.get("age", 0) <= 28):
        range_issues.append(f"  User {i} '{p.get('name')}': age={p.get('age')}")
    if p.get("gender") not in ("Male", "Female"):
        range_issues.append(f"  User {i} '{p.get('name')}': gender={p.get('gender')}")
    if not (5000 <= pref.get("budget", 0) <= 15000):
        range_issues.append(f"  User {i} '{p.get('name')}': budget={pref.get('budget')}")
    if pref.get("gender_preference") not in ("Male", "Female", "Any"):
        range_issues.append(f"  User {i} '{p.get('name')}': gender_preference={pref.get('gender_preference')}")
    if per.get("sleep_time") not in ("Early", "Late"):
        range_issues.append(f"  User {i} '{p.get('name')}': sleep_time={per.get('sleep_time')}")
    for key in ("cleanliness_rating", "noise_tolerance", "introversion_score"):
        val = per.get(key, 0)
        if not (1 <= val <= 5):
            range_issues.append(f"  User {i} '{p.get('name')}': {key}={val}")
    coords = loc.get("coordinates", [0, 0])
    if len(coords) != 2:
        range_issues.append(f"  User {i} '{p.get('name')}': bad coordinates length")
    elif not (80 <= coords[0] <= 88 and 17 <= coords[1] <= 23):
        range_issues.append(f"  User {i} '{p.get('name')}': coords {coords} outside Odisha bbox")

print(f"\n=== VALUE RANGES ===")
if range_issues:
    print(f"  ⚠ {len(range_issues)} issues:")
    for e in range_issues[:20]:
        print(e)
else:
    print("  ✅ All values within expected ranges!")

# ============================
# 4. Distribution Stats
# ============================

genders = Counter(u["profile"]["gender"] for u in users)
districts = Counter(u["location"]["area_name"] for u in users)
sleep = Counter(u["persona_raw"]["sleep_time"] for u in users)
budgets = [u["preferences"]["budget"] for u in users]
ages = [u["profile"]["age"] for u in users]
smoke_tol = Counter(u["preferences"]["smoking_tolerance"] for u in users)
pets = Counter(u["preferences"]["pets_allowed"] for u in users)
gender_pref = Counter(u["preferences"]["gender_preference"] for u in users)

print(f"\n=== DISTRIBUTIONS ===")
print(f"  Gender:       {dict(genders)}")
print(f"  Sleep:        {dict(sleep)}")
print(f"  Smoking tol:  {dict(smoke_tol)}")
print(f"  Pets allowed: {dict(pets)}")
print(f"  Gender pref:  {dict(gender_pref)}")
print(f"  Age range:    {min(ages)}-{max(ages)}, avg={sum(ages)/len(ages):.1f}")
print(f"  Budget range: ₹{min(budgets)}-₹{max(budgets)}, avg=₹{sum(budgets)/len(budgets):.0f}")
print(f"  Districts ({len(districts)} unique): {districts.most_common(10)}")

# ============================
# 5. Pairwise Similarity Sample
# ============================

def similarity_score(u1, u2):
    """Simple similarity: count matching fields."""
    score = 0
    total = 0

    # Budget closeness (within 2000)
    total += 1
    if abs(u1["preferences"]["budget"] - u2["preferences"]["budget"]) <= 2000:
        score += 1

    # Gender preference match
    total += 1
    if u1["preferences"]["gender_preference"] == u2["preferences"]["gender_preference"]:
        score += 1

    # Smoking tolerance
    total += 1
    if u1["preferences"]["smoking_tolerance"] == u2["preferences"]["smoking_tolerance"]:
        score += 1

    # Pets
    total += 1
    if u1["preferences"]["pets_allowed"] == u2["preferences"]["pets_allowed"]:
        score += 1

    # Sleep time
    total += 1
    if u1["persona_raw"]["sleep_time"] == u2["persona_raw"]["sleep_time"]:
        score += 1

    # Cleanliness (within 1)
    total += 1
    if abs(u1["persona_raw"]["cleanliness_rating"] - u2["persona_raw"]["cleanliness_rating"]) <= 1:
        score += 1

    # Noise tolerance (within 1)
    total += 1
    if abs(u1["persona_raw"]["noise_tolerance"] - u2["persona_raw"]["noise_tolerance"]) <= 1:
        score += 1

    # Introversion (within 1)
    total += 1
    if abs(u1["persona_raw"]["introversion_score"] - u2["persona_raw"]["introversion_score"]) <= 1:
        score += 1

    # Same district
    total += 1
    if u1["location"]["area_name"] == u2["location"]["area_name"]:
        score += 1

    return score, total

print(f"\n=== PAIRWISE SIMILARITY (sample of 20 random pairs) ===")

import random
random.seed(42)
sample_pairs = [(random.randint(0, len(users)-1), random.randint(0, len(users)-1)) for _ in range(20)]

high_matches = []
low_matches = []

for i, j in sample_pairs:
    if i == j:
        continue
    s, t = similarity_score(users[i], users[j])
    pct = s / t * 100
    name_i = users[i]["profile"]["name"]
    name_j = users[j]["profile"]["name"]
    line = f"  {name_i:25s} vs {name_j:25s} → {s}/{t} ({pct:.0f}%)"
    print(line)
    if pct >= 80:
        high_matches.append((name_i, name_j, pct))
    elif pct <= 30:
        low_matches.append((name_i, name_j, pct))

# Full scan for extreme matches
print(f"\n=== FULL SCAN: Finding most/least similar pairs (checking 5000 random pairs) ===")

best = (None, None, 0)
worst = (None, None, 100)

pairs_checked = 0
for _ in range(5000):
    i, j = random.sample(range(len(users)), 2)
    s, t = similarity_score(users[i], users[j])
    pct = s / t * 100
    pairs_checked += 1
    if pct > best[2]:
        best = (users[i]["profile"]["name"], users[j]["profile"]["name"], pct)
    if pct < worst[2]:
        worst = (users[i]["profile"]["name"], users[j]["profile"]["name"], pct)

print(f"  Checked {pairs_checked} random pairs")
print(f"  🔥 Most similar:  {best[0]} & {best[1]} → {best[2]:.0f}%")
print(f"  ❄️  Least similar: {worst[0]} & {worst[1]} → {worst[2]:.0f}%")

# Check for exact duplicates (identical persona+preferences)
print(f"\n=== EXACT DUPLICATE CHECK (persona + preferences) ===")
fingerprints = {}
exact_dups = 0
for u in users:
    fp = json.dumps({"p": u["preferences"], "r": u["persona_raw"]}, sort_keys=True)
    if fp in fingerprints:
        exact_dups += 1
        if exact_dups <= 5:
            print(f"  ⚠ '{u['profile']['name']}' has same persona+prefs as '{fingerprints[fp]}'")
    else:
        fingerprints[fp] = u["profile"]["name"]

if exact_dups == 0:
    print("  ✅ No exact duplicates in persona+preferences!")
else:
    print(f"  Total exact duplicates: {exact_dups}")

print("\n✅ Validation complete.")

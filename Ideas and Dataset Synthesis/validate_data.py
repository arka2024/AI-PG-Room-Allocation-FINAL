import json
from collections import Counter

with open("odisha_users.json", "r") as f:
    users = json.load(f)

print(f"Total users loaded: {len(users)}\n")

# ============================
# 1. Uniqueness Checks
# ============================

ids = [u["_id"] for u in users]
names = [u.get("full_name", "") for u in users]

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
    "root": {
        "_id", "full_name", "email", "phone", "age", "gender", "occupation", "bio",
        "city", "locality", "latitude", "longitude",
        "home_city", "home_locality", "home_latitude", "home_longitude",
        "sleep_schedule", "cleanliness", "noise_tolerance", "cooking_frequency",
        "guest_frequency", "workout_habit", "introversion_extroversion", "communication_style",
        "conflict_resolution", "social_battery", "budget_min", "budget_max", "smoking",
        "drinking", "veg_nonveg", "gender_preference", "pet_friendly", "preferred_move_in",
        "interests", "profile_complete", "is_looking"
    },
}

schema_errors = []
for i, u in enumerate(users):
    missing = REQUIRED_KEYS["root"] - set(u.keys())
    if missing:
        schema_errors.append(f"  User {i} ({u.get('_id','?')[:8]}): missing keys {missing}")

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
    name = u.get("full_name")

    if not (18 <= int(u.get("age", 0)) <= 65):
        range_issues.append(f"  User {i} '{name}': age={u.get('age')}")
    if u.get("gender") not in ("male", "female", "non-binary"):
        range_issues.append(f"  User {i} '{name}': gender={u.get('gender')}")
    if u.get("occupation") not in ("student", "working_professional", "freelancer"):
        range_issues.append(f"  User {i} '{name}': occupation={u.get('occupation')}")
    for key in (
        "sleep_schedule", "cleanliness", "noise_tolerance", "cooking_frequency", "guest_frequency",
        "workout_habit", "introversion_extroversion", "communication_style", "conflict_resolution", "social_battery"
    ):
        val = int(u.get(key, 0))
        if not (1 <= val <= 5):
            range_issues.append(f"  User {i} '{name}': {key}={val}")

    bmin = int(u.get("budget_min", 0))
    bmax = int(u.get("budget_max", 0))
    if bmin < 0 or bmax < 0 or bmin > bmax:
        range_issues.append(f"  User {i} '{name}': budget_min={bmin}, budget_max={bmax}")

    if u.get("smoking") not in ("never", "occasionally", "regularly"):
        range_issues.append(f"  User {i} '{name}': smoking={u.get('smoking')}")
    if u.get("drinking") not in ("never", "occasionally", "regularly"):
        range_issues.append(f"  User {i} '{name}': drinking={u.get('drinking')}")
    if u.get("veg_nonveg") not in ("veg", "nonveg", "eggetarian", "vegan"):
        range_issues.append(f"  User {i} '{name}': veg_nonveg={u.get('veg_nonveg')}")
    if u.get("gender_preference") not in ("male", "female", "any"):
        range_issues.append(f"  User {i} '{name}': gender_preference={u.get('gender_preference')}")
    if u.get("preferred_move_in") not in ("immediate", "within_month", "flexible"):
        range_issues.append(f"  User {i} '{name}': preferred_move_in={u.get('preferred_move_in')}")

    lat = float(u.get("latitude", 0))
    lng = float(u.get("longitude", 0))
    if not (17.78 <= lat <= 22.73 and 81.37 <= lng <= 87.53):
        range_issues.append(f"  User {i} '{name}': lat/lng [{lat}, {lng}] outside Odisha bbox")

    home_lat = float(u.get("home_latitude", 0))
    home_lng = float(u.get("home_longitude", 0))
    if not (17.78 <= home_lat <= 22.73 and 81.37 <= home_lng <= 87.53):
        range_issues.append(f"  User {i} '{name}': home_lat/lng [{home_lat}, {home_lng}] outside Odisha bbox")

    if not isinstance(u.get("interests", []), list):
        range_issues.append(f"  User {i} '{name}': interests is not a list")

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

genders = Counter(u["gender"] for u in users)
occupations = Counter(u["occupation"] for u in users)
localities = Counter(u["locality"] for u in users)
home_localities = Counter(u["home_locality"] for u in users)
move_in = Counter(u["preferred_move_in"] for u in users)
smoking = Counter(u["smoking"] for u in users)
drinking = Counter(u["drinking"] for u in users)
food = Counter(u["veg_nonveg"] for u in users)
gender_pref = Counter(u["gender_preference"] for u in users)
pet_friendly = Counter(u["pet_friendly"] for u in users)
budget_mins = [u["budget_min"] for u in users]
budget_maxs = [u["budget_max"] for u in users]
ages = [u["age"] for u in users]

print(f"\n=== DISTRIBUTIONS ===")
print(f"  Gender:       {dict(genders)}")
print(f"  Occupation:   {dict(occupations)}")
print(f"  Move-in:      {dict(move_in)}")
print(f"  Smoking:      {dict(smoking)}")
print(f"  Drinking:     {dict(drinking)}")
print(f"  Food pref:    {dict(food)}")
print(f"  Pet friendly: {dict(pet_friendly)}")
print(f"  Gender pref:  {dict(gender_pref)}")
print(f"  Age range:    {min(ages)}-{max(ages)}, avg={sum(ages)/len(ages):.1f}")
print(f"  Budget min range: ₹{min(budget_mins)}-₹{max(budget_mins)}")
print(f"  Budget max range: ₹{min(budget_maxs)}-₹{max(budget_maxs)}")
print(f"  Localities ({len(localities)} unique): {localities.most_common(10)}")
print(f"  Home localities ({len(home_localities)} unique): {home_localities.most_common(10)}")

# ============================
# 5. Pairwise Similarity Sample
# ============================

def similarity_score(u1, u2):
    """Simple similarity score over frontend fields."""
    score = 0
    total = 0

    # Budget overlap
    total += 1
    if not (u1["budget_min"] > u2["budget_max"] or u2["budget_min"] > u1["budget_max"]):
        score += 1

    # Gender preference match
    total += 1
    g1_ok = u1["gender_preference"] == "any" or u1["gender_preference"] == u2["gender"]
    g2_ok = u2["gender_preference"] == "any" or u2["gender_preference"] == u1["gender"]
    if g1_ok and g2_ok:
        score += 1

    # Smoking
    total += 1
    if u1["smoking"] == u2["smoking"]:
        score += 1

    # Pets
    total += 1
    if u1["pet_friendly"] == u2["pet_friendly"]:
        score += 1

    # Sleep schedule
    total += 1
    if abs(u1["sleep_schedule"] - u2["sleep_schedule"]) <= 1:
        score += 1

    # Cleanliness (within 1)
    total += 1
    if abs(u1["cleanliness"] - u2["cleanliness"]) <= 1:
        score += 1

    # Noise tolerance (within 1)
    total += 1
    if abs(u1["noise_tolerance"] - u2["noise_tolerance"]) <= 1:
        score += 1

    # Intro/extro (within 1)
    total += 1
    if abs(u1["introversion_extroversion"] - u2["introversion_extroversion"]) <= 1:
        score += 1

    # Same locality
    total += 1
    if u1["locality"] == u2["locality"]:
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
    name_i = users[i]["full_name"]
    name_j = users[j]["full_name"]
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
        best = (users[i]["full_name"], users[j]["full_name"], pct)
    if pct < worst[2]:
        worst = (users[i]["full_name"], users[j]["full_name"], pct)

print(f"  Checked {pairs_checked} random pairs")
print(f"  🔥 Most similar:  {best[0]} & {best[1]} → {best[2]:.0f}%")
print(f"  ❄️  Least similar: {worst[0]} & {worst[1]} → {worst[2]:.0f}%")

# Check for exact duplicates (identical persona+preferences)
print(f"\n=== EXACT DUPLICATE CHECK (core compatibility fields) ===")
fingerprints = {}
exact_dups = 0
for u in users:
    fp = json.dumps({
        "sleep_schedule": u["sleep_schedule"],
        "cleanliness": u["cleanliness"],
        "noise_tolerance": u["noise_tolerance"],
        "cooking_frequency": u["cooking_frequency"],
        "guest_frequency": u["guest_frequency"],
        "workout_habit": u["workout_habit"],
        "introversion_extroversion": u["introversion_extroversion"],
        "communication_style": u["communication_style"],
        "conflict_resolution": u["conflict_resolution"],
        "social_battery": u["social_battery"],
        "budget_min": u["budget_min"],
        "budget_max": u["budget_max"],
        "smoking": u["smoking"],
        "drinking": u["drinking"],
        "veg_nonveg": u["veg_nonveg"],
        "gender_preference": u["gender_preference"],
        "pet_friendly": u["pet_friendly"],
    }, sort_keys=True)
    if fp in fingerprints:
        exact_dups += 1
        if exact_dups <= 5:
            print(f"  ⚠ '{u['full_name']}' has same core profile as '{fingerprints[fp]}'")
    else:
        fingerprints[fp] = u["full_name"]

if exact_dups == 0:
    print("  ✅ No exact duplicates in core compatibility fields!")
else:
    print(f"  Total exact duplicates: {exact_dups}")

print("\n✅ Validation complete.")

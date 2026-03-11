import json
import math

with open("odisha_users.json", "r") as f:
    users = json.load(f)

print(f"Loaded {len(users)} users\n")

# ============================
# Weighted Similarity Scoring
# ============================

def geo_distance_km(c1, c2):
    """Haversine distance between two [lon, lat] coords in km."""
    lon1, lat1 = math.radians(c1[0]), math.radians(c1[1])
    lon2, lat2 = math.radians(c2[0]), math.radians(c2[1])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = math.sin(dlat/2)**2 + math.cos(lat1)*math.cos(lat2)*math.sin(dlon/2)**2
    return 6371 * 2 * math.asin(math.sqrt(a))

def compatibility_score(u1, u2):
    """Returns a 0-100 compatibility score with weighted criteria."""
    score = 0
    max_score = 0

    p1, p2 = u1["preferences"], u2["preferences"]
    r1, r2 = u1["persona_raw"], u2["persona_raw"]
    l1, l2 = u1["location"], u2["location"]
    pr1, pr2 = u1["profile"], u2["profile"]

    # --- Budget compatibility (weight: 20) ---
    max_score += 20
    budget_diff = abs(p1["budget"] - p2["budget"])
    if budget_diff <= 1000:
        score += 20
    elif budget_diff <= 3000:
        score += 15
    elif budget_diff <= 5000:
        score += 8

    # --- Gender preference match (weight: 15) ---
    max_score += 15
    g1_ok = p1["gender_preference"] == "Any" or p1["gender_preference"] == pr2["gender"]
    g2_ok = p2["gender_preference"] == "Any" or p2["gender_preference"] == pr1["gender"]
    if g1_ok and g2_ok:
        score += 15
    elif g1_ok or g2_ok:
        score += 5

    # --- Sleep schedule (weight: 15) ---
    max_score += 15
    if r1["sleep_time"] == r2["sleep_time"]:
        score += 15

    # --- Cleanliness (weight: 15) ---
    max_score += 15
    clean_diff = abs(r1["cleanliness_rating"] - r2["cleanliness_rating"])
    if clean_diff == 0:
        score += 15
    elif clean_diff == 1:
        score += 10
    elif clean_diff == 2:
        score += 4

    # --- Noise tolerance (weight: 10) ---
    max_score += 10
    noise_diff = abs(r1["noise_tolerance"] - r2["noise_tolerance"])
    if noise_diff == 0:
        score += 10
    elif noise_diff == 1:
        score += 7
    elif noise_diff == 2:
        score += 3

    # --- Introversion compatibility (weight: 10) ---
    max_score += 10
    intro_diff = abs(r1["introversion_score"] - r2["introversion_score"])
    if intro_diff == 0:
        score += 10
    elif intro_diff == 1:
        score += 7
    elif intro_diff == 2:
        score += 3

    # --- Smoking tolerance (weight: 5) ---
    max_score += 5
    if p1["smoking_tolerance"] == p2["smoking_tolerance"]:
        score += 5

    # --- Pets (weight: 5) ---
    max_score += 5
    if p1["pets_allowed"] == p2["pets_allowed"]:
        score += 5

    # --- Location proximity (weight: 5) ---
    max_score += 5
    dist = geo_distance_km(l1["coordinates"], l2["coordinates"])
    if dist <= 10:
        score += 5
    elif dist <= 30:
        score += 3
    elif dist <= 60:
        score += 1

    return round(score / max_score * 100, 1), dist

# ============================
# Find Top Matches for Each User
# ============================

def find_top_matches(user_idx, top_n=5):
    matches = []
    for j in range(len(users)):
        if j == user_idx:
            continue
        compat, dist = compatibility_score(users[user_idx], users[j])
        matches.append((j, compat, dist))
    matches.sort(key=lambda x: -x[1])
    return matches[:top_n]

def print_user_brief(u):
    p = u["profile"]
    pref = u["preferences"]
    r = u["persona_raw"]
    loc = u["location"]
    print(f"    {p['name']}, {p['age']}{p['gender'][0]} | {loc['area_name']} | ₹{pref['budget']}")
    print(f"    Sleep:{r['sleep_time']} Clean:{r['cleanliness_rating']} Noise:{r['noise_tolerance']} Intro:{r['introversion_score']} | Smoke:{pref['smoking_tolerance']} Pets:{pref['pets_allowed']} | Wants:{pref['gender_preference']}")

# Show matches for 10 sample users
print("=" * 70)
print("TOP 5 MATCHES FOR 10 SAMPLE USERS")
print("=" * 70)

import random
random.seed(123)
samples = random.sample(range(len(users)), 10)

for idx in samples:
    u = users[idx]
    print(f"\n🔍 User #{idx}: {u['profile']['name']}")
    print_user_brief(u)
    print(f"  Best matches:")
    for rank, (j, compat, dist) in enumerate(find_top_matches(idx), 1):
        m = users[j]
        print(f"    {rank}. [{compat}%] {m['profile']['name']}, {m['profile']['age']}{m['profile']['gender'][0]} | {m['location']['area_name']} | ₹{m['preferences']['budget']} | {dist:.0f}km away")

# ============================
# Global Best Pairs
# ============================

print("\n" + "=" * 70)
print("TOP 20 MOST COMPATIBLE PAIRS (full scan)")
print("=" * 70)

all_pairs = []
for i in range(len(users)):
    for j in range(i + 1, len(users)):
        compat, dist = compatibility_score(users[i], users[j])
        if compat >= 85:  # only track high matches to save memory
            all_pairs.append((i, j, compat, dist))

all_pairs.sort(key=lambda x: -x[2])

for rank, (i, j, compat, dist) in enumerate(all_pairs[:20], 1):
    u1, u2 = users[i], users[j]
    print(f"  {rank:2d}. [{compat}%] {u1['profile']['name']:25s} ↔ {u2['profile']['name']:25s} | {dist:.0f}km apart")

# Stats
print(f"\n=== MATCH STATS ===")
print(f"  Pairs with ≥85% compatibility: {len(all_pairs)}")
compat_90 = sum(1 for p in all_pairs if p[2] >= 90)
compat_95 = sum(1 for p in all_pairs if p[2] >= 95)
print(f"  Pairs with ≥90%: {compat_90}")
print(f"  Pairs with ≥95%: {compat_95}")
print(f"  Perfect 100%: {sum(1 for p in all_pairs if p[2] >= 100)}")

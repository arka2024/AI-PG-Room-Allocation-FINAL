import hashlib
import json
import random

ODISHA_DISTRICTS = {
    "Khordha": (85.83, 20.18),
    "Cuttack": (85.88, 20.46),
    "Puri": (85.83, 19.81),
    "Ganjam": (84.68, 19.59),
    "Sambalpur": (83.97, 21.47),
    "Balasore": (86.93, 21.49),
    "Sundargarh": (84.04, 22.12),
    "Mayurbhanj": (86.34, 21.94),
    "Koraput": (82.71, 18.81),
    "Jajpur": (86.33, 20.85),
    "Kendrapara": (86.42, 20.50),
    "Boudh": (84.32, 20.84),
    "Angul": (85.10, 20.84),
    "Dhenkanal": (85.60, 20.67),
    "Nayagarh": (85.10, 20.13),
    "Kalahandi": (83.17, 19.91),
    "Rayagada": (83.42, 19.17),
    "Bargarh": (83.62, 21.33),
    "Jharsuguda": (84.01, 21.86),
    "Bhadrak": (86.52, 21.05),
    "Bolangir": (83.49, 20.70),
    "Deogarh": (84.73, 21.54),
    "Gajapati": (84.13, 19.22),
    "Jagatsinghpur": (86.17, 20.26),
    "Kandhamal": (84.07, 20.30),
    "Keonjhar": (85.58, 21.63),
    "Malkangiri": (81.88, 18.35),
    "Nabarangpur": (82.55, 19.23),
    "Nuapada": (82.55, 20.80),
    "Subarnapur": (83.87, 20.83),
}

CITIES = ["Bhubaneswar", "Cuttack", "Puri", "Rourkela", "Sambalpur", "Berhampur"]
INTERESTS_POOL = [
    "Reading", "Music", "Gaming", "Cooking", "Fitness", "Movies", "Travel", "Photography",
    "Cricket", "Coding", "Badminton", "Yoga", "Dancing", "Art", "Cycling"
]


def _norm_gender(g):
    g = str(g or "").strip().lower()
    if g in ("male", "m"):
        return "male"
    if g in ("female", "f"):
        return "female"
    return random.choice(["male", "female", "non-binary"])


def _to_sleep_value(s):
    s = str(s or "").strip().lower()
    if s == "early":
        return random.choice([1, 2])
    if s == "late":
        return random.choice([4, 5])
    return 3


def _safe_int(v, low, high, default):
    try:
        iv = int(v)
    except (TypeError, ValueError):
        iv = default
    return max(low, min(high, iv))


def _synthetic_email(name):
    slug = "".join(ch.lower() for ch in name if ch.isalnum())
    return f"{slug[:18]}@synthetic.local"


def convert_user(u):
    # Pass through if already in new flat shape.
    if "full_name" in u and "sleep_schedule" in u:
        if "_id" not in u:
            u["_id"] = hashlib.sha1(u["full_name"].encode()).hexdigest()
        return u

    profile = u.get("profile", {})
    location = u.get("location", {})
    preferences = u.get("preferences", {})
    persona = u.get("persona_raw", {})

    name = profile.get("name", "Unknown User")
    gender = _norm_gender(profile.get("gender"))
    age = _safe_int(profile.get("age", 22), 18, 65, 22)

    area = location.get("area_name")
    if area not in ODISHA_DISTRICTS:
        area = random.choice(list(ODISHA_DISTRICTS.keys()))

    coords = location.get("coordinates", [])
    if isinstance(coords, list) and len(coords) == 2:
        lon, lat = float(coords[0]), float(coords[1])
    else:
        base_lon, base_lat = ODISHA_DISTRICTS[area]
        lon = round(base_lon + random.uniform(-0.12, 0.12), 6)
        lat = round(base_lat + random.uniform(-0.12, 0.12), 6)

    budget = _safe_int(preferences.get("budget", 8000), 3000, 25000, 8000)
    budget_min = max(3000, budget - random.randint(1000, 2500))
    budget_max = min(25000, max(budget_min + 1000, budget + random.randint(1000, 3500)))

    gender_pref_raw = str(preferences.get("gender_preference", "Any")).strip().lower()
    gender_pref = gender_pref_raw if gender_pref_raw in ("male", "female", "any") else "any"

    smoke_tol = bool(preferences.get("smoking_tolerance", False))
    smoking = random.choice(["occasionally", "regularly"]) if smoke_tol else random.choice(["never", "occasionally"])

    intro_raw = _safe_int(persona.get("introversion_score", 3), 1, 5, 3)
    intro_extro = 6 - intro_raw

    interests = random.sample(INTERESTS_POOL, k=random.randint(3, 5))

    flat = {
        "_id": u.get("_id") or hashlib.sha1(name.encode()).hexdigest(),
        "full_name": name,
        "email": _synthetic_email(name),
        "phone": f"9{random.randint(100000000, 999999999)}",
        "age": age,
        "gender": gender,
        "occupation": random.choice(["student", "working_professional", "freelancer"]),
        "bio": profile.get("bio") or "Friendly and responsible roommate looking for a compatible shared space.",
        "city": random.choice(CITIES),
        "locality": area,
        "latitude": round(lat, 6),
        "longitude": round(lon, 6),
        "sleep_schedule": _to_sleep_value(persona.get("sleep_time")),
        "cleanliness": _safe_int(persona.get("cleanliness_rating", 3), 1, 5, 3),
        "noise_tolerance": _safe_int(persona.get("noise_tolerance", 3), 1, 5, 3),
        "cooking_frequency": random.randint(1, 5),
        "guest_frequency": random.randint(1, 5),
        "workout_habit": random.randint(1, 5),
        "introversion_extroversion": intro_extro,
        "communication_style": random.randint(1, 5),
        "conflict_resolution": random.randint(1, 5),
        "social_battery": random.randint(1, 5),
        "budget_min": budget_min,
        "budget_max": budget_max,
        "smoking": smoking,
        "drinking": random.choice(["never", "occasionally", "regularly"]),
        "veg_nonveg": random.choice(["veg", "nonveg", "eggetarian", "vegan"]),
        "gender_preference": gender_pref,
        "pet_friendly": bool(preferences.get("pets_allowed", random.choice([True, False]))),
        "preferred_move_in": random.choice(["immediate", "within_month", "flexible"]),
        "interests": interests,
        "avatar_url": None,
        "profile_complete": True,
        "is_looking": True,
    }
    return flat


def main():
    with open("odisha_users.json", "r", encoding="utf-8") as f:
        users = json.load(f)

    converted = [convert_user(u) for u in users]

    # De-duplicate ids if any collision occurs.
    seen = set()
    for u in converted:
        uid = u["_id"]
        if uid in seen:
            u["_id"] = hashlib.sha1((u["full_name"] + str(random.random())).encode()).hexdigest()
        seen.add(u["_id"])

    with open("odisha_users.json", "w", encoding="utf-8") as f:
        json.dump(converted, f, indent=2)

    print(f"Converted {len(converted)} users to frontend schema in odisha_users.json")


if __name__ == "__main__":
    main()

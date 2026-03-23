import hashlib
import json
import os
import random
import time

import requests
from dotenv import load_dotenv


# ============================
# Gemini API Configuration
# ============================

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemma-3-27b-it"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

HEADERS = {
    "Content-Type": "application/json"
}

TARGET = 500
BATCH_SIZE = 5
MAX_RETRIES = 5
OUTPUT_FILE = "odisha_users.json"


# Odisha geographic extent (for clipping and validation)
ODISHA_LAT_MIN = 17.78
ODISHA_LAT_MAX = 22.73
ODISHA_LON_MIN = 81.37
ODISHA_LON_MAX = 87.53


DISTRICT_CENTERS = {
    "Khordha": (85.8245, 20.2961, "Bhubaneswar"),
    "Cuttack": (85.8828, 20.4625, "Cuttack"),
    "Puri": (85.8312, 19.8135, "Puri"),
    "Ganjam": (84.7941, 19.3149, "Berhampur"),
    "Sambalpur": (83.9701, 21.4704, "Sambalpur"),
    "Balasore": (86.9335, 21.4942, "Balasore"),
    "Sundargarh": (84.0281, 22.1170, "Rourkela"),
    "Mayurbhanj": (86.7218, 21.9360, "Baripada"),
    "Koraput": (82.7105, 18.8135, "Koraput"),
    "Jharsuguda": (84.0062, 21.8554, "Jharsuguda"),
    "Jajpur": (86.3333, 20.8500, "Jajpur"),
    "Kendrapara": (86.4234, 20.5016, "Kendrapara"),
    "Angul": (85.0985, 20.8445, "Angul"),
    "Dhenkanal": (85.5958, 20.6653, "Dhenkanal"),
    "Rayagada": (83.4160, 19.1712, "Rayagada"),
    "Kalahandi": (83.1688, 19.9074, "Bhawanipatna"),
}

PG_HUB_WEIGHTS = {
    "Khordha": 0.26,
    "Cuttack": 0.18,
    "Sundargarh": 0.11,
    "Sambalpur": 0.11,
    "Ganjam": 0.10,
    "Balasore": 0.07,
    "Puri": 0.06,
    "Angul": 0.04,
    "Jharsuguda": 0.04,
    "Koraput": 0.03,
}


MALE_FIRST = [
    "Akash", "Amit", "Anil", "Ankit", "Arun", "Ashish", "Bibhu", "Bikash", "Biswa", "Chandan",
    "Deepak", "Dilip", "Ganesh", "Girish", "Hari", "Hemant", "Jatin", "Jayant", "Kailash", "Kamal",
    "Kiran", "Kishore", "Krishna", "Manas", "Manoj", "Milan", "Mohan", "Mukesh", "Nikhil", "Omkar",
    "Pankaj", "Prakash", "Pramod", "Pranav", "Rajat", "Rajesh", "Rakesh", "Ranjan", "Ravi", "Rohit",
    "Roshan", "Sachin", "Sagar", "Sandeep", "Sanjay", "Santosh", "Saroj", "Satya", "Shashank", "Shiva",
    "Siddharth", "Soumya", "Subash", "Sudhir", "Sunil", "Surya", "Tarun", "Tushar", "Umesh", "Varun",
    "Vijay", "Vikash", "Vinod", "Yash", "Yogesh", "Abhinav", "Ajit", "Alok", "Bipin", "Gopal",
]

FEMALE_FIRST = [
    "Aditi", "Anjali", "Anita", "Ankita", "Anuradha", "Archana", "Barsha", "Bharati", "Deepa", "Dipti",
    "Gargi", "Gayatri", "Gita", "Isha", "Itishree", "Jyoti", "Kalpana", "Kavita", "Lata", "Lipika",
    "Madhusmita", "Mamata", "Manaswini", "Manisha", "Monalisa", "Namrata", "Nandini", "Neha", "Nibedita", "Pallavi",
    "Pragnya", "Pratibha", "Preeti", "Priya", "Puja", "Rachana", "Ranjita", "Rashmi", "Reema", "Ritu",
    "Sakshi", "Sangita", "Sanjukta", "Sarita", "Shilpa", "Shruti", "Sima", "Smita", "Sneha", "Sonali",
    "Subhashree", "Sucharita", "Sudha", "Sunita", "Supriya", "Swati", "Tanuja", "Uma", "Urmila", "Varsha",
]

LAST_NAMES = [
    "Behera", "Das", "Mishra", "Mohanty", "Nayak", "Panda", "Pradhan", "Rout", "Sahu", "Sahoo", "Sethi", "Swain",
    "Tripathy", "Barik", "Biswal", "Dalai", "Dash", "Jena", "Lenka", "Mahapatra", "Malik", "Meher", "Naik", "Parida",
    "Patra", "Samantaray", "Senapati", "Singh", "Acharya", "Bhoi", "Chand", "Dehury", "Dhal", "Giri", "Kar", "Khatua",
    "Maharana", "Majhi", "Mohapatra", "Palai", "Rath", "Ray", "Satpathy", "Sutar", "Tandi", "Bag", "Lakra", "Munda",
]

INTERESTS_POOL = [
    "Reading", "Music", "Gaming", "Cooking", "Fitness", "Movies", "Travel", "Photography", "Cricket", "Coding",
    "Badminton", "Yoga", "Dancing", "Art", "Cycling", "Hiking", "Tea", "Board Games", "Meditation", "Volunteering",
]


ARCHETYPES = {
    "organized_professional": {
        "sleep_schedule": 2,
        "cleanliness": 5,
        "noise_tolerance": 2,
        "cooking_frequency": 3,
        "guest_frequency": 2,
        "workout_habit": 4,
        "introversion_extroversion": 3,
        "communication_style": 4,
        "conflict_resolution": 4,
        "social_battery": 3,
        "smoking": "never",
        "drinking": "occasionally",
    },
    "social_extrovert": {
        "sleep_schedule": 4,
        "cleanliness": 3,
        "noise_tolerance": 4,
        "cooking_frequency": 2,
        "guest_frequency": 5,
        "workout_habit": 3,
        "introversion_extroversion": 5,
        "communication_style": 5,
        "conflict_resolution": 3,
        "social_battery": 5,
        "smoking": "occasionally",
        "drinking": "occasionally",
    },
    "quiet_student": {
        "sleep_schedule": 2,
        "cleanliness": 4,
        "noise_tolerance": 2,
        "cooking_frequency": 2,
        "guest_frequency": 1,
        "workout_habit": 2,
        "introversion_extroversion": 2,
        "communication_style": 3,
        "conflict_resolution": 2,
        "social_battery": 2,
        "smoking": "never",
        "drinking": "never",
    },
    "night_owl_creator": {
        "sleep_schedule": 5,
        "cleanliness": 3,
        "noise_tolerance": 5,
        "cooking_frequency": 2,
        "guest_frequency": 2,
        "workout_habit": 1,
        "introversion_extroversion": 2,
        "communication_style": 3,
        "conflict_resolution": 2,
        "social_battery": 2,
        "smoking": "occasionally",
        "drinking": "regularly",
    },
}


PROMPT_TEMPLATE = """
You are generating realistic synthetic user profiles for an Odisha roommate/PG matching app.

Generate exactly {batch} JSON records as an array for these assigned identities:
{name_list}

Output rules:
- Output ONLY valid JSON array.
- No markdown fences, no extra text.
- Keep records realistic and varied.
- Use Odisha-only coordinates.

Schema for each object (all required):
{{
  "full_name": "assigned full name exactly",
  "age": integer 18-34,
  "gender": "male" | "female" | "non-binary",
  "occupation": "student" | "working_professional" | "freelancer",
  "phone": "10-digit string",
  "bio": "one sentence",

  "city": "PG target city in Odisha",
  "locality": "PG target district/locality in Odisha",
  "latitude": number,
  "longitude": number,

  "home_city": "origin city in Odisha",
  "home_locality": "origin district/locality in Odisha",
  "home_latitude": number,
  "home_longitude": number,

  "sleep_schedule": integer 1-5,
  "cleanliness": integer 1-5,
  "noise_tolerance": integer 1-5,
  "cooking_frequency": integer 1-5,
  "guest_frequency": integer 1-5,
  "workout_habit": integer 1-5,
  "introversion_extroversion": integer 1-5,
  "communication_style": integer 1-5,
  "conflict_resolution": integer 1-5,
  "social_battery": integer 1-5,

  "budget_min": integer >=3000,
  "budget_max": integer >= budget_min,
  "smoking": "never" | "occasionally" | "regularly",
  "drinking": "never" | "occasionally" | "regularly",
  "veg_nonveg": "veg" | "nonveg" | "eggetarian" | "vegan",
  "gender_preference": "male" | "female" | "any",
  "pet_friendly": boolean,
  "preferred_move_in": "immediate" | "within_month" | "flexible",
  "interests": [2 to 6 short strings],

  "avatar_url": null,
  "profile_complete": true,
  "is_looking": true
}}

Geography constraints for Odisha:
- Latitude must be between 17.78 and 22.73.
- Longitude must be between 81.37 and 87.53.

Use realistic Odisha places like Bhubaneswar, Cuttack, Puri, Berhampur, Sambalpur, Rourkela, Balasore, Angul, etc.
"""


def clamp(v, low, high):
    return max(low, min(high, v))


def jitter_location(base_lon, base_lat, spread=0.2):
    lon = clamp(base_lon + random.uniform(-spread, spread), ODISHA_LON_MIN, ODISHA_LON_MAX)
    lat = clamp(base_lat + random.uniform(-spread, spread), ODISHA_LAT_MIN, ODISHA_LAT_MAX)
    return round(lon, 6), round(lat, 6)


def weighted_choice(weight_map):
    items = list(weight_map.keys())
    weights = list(weight_map.values())
    return random.choices(items, weights=weights, k=1)[0]


def normalize_gender_for_ui(gender):
    gender = str(gender).strip().lower()
    if gender in ("male", "female", "non-binary"):
        return gender
    return "male"


def clean_json_text(text):
    text = text.strip()

    if "```" in text:
        parts = text.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("json"):
                stripped = stripped[4:].strip()
            if stripped.startswith("["):
                text = stripped
                break

    start = text.find("[")
    end = text.rfind("]")
    if start != -1 and end != -1 and end > start:
        text = text[start:end + 1]

    return text.strip()


def choose_name_gender(used_names):
    while True:
        gender = random.choices(["male", "female", "non-binary"], weights=[0.49, 0.49, 0.02], k=1)[0]
        first_pool = FEMALE_FIRST if gender == "female" else MALE_FIRST
        full_name = f"{random.choice(first_pool)} {random.choice(LAST_NAMES)}"
        if full_name not in used_names:
            used_names.add(full_name)
            return full_name, gender


def generate_unique_id(name, idx):
    return hashlib.sha1(f"{name}-{idx}".encode("utf-8")).hexdigest()


def generate_email(name, idx):
    slug = "".join(ch.lower() for ch in name if ch.isalnum())
    return f"{slug[:16]}{idx % 97:02d}@synthetic.local"


def generate_phone():
    return f"9{random.randint(100000000, 999999999)}"


def pick_interests(archetype_key):
    base_map = {
        "organized_professional": ["Reading", "Fitness", "Cooking", "Meditation", "Travel"],
        "social_extrovert": ["Music", "Dancing", "Travel", "Cricket", "Movies"],
        "quiet_student": ["Reading", "Coding", "Tea", "Board Games", "Badminton"],
        "night_owl_creator": ["Music", "Gaming", "Photography", "Art", "Movies"],
    }
    seed = base_map.get(archetype_key, ["Reading", "Music", "Cooking"])
    picks = set(random.sample(seed, k=min(len(seed), random.randint(2, 4))))
    while len(picks) < random.randint(3, 6):
        picks.add(random.choice(INTERESTS_POOL))
    return sorted(picks)


def fallback_record(name, gender, idx):
    age = random.randint(18, 34)
    occupation = random.choices(
        ["student", "working_professional", "freelancer"],
        weights=[0.45, 0.4, 0.15],
        k=1,
    )[0]

    home_district = random.choice(list(DISTRICT_CENTERS.keys()))
    home_lon0, home_lat0, home_city = DISTRICT_CENTERS[home_district]
    home_lon, home_lat = jitter_location(home_lon0, home_lat0, spread=0.26)

    pg_district = weighted_choice(PG_HUB_WEIGHTS)
    pg_lon0, pg_lat0, pg_city = DISTRICT_CENTERS[pg_district]
    pg_lon, pg_lat = jitter_location(pg_lon0, pg_lat0, spread=0.2)

    archetype_key = random.choice(list(ARCHETYPES.keys()))
    archetype = ARCHETYPES[archetype_key]

    budget_anchor = random.randint(7000, 16000) if occupation != "student" else random.randint(4200, 9000)
    budget_min = max(3000, budget_anchor - random.randint(1200, 3000))
    budget_max = max(budget_min + 1000, budget_anchor + random.randint(1500, 4500))

    return {
        "full_name": name,
        "age": age,
        "gender": normalize_gender_for_ui(gender),
        "occupation": occupation,
        "phone": generate_phone(),
        "bio": f"{name.split()[0]} is friendly, responsible, and looking for a compatible PG roommate setup.",
        "city": pg_city,
        "locality": pg_district,
        "latitude": pg_lat,
        "longitude": pg_lon,
        "home_city": home_city,
        "home_locality": home_district,
        "home_latitude": home_lat,
        "home_longitude": home_lon,
        "sleep_schedule": int(clamp(archetype["sleep_schedule"] + random.choice([-1, 0, 1]), 1, 5)),
        "cleanliness": int(clamp(archetype["cleanliness"] + random.choice([-1, 0, 1]), 1, 5)),
        "noise_tolerance": int(clamp(archetype["noise_tolerance"] + random.choice([-1, 0, 1]), 1, 5)),
        "cooking_frequency": int(clamp(archetype["cooking_frequency"] + random.choice([-1, 0, 1]), 1, 5)),
        "guest_frequency": int(clamp(archetype["guest_frequency"] + random.choice([-1, 0, 1]), 1, 5)),
        "workout_habit": int(clamp(archetype["workout_habit"] + random.choice([-1, 0, 1]), 1, 5)),
        "introversion_extroversion": int(clamp(archetype["introversion_extroversion"] + random.choice([-1, 0, 1]), 1, 5)),
        "communication_style": int(clamp(archetype["communication_style"] + random.choice([-1, 0, 1]), 1, 5)),
        "conflict_resolution": int(clamp(archetype["conflict_resolution"] + random.choice([-1, 0, 1]), 1, 5)),
        "social_battery": int(clamp(archetype["social_battery"] + random.choice([-1, 0, 1]), 1, 5)),
        "budget_min": int(budget_min),
        "budget_max": int(min(26000, budget_max)),
        "smoking": archetype["smoking"],
        "drinking": archetype["drinking"],
        "veg_nonveg": random.choice(["veg", "nonveg", "eggetarian", "vegan"]),
        "gender_preference": random.choice(["any", "male", "female"]),
        "pet_friendly": random.choice([True, False]),
        "preferred_move_in": random.choice(["immediate", "within_month", "flexible"]),
        "interests": pick_interests(archetype_key),
        "avatar_url": None,
        "profile_complete": True,
        "is_looking": True,
    }


def validate_and_fix_user(user, expected_name, expected_gender, idx):
    user = user if isinstance(user, dict) else {}

    # Base fallback to guarantee complete schema.
    base = fallback_record(expected_name, expected_gender, idx)

    merged = {**base, **user}
    merged["full_name"] = expected_name
    merged["gender"] = normalize_gender_for_ui(expected_gender)

    merged["age"] = int(clamp(int(merged.get("age", base["age"])), 18, 34))
    if merged.get("occupation") not in ("student", "working_professional", "freelancer"):
        merged["occupation"] = base["occupation"]

    merged["phone"] = str(merged.get("phone", base["phone"]))
    digits_only = "".join(ch for ch in merged["phone"] if ch.isdigit())
    if len(digits_only) >= 10:
        merged["phone"] = digits_only[-10:]
    else:
        merged["phone"] = base["phone"]

    for coord_field, low, high in (
        ("latitude", ODISHA_LAT_MIN, ODISHA_LAT_MAX),
        ("longitude", ODISHA_LON_MIN, ODISHA_LON_MAX),
        ("home_latitude", ODISHA_LAT_MIN, ODISHA_LAT_MAX),
        ("home_longitude", ODISHA_LON_MIN, ODISHA_LON_MAX),
    ):
        try:
            merged[coord_field] = round(float(merged.get(coord_field, base[coord_field])), 6)
        except (TypeError, ValueError):
            merged[coord_field] = base[coord_field]
        merged[coord_field] = round(clamp(merged[coord_field], low, high), 6)

    if merged.get("locality") not in DISTRICT_CENTERS:
        merged["locality"] = base["locality"]
    if merged.get("home_locality") not in DISTRICT_CENTERS:
        merged["home_locality"] = base["home_locality"]

    if not merged.get("city"):
        merged["city"] = base["city"]
    if not merged.get("home_city"):
        merged["home_city"] = base["home_city"]

    for key in (
        "sleep_schedule", "cleanliness", "noise_tolerance", "cooking_frequency", "guest_frequency",
        "workout_habit", "introversion_extroversion", "communication_style", "conflict_resolution", "social_battery",
    ):
        try:
            merged[key] = int(merged.get(key, base[key]))
        except (TypeError, ValueError):
            merged[key] = base[key]
        merged[key] = int(clamp(merged[key], 1, 5))

    try:
        merged["budget_min"] = int(merged.get("budget_min", base["budget_min"]))
    except (TypeError, ValueError):
        merged["budget_min"] = base["budget_min"]
    try:
        merged["budget_max"] = int(merged.get("budget_max", base["budget_max"]))
    except (TypeError, ValueError):
        merged["budget_max"] = base["budget_max"]

    merged["budget_min"] = max(3000, merged["budget_min"])
    merged["budget_max"] = max(merged["budget_min"] + 1000, min(26000, merged["budget_max"]))

    if merged.get("smoking") not in ("never", "occasionally", "regularly"):
        merged["smoking"] = base["smoking"]
    if merged.get("drinking") not in ("never", "occasionally", "regularly"):
        merged["drinking"] = base["drinking"]
    if merged.get("veg_nonveg") not in ("veg", "nonveg", "eggetarian", "vegan"):
        merged["veg_nonveg"] = base["veg_nonveg"]
    if merged.get("gender_preference") not in ("male", "female", "any"):
        merged["gender_preference"] = base["gender_preference"]
    if merged.get("preferred_move_in") not in ("immediate", "within_month", "flexible"):
        merged["preferred_move_in"] = base["preferred_move_in"]

    merged["pet_friendly"] = bool(merged.get("pet_friendly", base["pet_friendly"]))

    interests = merged.get("interests", base["interests"])
    if not isinstance(interests, list):
        interests = base["interests"]
    interests = [str(x).strip() for x in interests if str(x).strip()]
    if len(interests) < 2:
        interests = base["interests"]
    merged["interests"] = interests[:6]

    merged["email"] = generate_email(expected_name, idx)
    merged["_id"] = generate_unique_id(expected_name, idx)
    merged["avatar_url"] = None
    merged["profile_complete"] = True
    merged["is_looking"] = True

    return merged


def generate_batch(names_with_gender):
    name_list = "\n".join(
        f"  {i + 1}. {name} ({gender})"
        for i, (name, gender) in enumerate(names_with_gender)
    )

    prompt = PROMPT_TEMPLATE.format(batch=len(names_with_gender), name_list=name_list)

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
        },
    }

    try:
        response = requests.post(URL, headers=HEADERS, json=payload, timeout=90)
    except requests.exceptions.RequestException as exc:
        print(f"  Request error: {exc}")
        return None

    if response.status_code != 200:
        print(f"  API error ({response.status_code}): {response.text[:180]}")
        return None

    try:
        result = response.json()
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError, TypeError, ValueError) as exc:
        print(f"  Unexpected API response: {exc}")
        return None

    text = clean_json_text(text)

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        print(f"  JSON parse error: {exc}")
        return None

    if not isinstance(data, list):
        print("  API response parsed but not a list.")
        return None

    return data


def main():
    if not GEMINI_API_KEY:
        raise RuntimeError("GEMINI_API_KEY is missing. Set it in your environment or .env file.")

    final_users = []
    used_names = set()

    batch_num = 0
    consecutive_failures = 0

    while len(final_users) < TARGET:
        batch_num += 1
        remaining = TARGET - len(final_users)
        batch_count = min(BATCH_SIZE, remaining)

        names_with_gender = [choose_name_gender(used_names) for _ in range(batch_count)]
        print(f"[Batch {batch_num}] generating {batch_count} users ({len(final_users)}/{TARGET})")

        users = generate_batch(names_with_gender)

        if users is None:
            consecutive_failures += 1
            print(f"  Failed attempt {consecutive_failures}/{MAX_RETRIES}; retrying.")

            # Allow names to be regenerated if the call failed entirely.
            for name, _ in names_with_gender:
                if name in used_names:
                    used_names.remove(name)

            if consecutive_failures >= MAX_RETRIES:
                print("Max retries reached. Using fallback generator for this batch.")
                users = [
                    fallback_record(name, gender, len(final_users) + i + 1)
                    for i, (name, gender) in enumerate(names_with_gender)
                ]
                consecutive_failures = 0
            else:
                time.sleep(4)
                continue

        consecutive_failures = 0
        added = 0

        for i, pair in enumerate(names_with_gender):
            if i >= len(users):
                break
            expected_name, expected_gender = pair
            idx = len(final_users) + 1
            fixed = validate_and_fix_user(users[i], expected_name, expected_gender, idx)
            final_users.append(fixed)
            added += 1

        print(f"  Added {added}. Total: {len(final_users)}/{TARGET}")

        with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
            json.dump(final_users, f, indent=2)

        time.sleep(4)

    print(f"Done. Generated {len(final_users)} users to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()

import json
import hashlib
import requests
import os
import time
import random
from dotenv import load_dotenv

# ============================
# Load API Key
# ============================

load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

MODEL = "gemma-3-27b-it"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={GEMINI_API_KEY}"

headers = {
    "Content-Type": "application/json"
}

TARGET = 500
BATCH_SIZE = 5
MAX_RETRIES = 5

# ============================
# Name Generation (programmatic — guarantees uniqueness)
# ============================

MALE_FIRST = [
    "Akash", "Amit", "Anil", "Ankit", "Arun", "Ashish", "Bibhu", "Bikash", "Biswa",
    "Chandan", "Chitta", "Debashis", "Deepak", "Dhiren", "Dilip", "Dinesh", "Durga",
    "Ganesh", "Girish", "Gobinda", "Hari", "Hemant", "Jagdish", "Jatin", "Jayant",
    "Kailash", "Kamal", "Kiran", "Kishore", "Krishna", "Kumar", "Laxman", "Manas",
    "Manoj", "Milan", "Mohan", "Mukesh", "Nandan", "Naresh", "Narayan", "Nikhil",
    "Niranjan", "Omkar", "Pankaj", "Paresh", "Prakash", "Pramod", "Pranav", "Prasad",
    "Prateek", "Praveen", "Purna", "Rabindra", "Rajat", "Rajesh", "Rakesh", "Ranjan",
    "Ravi", "Rohit", "Roshan", "Sachin", "Sagar", "Sandeep", "Sanjay", "Santosh",
    "Saroj", "Satya", "Shashank", "Shiva", "Siddharth", "Soumya", "Subash", "Sudhir",
    "Sunil", "Surya", "Sushant", "Tarun", "Tushar", "Umesh", "Utkal", "Varun",
    "Vijay", "Vikash", "Vinod", "Yash", "Yogesh", "Abhinav", "Ajit", "Alok",
    "Bhabani", "Bhagat", "Bipin", "Braja", "Chandra", "Deba", "Gagan", "Gopal",
    "Haris", "Iswar", "Jagat", "Jyoti", "Lingaraj", "Loknath", "Madhab", "Manoranjan",
    "Nigam", "Pabitra", "Pitambar", "Priyaranjan", "Purnendu", "Ramesh", "Sabyasachi",
    "Sambit", "Sanat", "Sasanka", "Sibaram", "Smruti", "Soumendra", "Sudam", "Tapan",
    "Trinath", "Uday", "Basant", "Dharma", "Hrushikesh", "Jitendra", "Khirod",
    "Laxmidhar", "Minaketan", "Naba", "Prafulla", "Rasmi", "Sarat", "Tarini",
]

FEMALE_FIRST = [
    "Aditi", "Anjali", "Anita", "Ankita", "Anuradha", "Archana", "Barsha", "Bharati",
    "Bina", "Chandni", "Deepa", "Deepthi", "Devika", "Dimple", "Dipti", "Gargi",
    "Gayatri", "Gita", "Ila", "Isha", "Itishree", "Jasmine", "Jyoti", "Kabita",
    "Kalpana", "Kamala", "Kavita", "Kiran", "Kumari", "Lata", "Laxmi", "Lipika",
    "Lopamudra", "Madhusmita", "Mamata", "Manaswini", "Manisha", "Meena", "Mita",
    "Monalisa", "Mousumi", "Namrata", "Nandini", "Neha", "Nibedita", "Nirupama",
    "Pallavi", "Paramita", "Prabha", "Pragnya", "Pranjali", "Pratibha", "Preeti",
    "Priya", "Puja", "Pushpa", "Rachana", "Radha", "Rajani", "Ranjita", "Rashmi",
    "Reema", "Ritu", "Rojalin", "Sabita", "Sakshi", "Sangita", "Sanjukta", "Sarita",
    "Shanti", "Shibani", "Shilpa", "Shruti", "Silu", "Sima", "Smita", "Sneha",
    "Sonia", "Subhadra", "Suchitra", "Sudha", "Sulochana", "Sunita", "Supriya",
    "Swati", "Tanuja", "Trupti", "Uma", "Urmila", "Varsha", "Vidya", "Yamini",
    "Abhilipsa", "Bhagyalaxmi", "Bijayini", "Debaki", "Hiranmayee", "Jhili",
    "Jyotsna", "Lily", "Minati", "Niharika", "Padmini", "Puspanjali", "Sagarika",
    "Sefali", "Sonali", "Subhashree", "Sucharita", "Tara", "Usharani",
]

LAST_NAMES = [
    "Behera", "Das", "Mishra", "Mohanty", "Nayak", "Panda", "Patel", "Pradhan",
    "Rout", "Sahu", "Sahoo", "Sethi", "Swain", "Tripathy", "Barik", "Biswal",
    "Dalai", "Dash", "Jena", "Khuntia", "Lenka", "Mahapatra", "Malik", "Meher",
    "Muduli", "Naik", "Parida", "Patra", "Samantaray", "Senapati", "Singh",
    "Acharya", "Bal", "Bastia", "Bhoi", "Chand", "Dehury", "Deo", "Dhal", "Garnayak",
    "Giri", "Hota", "Kar", "Khatua", "Maharana", "Majhi", "Mohapatra", "Palai",
    "Rath", "Ray", "Sagar", "Satpathy", "Sutar", "Tandi", "Bag", "Bhol",
    "Bibhar", "Digal", "Ghadei", "Guru", "Hansda", "Ho", "Kisan", "Lakra",
    "Marndi", "Munda", "Nag", "Oram", "Pani", "Pattnaik", "Purohit", "Samal",
    "Sandha", "Soren", "Tudu", "Xess",
]

ODISHA_DISTRICTS = {
    "Khordha":     (85.83, 20.18),
    "Cuttack":     (85.88, 20.46),
    "Puri":        (85.83, 19.81),
    "Ganjam":      (84.68, 19.59),
    "Sambalpur":   (83.97, 21.47),
    "Balasore":    (86.93, 21.49),
    "Sundargarh":  (84.04, 22.12),
    "Mayurbhanj":  (86.34, 21.94),
    "Koraput":     (82.71, 18.81),
    "Jajpur":      (86.33, 20.85),
    "Kendrapara":  (86.42, 20.50),
    "Boudh":       (84.32, 20.84),
    "Angul":       (85.10, 20.84),
    "Dhenkanal":   (85.60, 20.67),
    "Nayagarh":    (85.10, 20.13),
    "Kalahandi":   (83.17, 19.91),
    "Rayagada":    (83.42, 19.17),
    "Bargarh":     (83.62, 21.33),
    "Jharsuguda":  (84.01, 21.86),
    "Bhadrak":     (86.52, 21.05),
    "Bolangir":    (83.49, 20.70),
    "Deogarh":     (84.73, 21.54),
    "Gajapati":    (84.13, 19.22),
    "Jagatsinghpur": (86.17, 20.26),
    "Kandhamal":   (84.07, 20.30),
    "Keonjhar":    (85.58, 21.63),
    "Malkangiri":  (81.88, 18.35),
    "Nabarangpur": (82.55, 19.23),
    "Nuapada":     (82.55, 20.80),
    "Subarnapur":  (83.87, 20.83),
}

def generate_unique_names(count, used_names):
    """Generate guaranteed-unique full names programmatically."""
    names = []
    attempts = 0
    max_attempts = count * 20

    while len(names) < count and attempts < max_attempts:
        attempts += 1
        is_female = random.random() < 0.5
        first = random.choice(FEMALE_FIRST if is_female else MALE_FIRST)
        last = random.choice(LAST_NAMES)
        full_name = f"{first} {last}"

        if full_name not in used_names:
            used_names.add(full_name)
            names.append((full_name, "Female" if is_female else "Male"))

    return names

# ============================
# Prompt — names are pre-assigned, model fills in the rest
# ============================

prompt_template = """
You are generating structured synthetic dataset entries for people from Odisha, India.

Task: Generate profiles for these {batch} people. Use EXACTLY these names and genders:
{name_list}

Output Requirements:
- Output ONLY a valid JSON array.
- Do NOT include markdown, backticks, explanations, or comments.
- The output must be parseable by json.loads().
- No trailing commas. No text before or after the JSON array.

Each element must strictly follow this schema:

[
  {{
        "full_name": "<use the assigned name>",
        "age": <integer 18-28>,
        "gender": "<male or female exactly>",
        "occupation": "<student or working_professional or freelancer>",
        "phone": "<10-digit Indian mobile number as string>",
        "bio": "<short 1-sentence personality description>",
        "city": "<real Odisha city>",
        "locality": "<real Odisha district/locality>",
        "latitude": <float latitude>,
        "longitude": <float longitude>,
        "sleep_schedule": <integer 1-5>,
        "cleanliness": <integer 1-5>,
        "noise_tolerance": <integer 1-5>,
        "cooking_frequency": <integer 1-5>,
        "guest_frequency": <integer 1-5>,
        "workout_habit": <integer 1-5>,
        "introversion_extroversion": <integer 1-5>,
        "communication_style": <integer 1-5>,
        "conflict_resolution": <integer 1-5>,
        "social_battery": <integer 1-5>,
        "budget_min": <integer 3000-12000>,
        "budget_max": <integer 5000-20000 and >= budget_min>,
        "smoking": "<never or occasionally or regularly>",
        "drinking": "<never or occasionally or regularly>",
        "veg_nonveg": "<veg or nonveg or eggetarian or vegan>",
        "gender_preference": "<male or female or any>",
        "pet_friendly": <true or false>,
        "preferred_move_in": "<immediate or within_month or flexible>",
        "interests": ["<2-6 short interests strings>"],
        "avatar_url": null,
        "profile_complete": true,
        "is_looking": true
  }}
]

Constraints:
- Use real Odisha district names and realistic coordinates for those districts.
- Vary personalities, budgets, locations, and preferences realistically.
- Return ONLY the JSON array, nothing else.
"""

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

    if start != -1 and end != -1:
        text = text[start:end+1]

    return text.strip()

def generate_batch(names_with_gender):
    name_list = "\n".join(
        f"  {i+1}. {name} ({gender})"
        for i, (name, gender) in enumerate(names_with_gender)
    )

    prompt = prompt_template.format(
        batch=len(names_with_gender),
        name_list=name_list,
    )

    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.7,
            "topP": 0.9,
        }
    }

    try:
        response = requests.post(URL, headers=headers, json=payload, timeout=60)
    except requests.exceptions.RequestException as e:
        print(f"  Request Error: {e}")
        return None

    if response.status_code != 200:
        print(f"  API Error ({response.status_code}): {response.text[:200]}")
        return None

    result = response.json()

    try:
        text = result["candidates"][0]["content"]["parts"][0]["text"]
    except (KeyError, IndexError) as e:
        print(f"  Unexpected API response: {e}")
        return None

    text = clean_json_text(text)

    try:
        data = json.loads(text)
        if not isinstance(data, list):
            print("  API returned valid JSON but not a list.")
            return None
        return data
    except json.JSONDecodeError as e:
        print(f"  JSON Parse Error: {e}")
        print(f"  Raw (first 300 chars): {text[:300]}")
        return None

def validate_and_fix_user(user, expected_name, expected_gender):
    """Ensure generated user follows frontend-compatible flat schema."""
    try:
        user = user if isinstance(user, dict) else {}
        user["full_name"] = expected_name
        user["gender"] = expected_gender.lower()

        age = user.get("age", random.randint(18, 28))
        user["age"] = max(18, min(28, int(age)))

        locality = user.get("locality")
        if locality not in ODISHA_DISTRICTS:
            locality = random.choice(list(ODISHA_DISTRICTS.keys()))
        base_lon, base_lat = ODISHA_DISTRICTS[locality]
        lon = user.get("longitude", round(base_lon + random.uniform(-0.15, 0.15), 6))
        lat = user.get("latitude", round(base_lat + random.uniform(-0.15, 0.15), 6))

        user["city"] = str(user.get("city") or "Bhubaneswar").strip()
        user["locality"] = locality
        user["longitude"] = round(float(lon), 6)
        user["latitude"] = round(float(lat), 6)

        user["occupation"] = user.get("occupation") if user.get("occupation") in ("student", "working_professional", "freelancer") else random.choice(["student", "working_professional", "freelancer"])
        user["phone"] = str(user.get("phone") or f"9{random.randint(100000000, 999999999)}")
        user["bio"] = str(user.get("bio") or "Friendly and responsible roommate looking for a good shared space.").strip()

        for key in (
            "sleep_schedule", "cleanliness", "noise_tolerance", "cooking_frequency", "guest_frequency",
            "workout_habit", "introversion_extroversion", "communication_style", "conflict_resolution", "social_battery"
        ):
            user[key] = max(1, min(5, int(user.get(key, random.randint(1, 5)))))

        min_budget = int(user.get("budget_min", random.randint(3500, 12000)))
        max_budget = int(user.get("budget_max", min_budget + random.randint(1000, 6000)))
        min_budget = max(3000, min(min_budget, 20000))
        max_budget = max(min_budget, min(max_budget, 25000))
        user["budget_min"] = min_budget
        user["budget_max"] = max_budget

        user["smoking"] = user.get("smoking") if user.get("smoking") in ("never", "occasionally", "regularly") else random.choice(["never", "occasionally", "regularly"])
        user["drinking"] = user.get("drinking") if user.get("drinking") in ("never", "occasionally", "regularly") else random.choice(["never", "occasionally", "regularly"])
        user["veg_nonveg"] = user.get("veg_nonveg") if user.get("veg_nonveg") in ("veg", "nonveg", "eggetarian", "vegan") else random.choice(["veg", "nonveg", "eggetarian", "vegan"])
        user["gender_preference"] = user.get("gender_preference") if user.get("gender_preference") in ("male", "female", "any") else random.choice(["male", "female", "any"])
        user["pet_friendly"] = bool(user.get("pet_friendly", random.choice([True, False])))
        user["preferred_move_in"] = user.get("preferred_move_in") if user.get("preferred_move_in") in ("immediate", "within_month", "flexible") else random.choice(["immediate", "within_month", "flexible"])

        interests = user.get("interests", [])
        if not isinstance(interests, list):
            interests = []
        if not interests:
            pool = ["Reading", "Music", "Gaming", "Cooking", "Fitness", "Movies", "Travel", "Photography", "Cricket", "Coding"]
            interests = random.sample(pool, k=random.randint(3, 5))
        user["interests"] = [str(i).strip() for i in interests if str(i).strip()][:6]

        user["avatar_url"] = None
        user["profile_complete"] = True
        user["is_looking"] = True

        # Deterministic synthetic email from name
        slug = "".join(c.lower() for c in expected_name if c.isalnum())
        user["email"] = user.get("email") or f"{slug[:18]}@synthetic.local"

        return user
    except Exception:
        return None

# ============================
# Resume from existing data
# ============================

final_users = []
existing_ids = set()
existing_names = set()

if os.path.exists("odisha_users.json"):
    try:
        with open("odisha_users.json", "r") as f:
            final_users = json.load(f)
        for user in final_users:
            if "_id" in user:
                existing_ids.add(user["_id"])
            if isinstance(user, dict):
                if "full_name" in user:
                    existing_names.add(user["full_name"])
                elif "profile" in user and isinstance(user["profile"], dict) and user["profile"].get("name"):
                    existing_names.add(user["profile"]["name"])
        print(f"Resumed with {len(final_users)} existing users.")
    except Exception as e:
        print(f"Could not resume: {e}. Starting fresh.")
        final_users = []

# ============================
# Main Loop
# ============================

batch_num = 0
consecutive_failures = 0

while len(final_users) < TARGET:
    batch_num += 1
    remaining = TARGET - len(final_users)
    batch_count = min(BATCH_SIZE, remaining)

    # Generate unique names for this batch
    names_with_gender = generate_unique_names(batch_count, existing_names)
    if not names_with_gender:
        print("Could not generate more unique names. Stopping.")
        break

    print(f"[Batch {batch_num}] Generating {len(names_with_gender)} users (have {len(final_users)}/{TARGET})")

    users = generate_batch(names_with_gender)

    if users is None:
        consecutive_failures += 1
        # Return names to pool so they can be reused on retry
        for name, _ in names_with_gender:
            existing_names.discard(name)
        print(f"  Failed (attempt {consecutive_failures}/{MAX_RETRIES}). Retrying...")
        if consecutive_failures >= MAX_RETRIES:
            print(f"Too many consecutive failures. Stopping with {len(final_users)} users.")
            break
        time.sleep(4)
        continue

    consecutive_failures = 0
    added = 0

    for i, user in enumerate(users):
        if i >= len(names_with_gender):
            break
        expected_name, expected_gender = names_with_gender[i]

        user = validate_and_fix_user(user, expected_name, expected_gender)
        if user is None:
            continue

        sha1_id = hashlib.sha1(expected_name.encode()).hexdigest()
        if sha1_id in existing_ids:
            continue

        user["_id"] = sha1_id
        existing_ids.add(sha1_id)
        final_users.append(user)
        added += 1

    print(f"  +{added} new. Total: {len(final_users)}/{TARGET}")

    # Save progressively
    with open("odisha_users.json", "w") as f:
        json.dump(final_users, f, indent=2)

    # Stay under 30 RPM (Gemma limit) — 4s gap = ~15 RPM
    time.sleep(4)

print(f"Done! {len(final_users)} users saved to odisha_users.json.")
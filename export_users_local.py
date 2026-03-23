import argparse
import json
import os
from pathlib import Path
from datetime import datetime, date

from dotenv import load_dotenv
from pymongo import MongoClient

# Rough Odisha bounding box
ODISHA_LAT_MIN = 17.5
ODISHA_LAT_MAX = 22.8
ODISHA_LNG_MIN = 81.4
ODISHA_LNG_MAX = 87.6

# Fallback location inside Odisha
FALLBACK_CITY = "Bhubaneswar"
FALLBACK_LOCALITY = "Patia"
FALLBACK_LAT = 20.2961
FALLBACK_LNG = 85.8245


def is_number(value):
    return isinstance(value, (int, float))


def in_odisha(lat, lng):
    if not (is_number(lat) and is_number(lng)):
        return False
    return ODISHA_LAT_MIN <= float(lat) <= ODISHA_LAT_MAX and ODISHA_LNG_MIN <= float(lng) <= ODISHA_LNG_MAX


def pick_odisha_preferred_location(doc):
    pref_lat = doc.get("latitude")
    pref_lng = doc.get("longitude")
    pref_city = doc.get("city")
    pref_locality = doc.get("locality")

    home_lat = doc.get("home_latitude")
    home_lng = doc.get("home_longitude")
    home_city = doc.get("home_city")
    home_locality = doc.get("home_locality")

    # Priority 1: existing preferred location if already in Odisha
    if in_odisha(pref_lat, pref_lng):
        return {
            "latitude": float(pref_lat),
            "longitude": float(pref_lng),
            "city": pref_city or FALLBACK_CITY,
            "locality": pref_locality or FALLBACK_LOCALITY,
            "source": "preferred",
        }

    # Priority 2: use home location if it's in Odisha
    if in_odisha(home_lat, home_lng):
        return {
            "latitude": float(home_lat),
            "longitude": float(home_lng),
            "city": home_city or pref_city or FALLBACK_CITY,
            "locality": home_locality or pref_locality or FALLBACK_LOCALITY,
            "source": "home_promoted",
        }

    # Priority 3: fallback to Bhubaneswar
    return {
        "latitude": FALLBACK_LAT,
        "longitude": FALLBACK_LNG,
        "city": FALLBACK_CITY,
        "locality": FALLBACK_LOCALITY,
        "source": "fallback",
    }


def sanitize_user(doc):
    user = {}
    for k, v in dict(doc).items():
        if isinstance(v, (datetime, date)):
            user[k] = v.isoformat()
        elif isinstance(v, bytes):
            user[k] = v.decode("utf-8", errors="ignore")
        else:
            user[k] = v
    user["_id"] = str(user.get("_id"))

    location = pick_odisha_preferred_location(user)
    user["latitude"] = location["latitude"]
    user["longitude"] = location["longitude"]
    user["city"] = location["city"]
    user["locality"] = location["locality"]
    user["preferred_location_source"] = location["source"]

    # Remove home location fields entirely for local testing data
    for key in ("home_city", "home_locality", "home_latitude", "home_longitude"):
        user.pop(key, None)

    return user


def parse_args():
    parser = argparse.ArgumentParser(
        description="Export users from MongoDB to local JSON, enforcing Odisha preferred location and removing home location fields."
    )
    parser.add_argument(
        "--output",
        default="local_data/users_local.json",
        help="Local output path for exported users JSON.",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MONGO_DB_NAME", "cohabitai"),
        help="Mongo database name (default: MONGO_DB_NAME or cohabitai).",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("MONGO_COLLECTION_NAME", "users"),
        help="Mongo collection name (default: MONGO_COLLECTION_NAME or users).",
    )
    parser.add_argument(
        "--check-email",
        default="sar656hal@gmail.com",
        help="Email to print verification details for.",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    mongo_uri = os.getenv("MONGO_CONNECTION_STRING") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("Missing MONGO_CONNECTION_STRING or MONGODB_URI in environment/.env")

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")

    db = client[args.db]
    users_col = db[args.collection]

    docs = list(users_col.find({}))
    cleaned = [sanitize_user(d) for d in docs]

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(cleaned, f, ensure_ascii=False, indent=2)

    promoted_from_home = sum(1 for u in cleaned if u.get("preferred_location_source") == "home_promoted")
    fallback_count = sum(1 for u in cleaned if u.get("preferred_location_source") == "fallback")

    print(f"Exported users: {len(cleaned)}")
    print(f"Promoted home->preferred (Odisha): {promoted_from_home}")
    print(f"Fallback to Bhubaneswar: {fallback_count}")
    print(f"Saved file: {output_path}")

    target = next((u for u in cleaned if (u.get("email") or "").lower() == args.check_email.lower()), None)
    if target:
        print("--- Verified user ---")
        print(f"email: {target.get('email')}")
        print(f"city/locality: {target.get('city')} / {target.get('locality')}")
        print(f"lat/lng: {target.get('latitude')}, {target.get('longitude')}")
        print(f"in_odisha: {in_odisha(target.get('latitude'), target.get('longitude'))}")
    else:
        print(f"User not found for email: {args.check_email}")


if __name__ == "__main__":
    main()

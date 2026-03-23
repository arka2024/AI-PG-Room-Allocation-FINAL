import argparse
import json
import random
from pathlib import Path

# Odisha PG hubs with consistent city/locality + center coordinates
ODISHA_HUBS = [
    {"city": "Bhubaneswar", "locality": "Patia", "lat": 20.3550, "lng": 85.8190},
    {"city": "Cuttack", "locality": "Badambadi", "lat": 20.4625, "lng": 85.8830},
    {"city": "Puri", "locality": "Grand Road", "lat": 19.8070, "lng": 85.8270},
    {"city": "Rourkela", "locality": "Udit Nagar", "lat": 22.2600, "lng": 84.8530},
    {"city": "Sambalpur", "locality": "Ainthapali", "lat": 21.4700, "lng": 83.9800},
    {"city": "Balasore", "locality": "FM Circle", "lat": 21.4942, "lng": 86.9335},
    {"city": "Berhampur", "locality": "Bhanjanagar Road", "lat": 19.3149, "lng": 84.7941},
    {"city": "Jharsuguda", "locality": "Beheramal", "lat": 21.8550, "lng": 84.0060},
    {"city": "Angul", "locality": "Amalapada", "lat": 20.8440, "lng": 85.1510},
    {"city": "Baripada", "locality": "Bhanjpur", "lat": 21.9374, "lng": 86.7250},
    {"city": "Jajpur", "locality": "Jajpur Road", "lat": 20.8500, "lng": 86.3330},
    {"city": "Dhenkanal", "locality": "Town", "lat": 20.6570, "lng": 85.5960},
    {"city": "Keonjhar", "locality": "Mining Road", "lat": 21.6290, "lng": 85.5820},
    {"city": "Koraput", "locality": "Semiliguda Road", "lat": 18.8135, "lng": 82.7123},
    {"city": "Rayagada", "locality": "New Colony", "lat": 19.1710, "lng": 83.4160},
]


def parse_args():
    parser = argparse.ArgumentParser(
        description="Evenly redistribute preferred PG locations across Odisha with consistent city/locality pairs."
    )
    parser.add_argument(
        "--input",
        default="local_data/users_local.json",
        help="Input JSON file path.",
    )
    parser.add_argument(
        "--output",
        default="local_data/users_local_balanced.json",
        help="Output JSON file path.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for stable redistribution.",
    )
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="Overwrite input file directly.",
    )
    parser.add_argument(
        "--restore-home",
        action="store_true",
        help="Also create home_* fields by mirroring preferred location (testing convenience).",
    )
    return parser.parse_args()


def jitter(val, spread=0.045):
    return round(val + random.uniform(-spread, spread), 6)


def even_assignments(count, buckets):
    indices = list(range(count))
    random.shuffle(indices)

    k = len(buckets)
    base = count // k
    rem = count % k

    plan = []
    for i in range(k):
        n = base + (1 if i < rem else 0)
        plan.extend([i] * n)

    random.shuffle(plan)

    out = [0] * count
    for idx, bucket_id in zip(indices, plan):
        out[idx] = bucket_id
    return out


def rebalance(users, restore_home=False):
    assignments = even_assignments(len(users), ODISHA_HUBS)

    for i, user in enumerate(users):
        hub = ODISHA_HUBS[assignments[i]]

        user["city"] = hub["city"]
        user["locality"] = hub["locality"]
        user["latitude"] = jitter(hub["lat"])
        user["longitude"] = jitter(hub["lng"])
        user["preferred_location_source"] = "balanced_odisha"

        if restore_home:
            user["home_city"] = hub["city"]
            user["home_locality"] = hub["locality"]
            user["home_latitude"] = user["latitude"]
            user["home_longitude"] = user["longitude"]

    return users


def summarize(users):
    counts = {}
    for u in users:
        key = (u.get("city"), u.get("locality"))
        counts[key] = counts.get(key, 0) + 1

    print("Distribution by city/locality:")
    for (city, locality), n in sorted(counts.items(), key=lambda x: (x[0][0] or "", x[0][1] or "")):
        print(f"- {city} / {locality}: {n}")


def main():
    args = parse_args()
    random.seed(args.seed)

    input_path = Path(args.input)
    if not input_path.exists():
        raise FileNotFoundError(f"Input file not found: {input_path}")

    users = json.loads(input_path.read_text(encoding="utf-8"))
    if not isinstance(users, list):
        raise ValueError("Input JSON must be an array of users.")

    users = rebalance(users, restore_home=args.restore_home)

    output_path = input_path if args.in_place else Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(users, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Users processed: {len(users)}")
    print(f"Output file: {output_path}")
    summarize(users)


if __name__ == "__main__":
    main()

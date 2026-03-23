import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient, ReplaceOne


def load_dataset(dataset_path: Path):
    if not dataset_path.exists():
        raise FileNotFoundError(f"Dataset file not found: {dataset_path}")

    with dataset_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Dataset must be a JSON array of user objects.")

    return data


def sanitize_document(doc):
    out = dict(doc)
    # Ensure _id is available and stable for upserts.
    if "_id" not in out or out["_id"] in (None, ""):
        # Fallback deterministic key if needed.
        key_seed = f"{out.get('full_name', 'unknown')}|{out.get('email', '')}"
        out["_id"] = key_seed.lower().replace(" ", "_")
    out["_id"] = str(out["_id"])
    return out


def parse_args():
    parser = argparse.ArgumentParser(description="Push synthetic users JSON to MongoDB.")
    parser.add_argument(
        "--dataset",
        default="Ideas and Dataset Synthesis/odisha_users.json",
        help="Path to dataset JSON file.",
    )
    parser.add_argument(
        "--db",
        default=os.getenv("MONGO_DB_NAME", "cohabitai"),
        help="MongoDB database name (default: MONGO_DB_NAME or cohabitai).",
    )
    parser.add_argument(
        "--collection",
        default=os.getenv("MONGO_COLLECTION_NAME", "users"),
        help="MongoDB collection name (default: MONGO_COLLECTION_NAME or users).",
    )
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop target collection before import.",
    )
    return parser.parse_args()


def main():
    load_dotenv()
    args = parse_args()

    mongo_uri = os.getenv("MONGO_CONNECTION_STRING") or os.getenv("MONGODB_URI")
    if not mongo_uri:
        raise RuntimeError("Missing MONGO_CONNECTION_STRING or MONGODB_URI in environment/.env")

    dataset_path = Path(args.dataset)
    data = load_dataset(dataset_path)

    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=15000)
    client.admin.command("ping")

    db = client[args.db]
    collection = db[args.collection]

    if args.drop:
        collection.drop()

    operations = []
    for doc in data:
        clean_doc = sanitize_document(doc)
        operations.append(ReplaceOne({"_id": clean_doc["_id"]}, clean_doc, upsert=True))

    if not operations:
        print("No documents to import.")
        return

    result = collection.bulk_write(operations, ordered=False)

    # Useful indexes for search/matching patterns.
    collection.create_index("email", unique=False, sparse=True)
    collection.create_index("city")
    collection.create_index("locality")
    collection.create_index("occupation")
    collection.create_index("gender")
    collection.create_index("is_looking")

    print(f"Imported documents: {len(operations)}")
    print(f"Upserts: {result.upserted_count}")
    print(f"Modified: {result.modified_count}")
    print(f"Target: {args.db}.{args.collection}")


if __name__ == "__main__":
    main()

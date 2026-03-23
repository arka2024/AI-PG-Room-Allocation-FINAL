"""
CohabitAI - Main Flask Application
MongoDB-backed roommate matching platform.
"""

import os
import uuid
from datetime import datetime

from dotenv import load_dotenv
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
from pymongo import MongoClient
from pymongo.errors import OperationFailure
from werkzeug.security import check_password_hash, generate_password_hash

from chatbot import generate_conflict_prompts, generate_response
from compatibility import (
    check_hard_constraints,
    compute_compatibility,
    compute_feature_differential,
    get_top_overlaps_and_conflicts,
    haversine_distance,
    rank_users_by_compatibility,
)


load_dotenv()


class MongoUser(UserMixin):
    def __init__(self, doc):
        self._doc = dict(doc)
        self.id = str(self._doc.get("_id"))
        self.email = self._doc.get("email", "")
        self.password_hash = self._doc.get("password_hash", "")
        self.full_name = self._doc.get("full_name", "")
        self.age = self._doc.get("age", 25)
        self.gender = self._doc.get("gender", "male")
        self.occupation = self._doc.get("occupation", "student")
        self.phone = self._doc.get("phone")
        self.bio = self._doc.get("bio")
        self.avatar_url = self._doc.get("avatar_url")
        self.latitude = self._doc.get("latitude")
        self.longitude = self._doc.get("longitude")
        self.city = self._doc.get("city")
        self.locality = self._doc.get("locality")
        self.home_city = self._doc.get("home_city")
        self.home_locality = self._doc.get("home_locality")
        self.home_latitude = self._doc.get("home_latitude")
        self.home_longitude = self._doc.get("home_longitude")
        self.sleep_schedule = self._doc.get("sleep_schedule", 3)
        self.cleanliness = self._doc.get("cleanliness", 3)
        self.noise_tolerance = self._doc.get("noise_tolerance", 3)
        self.cooking_frequency = self._doc.get("cooking_frequency", 3)
        self.guest_frequency = self._doc.get("guest_frequency", 3)
        self.workout_habit = self._doc.get("workout_habit", 3)
        self.introversion_extroversion = self._doc.get("introversion_extroversion", 3)
        self.communication_style = self._doc.get("communication_style", 3)
        self.conflict_resolution = self._doc.get("conflict_resolution", 3)
        self.social_battery = self._doc.get("social_battery", 3)
        self.budget_min = self._doc.get("budget_min")
        self.budget_max = self._doc.get("budget_max")
        self.smoking = self._doc.get("smoking", "never")
        self.drinking = self._doc.get("drinking", "never")
        self.pet_friendly = bool(self._doc.get("pet_friendly", False))
        self.veg_nonveg = self._doc.get("veg_nonveg", "nonveg")
        self.gender_preference = self._doc.get("gender_preference", "any")
        self.preferred_move_in = self._doc.get("preferred_move_in", "flexible")
        self.is_looking = bool(self._doc.get("is_looking", True))
        self.profile_complete = bool(self._doc.get("profile_complete", False))

    def __getitem__(self, key):
        return getattr(self, key)

    def get_feature_vector(self):
        return {
            "sleep_schedule": self.sleep_schedule or 3,
            "cleanliness": self.cleanliness or 3,
            "noise_tolerance": self.noise_tolerance or 3,
            "cooking_frequency": self.cooking_frequency or 3,
            "guest_frequency": self.guest_frequency or 3,
            "workout_habit": self.workout_habit or 3,
            "introversion_extroversion": self.introversion_extroversion or 3,
            "communication_style": self.communication_style or 3,
            "conflict_resolution": self.conflict_resolution or 3,
            "social_battery": self.social_battery or 3,
        }

    def get_interests_list(self):
        interests = self._doc.get("interests")
        if isinstance(interests, list):
            return interests
        return []

    def set_interests_list(self, lst):
        self._doc["interests"] = lst


class MongoChatMessage:
    def __init__(self, doc):
        self._doc = dict(doc)
        self.user_id = str(self._doc.get("user_id"))
        self.role = self._doc.get("role", "user")
        self.message = self._doc.get("message", "")
        self.created_at = self._doc.get("created_at") or datetime.utcnow()


# App configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "cohabitai-secret-key-2026"

mongo_uri = os.getenv("MONGO_CONNECTION_STRING") or os.getenv("MONGODB_URI")
if not mongo_uri:
    raise RuntimeError("Missing MONGO_CONNECTION_STRING or MONGODB_URI in .env")

mongo_db_name = os.getenv("MONGO_DB_NAME", "cohabitai")
mongo_client = MongoClient(mongo_uri)
mongo_db = mongo_client[mongo_db_name]
users_col = mongo_db[os.getenv("MONGO_COLLECTION_NAME", "users")]
chat_col = mongo_db["chat_messages"]


def _safe_create_index(collection, keys, **kwargs):
    try:
        collection.create_index(keys, **kwargs)
    except OperationFailure:
        # Keep app startup resilient if index with same name/key exists but options differ.
        pass


# Indexes for fast login and filtering.
_safe_create_index(users_col, "email", unique=True, sparse=True)
_safe_create_index(users_col, "is_looking")
_safe_create_index(users_col, "city")
_safe_create_index(users_col, "locality")
_safe_create_index(chat_col, [("user_id", 1), ("created_at", 1)])

login_manager = LoginManager(app)
login_manager.login_view = "login"
login_manager.login_message_category = "info"


def _as_int(value, default=0):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _as_float(value, default=None):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _to_user(doc):
    if not doc:
        return None
    return MongoUser(doc)


def get_user_by_id(user_id):
    return _to_user(users_col.find_one({"_id": str(user_id)}))


def get_user_by_email(email):
    return _to_user(users_col.find_one({"email": email}))


def get_all_active_users(exclude_user_id=None):
    query = {
        "is_looking": True,
        "$nor": [
            {"full_name": "Test User"},
            {"email": {"$regex": r"^test_.*@example\.com$"}},
        ],
    }
    docs = list(users_col.find(query))
    users = [_to_user(d) for d in docs]
    if exclude_user_id is not None:
        users = [u for u in users if u and str(u.id) != str(exclude_user_id)]
    return [u for u in users if u]


def discover_candidates_by_location(query_user, users, radius_km=20.0):
    """Geospatial-first discovery based on preferred PG location only."""
    origin_lat, origin_lng = query_user.latitude, query_user.longitude

    if origin_lat is None or origin_lng is None:
        return []

    discovered = []
    for user in users:
        target_lat, target_lng = user.latitude, user.longitude

        if target_lat is None or target_lng is None:
            continue

        dist = haversine_distance(origin_lat, origin_lng, target_lat, target_lng)
        if radius_km is not None and dist > radius_km:
            continue

        discovered.append({
            "user": user,
            "distance_km": round(dist, 1),
        })

    discovered.sort(key=lambda x: x["distance_km"])
    return discovered


def upsert_user_profile(user_id, payload):
    users_col.update_one({"_id": str(user_id)}, {"$set": payload}, upsert=False)
    return get_user_by_id(user_id)


def create_user_from_form(form):
    user_id = uuid.uuid4().hex
    interests_raw = form.get("interests", "")
    interests = [i.strip() for i in interests_raw.split(",") if i.strip()] if interests_raw else []

    user_doc = {
        "_id": user_id,
        "email": form.get("email", "").strip(),
        "password_hash": generate_password_hash(form.get("password", "")),
        "full_name": form.get("full_name", "").strip(),
        "age": _as_int(form.get("age"), 25),
        "gender": form.get("gender", "male"),
        "occupation": form.get("occupation", "student"),
        "phone": form.get("phone", ""),
        "bio": form.get("bio", ""),
        "city": form.get("city", ""),
        "locality": form.get("locality", ""),
        "home_city": form.get("home_city", ""),
        "home_locality": form.get("home_locality", ""),
        "latitude": _as_float(form.get("latitude")),
        "longitude": _as_float(form.get("longitude")),
        "home_latitude": _as_float(form.get("home_latitude")),
        "home_longitude": _as_float(form.get("home_longitude")),
        "sleep_schedule": _as_int(form.get("sleep_schedule"), 3),
        "cleanliness": _as_int(form.get("cleanliness"), 3),
        "noise_tolerance": _as_int(form.get("noise_tolerance"), 3),
        "cooking_frequency": _as_int(form.get("cooking_frequency"), 3),
        "guest_frequency": _as_int(form.get("guest_frequency"), 3),
        "workout_habit": _as_int(form.get("workout_habit"), 3),
        "introversion_extroversion": _as_int(form.get("introversion_extroversion"), 3),
        "communication_style": _as_int(form.get("communication_style"), 3),
        "conflict_resolution": _as_int(form.get("conflict_resolution"), 3),
        "social_battery": _as_int(form.get("social_battery"), 3),
        "budget_min": _as_int(form.get("budget_min"), 0) or None,
        "budget_max": _as_int(form.get("budget_max"), 0) or None,
        "smoking": form.get("smoking", "never"),
        "drinking": form.get("drinking", "never"),
        "pet_friendly": bool(form.get("pet_friendly")),
        "veg_nonveg": form.get("veg_nonveg", "nonveg"),
        "gender_preference": form.get("gender_preference", "any"),
        "preferred_move_in": form.get("preferred_move_in", "flexible"),
        "interests": interests,
        "avatar_url": None,
        "profile_complete": True,
        "is_looking": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "source": "app_signup",
    }
    users_col.insert_one(user_doc)
    return get_user_by_id(user_id)


def get_chat_history(user_id, limit=50):
    docs = list(chat_col.find({"user_id": str(user_id)}).sort("created_at", 1).limit(limit))
    return [MongoChatMessage(d) for d in docs]


@login_manager.user_loader
def load_user(user_id):
    return get_user_by_id(user_id)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/architecture")
def architecture():
    return render_template("architecture.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect(url_for("register"))

        if get_user_by_email(email):
            flash("Email already registered. Please login.", "error")
            return redirect(url_for("register"))

        user = create_user_from_form(request.form)
        login_user(user)
        flash("Profile created successfully! Welcome to CohabitAI.", "success")
        return redirect(url_for("dashboard"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        user = get_user_by_email(email)

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f"Welcome back, {user.full_name.split()[0]}!", "success")
            return redirect(url_for("dashboard"))
        flash("Invalid email or password.", "error")

    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.", "info")
    return redirect(url_for("index"))


@app.route("/dashboard")
@login_required
def dashboard():
    all_users = get_all_active_users(exclude_user_id=current_user.id)
    # Keep dashboard focused on practical nearby options by default.
    top_matches = rank_users_by_compatibility(current_user, all_users, radius_km=80)

    nearby_count = 0
    if current_user.latitude and current_user.longitude:
        for u in all_users:
            if u.latitude and u.longitude:
                dist = haversine_distance(current_user.latitude, current_user.longitude, u.latitude, u.longitude)
                if dist <= 10:
                    nearby_count += 1

    return render_template("dashboard.html", top_matches=top_matches, nearby_count=nearby_count)


@app.route("/profile/<user_id>")
@login_required
def profile_view(user_id):
    user = get_user_by_id(user_id)
    if not user:
        flash("User not found.", "error")
        return redirect(url_for("dashboard"))

    feature_vector = user.get_feature_vector()

    compatibility_score = None
    constraint_issues = []
    if str(current_user.id) != str(user.id):
        compatibility_score = compute_compatibility(
            current_user.get_feature_vector(), feature_vector, current_user.bio or "", user.bio or ""
        )
        constraint_issues = check_hard_constraints(current_user, user)

    return render_template(
        "profile.html",
        user=user,
        feature_vector=feature_vector,
        compatibility_score=compatibility_score,
        constraint_issues=constraint_issues,
    )


@app.route("/edit-profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    if request.method == "POST":
        payload = {
            "full_name": request.form.get("full_name", current_user.full_name),
            "age": _as_int(request.form.get("age"), current_user.age),
            "gender": request.form.get("gender", current_user.gender),
            "occupation": request.form.get("occupation", current_user.occupation),
            "city": request.form.get("city", current_user.city),
            "locality": request.form.get("locality", current_user.locality),
            "home_city": request.form.get("home_city", current_user.home_city),
            "home_locality": request.form.get("home_locality", current_user.home_locality),
            "bio": request.form.get("bio", current_user.bio),
            "sleep_schedule": _as_int(request.form.get("sleep_schedule"), 3),
            "cleanliness": _as_int(request.form.get("cleanliness"), 3),
            "noise_tolerance": _as_int(request.form.get("noise_tolerance"), 3),
            "cooking_frequency": _as_int(request.form.get("cooking_frequency"), 3),
            "guest_frequency": _as_int(request.form.get("guest_frequency"), 3),
            "workout_habit": _as_int(request.form.get("workout_habit"), 3),
            "introversion_extroversion": _as_int(request.form.get("introversion_extroversion"), 3),
            "communication_style": _as_int(request.form.get("communication_style"), 3),
            "conflict_resolution": _as_int(request.form.get("conflict_resolution"), 3),
            "social_battery": _as_int(request.form.get("social_battery"), 3),
            "budget_min": _as_int(request.form.get("budget_min"), 0) or None,
            "budget_max": _as_int(request.form.get("budget_max"), 0) or None,
            "smoking": request.form.get("smoking", "never"),
            "drinking": request.form.get("drinking", "never"),
            "pet_friendly": bool(request.form.get("pet_friendly")),
            "veg_nonveg": request.form.get("veg_nonveg", "nonveg"),
            "gender_preference": request.form.get("gender_preference", "any"),
            "interests": [i.strip() for i in request.form.get("interests", "").split(",") if i.strip()],
            "profile_complete": True,
            "updated_at": datetime.utcnow(),
        }

        lat = _as_float(request.form.get("latitude"))
        lng = _as_float(request.form.get("longitude"))
        if lat is not None and lng is not None:
            payload["latitude"] = lat
            payload["longitude"] = lng

        home_lat = _as_float(request.form.get("home_latitude"))
        home_lng = _as_float(request.form.get("home_longitude"))
        if home_lat is not None and home_lng is not None:
            payload["home_latitude"] = home_lat
            payload["home_longitude"] = home_lng

        updated_user = upsert_user_profile(current_user.id, payload)
        login_user(updated_user)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile_view", user_id=current_user.id))

    return render_template("edit_profile.html", user=current_user)


@app.route("/map")
@login_required
def map_view():
    return redirect(url_for("search_view"))


@app.route("/search")
@login_required
def search_view():
    all_users = get_all_active_users(exclude_user_id=current_user.id)
    gender = request.args.get("gender")
    occupation = request.args.get("occupation")
    smoking = request.args.get("smoking")
    veg_nonveg = request.args.get("veg_nonveg")
    max_distance = request.args.get("max_distance")
    radius = _as_float(max_distance, 20.0)

    # Step 1: geospatial discovery first.
    discovered = discover_candidates_by_location(current_user, all_users, radius_km=radius)

    # Step 2: apply filters on discovered candidates.
    if gender:
        discovered = [d for d in discovered if d["user"].gender == gender]
    if occupation:
        discovered = [d for d in discovered if d["user"].occupation == occupation]
    if smoking:
        discovered = [d for d in discovered if d["user"].smoking == smoking]
    if veg_nonveg:
        discovered = [d for d in discovered if d["user"].veg_nonveg == veg_nonveg]

    results = discovered

    return render_template("search.html", results=results)


@app.route("/compare")
@login_required
def compare_view():
    all_users = get_all_active_users()

    user1_id = request.args.get("user1")
    user2_id = request.args.get("user2")

    comparison = None
    user_a = user_b = None
    vec_a = vec_b = {}
    score = 0
    overlaps = conflicts = []
    constraint_issues = []
    discussion_prompts = ""

    if user1_id and user2_id:
        user_a = get_user_by_id(user1_id)
        user_b = get_user_by_id(user2_id)
        if user_a and user_b:
            vec_a = user_a.get_feature_vector()
            vec_b = user_b.get_feature_vector()
            score = compute_compatibility(vec_a, vec_b, user_a.bio or "", user_b.bio or "")
            comparison = compute_feature_differential(vec_a, vec_b)
            overlaps, conflicts = get_top_overlaps_and_conflicts(vec_a, vec_b, n=5)
            constraint_issues = check_hard_constraints(user_a, user_b)
            discussion_prompts = generate_conflict_prompts(vec_a, vec_b, user_b.full_name)

    return render_template(
        "compare.html",
        all_users=all_users,
        comparison=comparison,
        user_a=user_a,
        user_b=user_b,
        vec_a=vec_a,
        vec_b=vec_b,
        score=score,
        overlaps=overlaps,
        conflicts=conflicts,
        constraint_issues=constraint_issues,
        discussion_prompts=discussion_prompts,
    )


@app.route("/chatbot")
@login_required
def chatbot_view():
    chat_history = get_chat_history(current_user.id, limit=50)
    return render_template("chatbot.html", chat_history=chat_history)


@app.route("/api/map-search")
@login_required
def api_map_search():
    radius = request.args.get("radius", 10, type=float)

    all_users = get_all_active_users(exclude_user_id=current_user.id)

    discovered = discover_candidates_by_location(current_user, all_users, radius_km=radius)
    results = []
    for item in discovered:
        user = item["user"]
        target_lat, target_lng = user.latitude, user.longitude
        target_city = user.city or ""
        target_locality = user.locality or ""

        results.append(
            {
                "id": user.id,
                "name": user.full_name,
                "occupation": user.occupation.replace("_", " ").title(),
                "city": target_city,
                "locality": target_locality,
                "lat": target_lat,
                "lng": target_lng,
                "distance": item["distance_km"],
            }
        )

    return jsonify({"results": results})


@app.route("/api/chat", methods=["POST"])
@login_required
def api_chat():
    data = request.get_json() or {}
    message = data.get("message", "").strip()

    if not message:
        return jsonify({"response": "Please type a message."})

    chat_col.insert_one(
        {
            "_id": uuid.uuid4().hex,
            "user_id": str(current_user.id),
            "role": "user",
            "message": message,
            "created_at": datetime.utcnow(),
        }
    )

    response = generate_response(message, user=current_user)

    chat_col.insert_one(
        {
            "_id": uuid.uuid4().hex,
            "user_id": str(current_user.id),
            "role": "bot",
            "message": response,
            "created_at": datetime.utcnow(),
        }
    )

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

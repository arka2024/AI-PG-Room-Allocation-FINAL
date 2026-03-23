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


class SimpleQuery:
    """Small chainable query wrapper for template compatibility."""

    def __init__(self, items):
        self.items = list(items)

    def count(self):
        return len(self.items)

    def order_by(self, _):
        self.items = sorted(self.items, key=lambda x: x.created_at, reverse=True)
        return self

    def limit(self, n):
        self.items = self.items[:n]
        return self

    def all(self):
        return self.items


class ReviewSortShim:
    class created_at:
        @staticmethod
        def desc():
            return "created_at_desc"


Review = ReviewSortShim


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

    @property
    def reviews_received(self):
        items = list(reviews_col.find({"reviewed_id": self.id}).sort("created_at", -1))
        mapped = [MongoReview(r) for r in items]
        return SimpleQuery(mapped)

    def get_avg_rating(self):
        ratings = [r.overall_rating for r in self.reviews_received.all() if r.overall_rating is not None]
        if not ratings:
            return None
        return round(sum(ratings) / len(ratings), 1)


class MongoReview:
    def __init__(self, doc):
        self._doc = dict(doc)
        self.id = str(self._doc.get("_id"))
        self.reviewer_id = str(self._doc.get("reviewer_id"))
        self.reviewed_id = str(self._doc.get("reviewed_id"))
        self.overall_rating = self._doc.get("overall_rating")
        self.cleanliness_rating = self._doc.get("cleanliness_rating")
        self.communication_rating = self._doc.get("communication_rating")
        self.respect_rating = self._doc.get("respect_rating")
        self.reliability_rating = self._doc.get("reliability_rating")
        self.comment = self._doc.get("comment")
        self.duration_months = self._doc.get("duration_months")
        self.would_recommend = bool(self._doc.get("would_recommend", True))
        self.created_at = self._doc.get("created_at") or datetime.utcnow()
        self.reviewer = get_user_by_id(self.reviewer_id)
        self.reviewed = get_user_by_id(self.reviewed_id)


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
reviews_col = mongo_db["reviews"]
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
_safe_create_index(reviews_col, [("reviewed_id", 1), ("created_at", -1)])
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
    query = {"is_looking": True}
    docs = list(users_col.find(query))
    users = [_to_user(d) for d in docs]
    if exclude_user_id is not None:
        users = [u for u in users if u and str(u.id) != str(exclude_user_id)]
    return [u for u in users if u]


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
        "latitude": _as_float(form.get("latitude")),
        "longitude": _as_float(form.get("longitude")),
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
    }
    users_col.insert_one(user_doc)
    return get_user_by_id(user_id)


def get_recent_reviews(limit=20):
    docs = list(reviews_col.find().sort("created_at", -1).limit(limit))
    return [MongoReview(d) for d in docs]


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
    top_matches = rank_users_by_compatibility(current_user, all_users)

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

    recent_reviews = user.reviews_received.limit(5).all()
    return render_template(
        "profile.html",
        user=user,
        feature_vector=feature_vector,
        compatibility_score=compatibility_score,
        constraint_issues=constraint_issues,
        review_model=Review,
        recent_reviews=recent_reviews,
        reviews_count=user.reviews_received.count(),
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

        updated_user = upsert_user_profile(current_user.id, payload)
        login_user(updated_user)
        flash("Profile updated successfully!", "success")
        return redirect(url_for("profile_view", user_id=current_user.id))

    return render_template("edit_profile.html", user=current_user)


@app.route("/map")
@login_required
def map_view():
    return render_template("map.html")


@app.route("/search")
@login_required
def search_view():
    all_users = get_all_active_users(exclude_user_id=current_user.id)

    gender = request.args.get("gender")
    occupation = request.args.get("occupation")
    smoking = request.args.get("smoking")
    veg_nonveg = request.args.get("veg_nonveg")
    max_distance = request.args.get("max_distance")
    min_score = request.args.get("min_score")

    if gender:
        all_users = [u for u in all_users if u.gender == gender]
    if occupation:
        all_users = [u for u in all_users if u.occupation == occupation]
    if smoking:
        all_users = [u for u in all_users if u.smoking == smoking]
    if veg_nonveg:
        all_users = [u for u in all_users if u.veg_nonveg == veg_nonveg]

    radius = _as_float(max_distance)
    results = rank_users_by_compatibility(current_user, all_users, radius_km=radius)

    if min_score:
        min_score_val = _as_float(min_score, 0)
        results = [r for r in results if r["score"] >= min_score_val]

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


@app.route("/reviews")
@login_required
def reviews_view():
    all_users = [u for u in get_all_active_users() if str(u.id) != str(current_user.id)]
    reviews = get_recent_reviews(limit=20)
    return render_template("reviews.html", all_users=all_users, reviews=reviews)


@app.route("/reviews/write/<user_id>")
@login_required
def write_review(user_id):
    all_users = [u for u in get_all_active_users() if str(u.id) != str(current_user.id)]
    reviews = get_recent_reviews(limit=20)
    return render_template("reviews.html", all_users=all_users, reviews=reviews)


@app.route("/reviews/submit", methods=["POST"])
@login_required
def submit_review():
    reviewed_id = request.form.get("reviewed_id")
    overall_rating = _as_float(request.form.get("overall_rating"))

    if not reviewed_id or not overall_rating:
        flash("Please select a user and provide an overall rating.", "error")
        return redirect(url_for("reviews_view"))

    review_doc = {
        "_id": uuid.uuid4().hex,
        "reviewer_id": str(current_user.id),
        "reviewed_id": str(reviewed_id),
        "overall_rating": overall_rating,
        "cleanliness_rating": _as_float(request.form.get("cleanliness_rating")),
        "communication_rating": _as_float(request.form.get("communication_rating")),
        "respect_rating": _as_float(request.form.get("respect_rating")),
        "reliability_rating": _as_float(request.form.get("reliability_rating")),
        "comment": request.form.get("comment", "").strip(),
        "duration_months": _as_int(request.form.get("duration_months"), 0) or None,
        "would_recommend": bool(request.form.get("would_recommend")),
        "created_at": datetime.utcnow(),
    }

    reviews_col.insert_one(review_doc)
    flash("Review submitted successfully!", "success")
    return redirect(url_for("reviews_view"))


@app.route("/chatbot")
@login_required
def chatbot_view():
    chat_history = get_chat_history(current_user.id, limit=50)
    return render_template("chatbot.html", chat_history=chat_history)


@app.route("/api/map-search")
@login_required
def api_map_search():
    radius = request.args.get("radius", 10, type=float)
    min_score = request.args.get("min_score", 0, type=float)

    all_users = get_all_active_users(exclude_user_id=current_user.id)
    all_users = [u for u in all_users if u.latitude is not None and u.longitude is not None]

    results = []
    query_vec = current_user.get_feature_vector()

    for user in all_users:
        if not current_user.latitude or not current_user.longitude:
            continue

        dist = haversine_distance(current_user.latitude, current_user.longitude, user.latitude, user.longitude)
        if dist > radius:
            continue

        score = compute_compatibility(query_vec, user.get_feature_vector(), current_user.bio or "", user.bio or "")
        if score < min_score:
            continue

        results.append(
            {
                "id": user.id,
                "name": user.full_name,
                "occupation": user.occupation.replace("_", " ").title(),
                "city": user.city or "",
                "lat": user.latitude,
                "lng": user.longitude,
                "score": score,
                "distance": round(dist, 1),
            }
        )

    results.sort(key=lambda x: x["score"], reverse=True)
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

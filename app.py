"""
CohabitAI - Main Flask Application
Local JSON-backed roommate matching platform.
"""

import json
import os
import random
import re
import uuid
from datetime import datetime
from pathlib import Path
from threading import Lock

import requests
from flask import Flask, flash, jsonify, redirect, render_template, request, url_for
from flask_login import LoginManager, UserMixin, current_user, login_required, login_user, logout_user
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


class LocalUser(UserMixin):
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
        
        ca = self._doc.get("created_at")
        if isinstance(ca, str):
            try:
                self.created_at = datetime.fromisoformat(ca.replace('Z', '+00:00'))
            except (ValueError, TypeError):
                self.created_at = datetime.utcnow()
        elif isinstance(ca, datetime):
            self.created_at = ca
        else:
            self.created_at = datetime.utcnow()


# App configuration
app = Flask(__name__)
app.config["SECRET_KEY"] = "cohabitai-secret-key-2026"

USERS_FILE = Path(os.getenv("USERS_FILE_PATH", "local_data/users_local_balanced.json"))
_USERS_LOCK = Lock()
FALLBACK_SEARCH_LAT = 20.2961
FALLBACK_SEARCH_LNG = 85.8245

QUESTION_SEGMENTS = {
    "sleep_schedule": {
        "label": "Sleep Schedule",
        "group": "lifestyle",
        "impact": "high",
        "left_label": "Early Bird",
        "right_label": "Night Owl",
    },
    "cleanliness": {
        "label": "Cleanliness",
        "group": "lifestyle",
        "impact": "high",
        "left_label": "Relaxed",
        "right_label": "Very Tidy",
    },
    "noise_tolerance": {
        "label": "Noise Tolerance",
        "group": "lifestyle",
        "impact": "high",
        "left_label": "Needs Quiet",
        "right_label": "Noise-Friendly",
    },
    "cooking_frequency": {
        "label": "Cooking Frequency",
        "group": "lifestyle",
        "impact": "medium",
        "left_label": "Never Cook",
        "right_label": "Daily Cook",
    },
    "guest_frequency": {
        "label": "Guest Frequency",
        "group": "lifestyle",
        "impact": "medium",
        "left_label": "No Guests",
        "right_label": "Frequent Guests",
    },
    "workout_habit": {
        "label": "Workout Habit",
        "group": "lifestyle",
        "impact": "low",
        "left_label": "Sedentary",
        "right_label": "Daily Gym",
    },
    "introversion_extroversion": {
        "label": "Introversion / Extroversion",
        "group": "personality",
        "impact": "medium",
        "left_label": "Introvert",
        "right_label": "Extrovert",
    },
    "communication_style": {
        "label": "Communication Style",
        "group": "personality",
        "impact": "medium",
        "left_label": "Reserved",
        "right_label": "Very Open",
    },
    "conflict_resolution": {
        "label": "Conflict Resolution",
        "group": "personality",
        "impact": "medium",
        "left_label": "Avoidant",
        "right_label": "Direct",
    },
    "social_battery": {
        "label": "Social Battery",
        "group": "personality",
        "impact": "medium",
        "left_label": "Needs Alone Time",
        "right_label": "Always Social",
    },
}

DEFAULT_QUESTION_BANK = {
    "sleep_schedule": [
        {
            "question": "When do you typically go to sleep?",
            "options": [
                {"text": "Before 9 PM (very early)", "score": 1},
                {"text": "9-10 PM (early)", "score": 2},
                {"text": "10-11 PM (normal)", "score": 3},
                {"text": "11 PM - 12 AM (late)", "score": 4},
                {"text": "After 12 AM (very late)", "score": 5},
            ]
        },
        {
            "question": "How do you feel about 6 AM wake-ups?",
            "options": [
                {"text": "I love early mornings", "score": 1},
                {"text": "It's manageable", "score": 2},
                {"text": "It's okay sometimes", "score": 3},
                {"text": "I'd rather not", "score": 4},
                {"text": "Absolutely not", "score": 5},
            ]
        },
        {
            "question": "How often do you stay awake past midnight?",
            "options": [
                {"text": "Almost never", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Often", "score": 4},
                {"text": "Very frequently", "score": 5},
            ]
        },
    ],
    "cleanliness": [
        {
            "question": "How quickly do you clean dishes after eating?",
            "options": [
                {"text": "Immediately", "score": 5},
                {"text": "Within an hour", "score": 4},
                {"text": "Same day", "score": 3},
                {"text": "Next day", "score": 2},
                {"text": "Whenever I get around to it", "score": 1},
            ]
        },
        {
            "question": "How comfortable are you with visible mess?",
            "options": [
                {"text": "I'm very bothered by it", "score": 5},
                {"text": "It bothers me", "score": 4},
                {"text": "It's somewhat okay", "score": 3},
                {"text": "I don't mind much", "score": 2},
                {"text": "I'm completely fine with it", "score": 1},
            ]
        },
        {
            "question": "How often do you deep-clean your space?",
            "options": [
                {"text": "Multiple times a week", "score": 5},
                {"text": "Weekly", "score": 4},
                {"text": "Monthly", "score": 3},
                {"text": "When needed", "score": 2},
                {"text": "Rarely", "score": 1},
            ]
        },
    ],
    "noise_tolerance": [
        {
            "question": "How do you feel about background noise while working/studying?",
            "options": [
                {"text": "I need complete silence", "score": 1},
                {"text": "I prefer quiet", "score": 2},
                {"text": "Some noise is okay", "score": 3},
                {"text": "I'm comfortable with noise", "score": 4},
                {"text": "I prefer having background noise", "score": 5},
            ]
        },
        {
            "question": "How would you react if your roommate was calling/on video late?",
            "options": [
                {"text": "Very bothered", "score": 1},
                {"text": "Somewhat bothered", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Okay with it", "score": 4},
                {"text": "Completely fine", "score": 5},
            ]
        },
        {
            "question": "Would occasional loud social gatherings at home bother you?",
            "options": [
                {"text": "Definitely would bother me", "score": 1},
                {"text": "Probably would bother me", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Probably wouldn't bother me", "score": 4},
                {"text": "Not at all", "score": 5},
            ]
        },
    ],
    "cooking_frequency": [
        {
            "question": "How many days per week do you cook?",
            "options": [
                {"text": "Never/Always order out", "score": 1},
                {"text": "1-2 days", "score": 2},
                {"text": "3-4 days", "score": 3},
                {"text": "5-6 days", "score": 4},
                {"text": "Daily", "score": 5},
            ]
        },
        {
            "question": "How often would you use the kitchen after 9 PM?",
            "options": [
                {"text": "Never", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Often", "score": 4},
                {"text": "Very frequently", "score": 5},
            ]
        },
        {
            "question": "Do you enjoy meal prep or batch cooking?",
            "options": [
                {"text": "Not at all", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Often", "score": 4},
                {"text": "Yes, love it", "score": 5},
            ]
        },
    ],
    "guest_frequency": [
        {
            "question": "How often do friends visit your place monthly?",
            "options": [
                {"text": "Almost never", "score": 1},
                {"text": "1-2 times", "score": 2},
                {"text": "2-3 times", "score": 3},
                {"text": "Weekly", "score": 4},
                {"text": "Multiple times a week", "score": 5},
            ]
        },
        {
            "question": "How comfortable are you hosting guests last-minute?",
            "options": [
                {"text": "Very uncomfortable", "score": 1},
                {"text": "Somewhat uncomfortable", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Comfortable", "score": 4},
                {"text": "Very comfortable", "score": 5},
            ]
        },
        {
            "question": "How likely are overnight guest stays in your routine?",
            "options": [
                {"text": "Very unlikely", "score": 1},
                {"text": "Unlikely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Likely", "score": 4},
                {"text": "Very likely", "score": 5},
            ]
        },
    ],
    "workout_habit": [
        {
            "question": "How many days per week do you exercise?",
            "options": [
                {"text": "Never", "score": 1},
                {"text": "1-2 days", "score": 2},
                {"text": "3-4 days", "score": 3},
                {"text": "5-6 days", "score": 4},
                {"text": "Daily", "score": 5},
            ]
        },
        {
            "question": "How consistent is your workout routine?",
            "options": [
                {"text": "I don't have a routine", "score": 1},
                {"text": "Very inconsistent", "score": 2},
                {"text": "Somewhat consistent", "score": 3},
                {"text": "Mostly consistent", "score": 4},
                {"text": "Very consistent", "score": 5},
            ]
        },
        {
            "question": "How does early morning gym sound to you?",
            "options": [
                {"text": "No way", "score": 1},
                {"text": "Not appealing", "score": 2},
                {"text": "Maybe sometimes", "score": 3},
                {"text": "I'd consider it", "score": 4},
                {"text": "I love early gym", "score": 5},
            ]
        },
    ],
    "introversion_extroversion": [
        {
            "question": "After a long day, do you recharge better alone or with people?",
            "options": [
                {"text": "Definitely alone", "score": 1},
                {"text": "Probably alone", "score": 2},
                {"text": "No preference", "score": 3},
                {"text": "Probably with people", "score": 4},
                {"text": "Definitely with people", "score": 5},
            ]
        },
        {
            "question": "How energized do you feel at social gatherings?",
            "options": [
                {"text": "Drained", "score": 1},
                {"text": "Somewhat drained", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Somewhat energized", "score": 4},
                {"text": "Very energized", "score": 5},
            ]
        },
        {
            "question": "How likely are you to start conversations with strangers?",
            "options": [
                {"text": "Very unlikely", "score": 1},
                {"text": "Unlikely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Likely", "score": 4},
                {"text": "Very likely", "score": 5},
            ]
        },
    ],
    "communication_style": [
        {
            "question": "When something bothers you, do you address it directly?",
            "options": [
                {"text": "Never, I avoid it", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Usually", "score": 4},
                {"text": "Always, immediately", "score": 5},
            ]
        },
        {
            "question": "Do you prefer direct feedback or gentle hints?",
            "options": [
                {"text": "Gentle hints only", "score": 1},
                {"text": "Mostly hints", "score": 2},
                {"text": "Both equally", "score": 3},
                {"text": "Mostly direct", "score": 4},
                {"text": "Direct feedback always", "score": 5},
            ]
        },
        {
            "question": "How open are you about your daily boundaries?",
            "options": [
                {"text": "Very private, rarely share", "score": 1},
                {"text": "Share minimally", "score": 2},
                {"text": "Moderately open", "score": 3},
                {"text": "Quite open", "score": 4},
                {"text": "Very transparent", "score": 5},
            ]
        },
    ],
    "conflict_resolution": [
        {
            "question": "When conflict happens, do you address it immediately?",
            "options": [
                {"text": "Never", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Usually", "score": 4},
                {"text": "Always", "score": 5},
            ]
        },
        {
            "question": "How willing are you to compromise?",
            "options": [
                {"text": "Very unwilling", "score": 1},
                {"text": "Somewhat unwilling", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Somewhat willing", "score": 4},
                {"text": "Very willing", "score": 5},
            ]
        },
        {
            "question": "Do you need cooling-off time before difficult conversations?",
            "options": [
                {"text": "Always need time", "score": 1},
                {"text": "Usually need time", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Rarely need time", "score": 4},
                {"text": "Can discuss immediately", "score": 5},
            ]
        },
    ],
    "social_battery": [
        {
            "question": "How much alone time do you need to feel recharged?",
            "options": [
                {"text": "Lots of daily alone time", "score": 1},
                {"text": "Several hours daily", "score": 2},
                {"text": "Some time daily", "score": 3},
                {"text": "A little time", "score": 4},
                {"text": "Minimal or no need", "score": 5},
            ]
        },
        {
            "question": "How often do you want shared meals/conversations at home?",
            "options": [
                {"text": "Almost never", "score": 1},
                {"text": "Rarely", "score": 2},
                {"text": "Sometimes", "score": 3},
                {"text": "Often", "score": 4},
                {"text": "Always", "score": 5},
            ]
        },
        {
            "question": "Do frequent home interactions energize or drain you?",
            "options": [
                {"text": "Very draining", "score": 1},
                {"text": "Somewhat draining", "score": 2},
                {"text": "Neutral", "score": 3},
                {"text": "Somewhat energizing", "score": 4},
                {"text": "Very energizing", "score": 5},
            ]
        },
    ],
}


def _question_generation_prompt():
    schema = {key: ["question 1", "question 2", "question 3"] for key in QUESTION_SEGMENTS}
    instructions = (
        "Generate a RANDOM personality and lifestyle questionnaire for roommate matching. "
        "You must create exactly 3 short, unique questions for each key in the schema. "
        "Questions must be in plain English, <= 110 characters, no numbering prefixes, no markdown. "
        "Output JSON only, with the exact keys, and each value must be an array of 3 strings."
    )
    return f"{instructions}\nSchema keys:\n{json.dumps(schema, indent=2)}"


def _extract_first_json_object(text):
    if not text:
        return None
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _normalize_question_map(raw_map):
    if not isinstance(raw_map, dict):
        return None

    normalized = {}
    for key in QUESTION_SEGMENTS:
        values = raw_map.get(key)
        if not isinstance(values, list):
            return None

        clean_questions = []
        for item in values:
            if not isinstance(item, dict):
                continue
            question_text = item.get("question", "")
            options = item.get("options", [])
            
            if not question_text or not isinstance(options, list) or len(options) < 3:
                continue
            
            q = " ".join(question_text.strip().split())
            if not q.endswith("?"):
                q = f"{q}?"
            
            # Validate options have text and score
            valid_options = []
            for opt in options:
                if isinstance(opt, dict) and "text" in opt and "score" in opt:
                    valid_options.append(opt)
            
            if len(valid_options) >= 3:
                clean_questions.append({"question": q[:120], "options": valid_options})

        deduped = {q["question"]: q for q in clean_questions}.values()
        if len(deduped) < 3:
            return None

        normalized[key] = list(deduped)[:3]

    return normalized


def _build_fallback_questions():
    questions = {}
    for key, bank in DEFAULT_QUESTION_BANK.items():
        selected = random.sample(bank, k=3) if len(bank) >= 3 else bank[:]
        questions[key] = selected
    return questions


def _generate_questions_from_ollama(prompt_text):
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
    model = os.getenv("GEMMA_MODEL", "gemma3:4b")
    payload = {
        "model": model,
        "prompt": prompt_text,
        "stream": False,
        "options": {
            "temperature": 1.1,
            "top_p": 0.95,
        },
    }
    response = requests.post(ollama_url, json=payload, timeout=30)
    response.raise_for_status()
    body = response.json()
    generated = body.get("response", "")
    parsed = _extract_first_json_object(generated)
    normalized = _normalize_question_map(parsed)
    if not normalized:
        raise ValueError("Invalid questionnaire JSON from Ollama Gemma")
    return normalized, model


def _generate_questions_from_google(prompt_text):
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY missing")

    model = os.getenv("GEMINI_MODEL", "gemma-3-4b-it")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "temperature": 1.1,
            "topP": 0.95,
            "responseMimeType": "application/json",
        },
    }
    response = requests.post(url, json=payload, timeout=45)
    response.raise_for_status()
    data = response.json()
    text = data["candidates"][0]["content"]["parts"][0].get("text", "")
    parsed = _extract_first_json_object(text)
    normalized = _normalize_question_map(parsed)
    if not normalized:
        raise ValueError("Invalid questionnaire JSON from Google Gemma")
    return normalized, model


def generate_segment_questions():
    """Load pre-generated questions from JSON file and randomly select for user."""
    questions_file = Path("local_data/ai_questions_pool.json")
    
    if not questions_file.exists():
        return _build_fallback_questions(), "fallback:local-default"
    
    try:
        with open(questions_file, "r", encoding="utf-8") as f:
            pool = json.load(f)
        
        selected = {}
        for segment_key, segment_data in pool.items():
            if isinstance(segment_data, dict) and "questions" in segment_data:
                available = segment_data["questions"]
                if isinstance(available, list) and len(available) > 0:
                    selected[segment_key] = random.sample(available, k=min(3, len(available)))
        
        source = pool.get("_metadata", {}).get("source", "json:ai-pool")
        return selected, source if selected else pool.get("sleep_schedule", {}).get("source", "json:ai-pool")
    except Exception as e:
        print(f"Warning: Failed to load question pool: {e}")
        return _build_fallback_questions(), "fallback:error"


def _load_users_docs():
    if not USERS_FILE.exists():
        odisha_dataset = Path("Ideas and Dataset Synthesis/odisha_users.json")
        if odisha_dataset.exists():
            docs = json.loads(odisha_dataset.read_text(encoding="utf-8") or "[]")
            if isinstance(docs, list):
                USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
                USERS_FILE.write_text(json.dumps(docs, ensure_ascii=False, indent=2), encoding="utf-8")

    if not USERS_FILE.exists():
        USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
        USERS_FILE.write_text("[]", encoding="utf-8")

    raw = USERS_FILE.read_text(encoding="utf-8")
    docs = json.loads(raw) if raw.strip() else []
    if not isinstance(docs, list):
        raise ValueError(f"{USERS_FILE} must contain a JSON array")

    changed = False
    for doc in docs:
        if "_id" not in doc or doc.get("_id") in (None, ""):
            doc["_id"] = uuid.uuid4().hex
            changed = True
        else:
            doc["_id"] = str(doc.get("_id"))
    if changed:
        _write_users_docs(docs)
    return docs


def _write_users_docs(docs):
    payload = json.dumps(docs, ensure_ascii=False, indent=2)
    USERS_FILE.parent.mkdir(parents=True, exist_ok=True)
    USERS_FILE.write_text(payload, encoding="utf-8")


def _with_users_docs(mutator=None):
    with _USERS_LOCK:
        docs = _load_users_docs()
        if mutator is None:
            return docs
        updated = mutator(docs)
        _write_users_docs(docs)
        return updated

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
    return LocalUser(doc)


def get_user_by_id(user_id):
    target_id = str(user_id)
    docs = _with_users_docs()
    doc = next((d for d in docs if str(d.get("_id")) == target_id), None)
    return _to_user(doc)


def get_user_by_email(email):
    email_norm = (email or "").strip().lower()
    docs = _with_users_docs()
    doc = next((d for d in docs if (d.get("email") or "").strip().lower() == email_norm), None)
    return _to_user(doc)


def get_all_active_users(exclude_user_id=None):
    docs = _with_users_docs()
    users = []
    for d in docs:
        if not d.get("is_looking", True):
            continue
        if d.get("full_name") == "Test User":
            continue
        email = (d.get("email") or "").lower()
        if email.startswith("test_") and email.endswith("@example.com"):
            continue
        users.append(_to_user(d))

    if exclude_user_id is not None:
        users = [u for u in users if u and str(u.id) != str(exclude_user_id)]
    return [u for u in users if u]


def discover_candidates_by_location(query_user, users, radius_km=20.0):
    """Geospatial-first discovery based on preferred PG location only."""
    origin_lat, origin_lng = query_user.latitude, query_user.longitude

    if origin_lat is None or origin_lng is None:
        origin_lat = getattr(query_user, "home_latitude", None)
        origin_lng = getattr(query_user, "home_longitude", None)

    if origin_lat is None or origin_lng is None:
        # Keep discover usable even when user skipped map pinning.
        origin_lat, origin_lng = FALLBACK_SEARCH_LAT, FALLBACK_SEARCH_LNG

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
    target_id = str(user_id)

    def _mutate(docs):
        for doc in docs:
            if str(doc.get("_id")) == target_id:
                doc.update(payload)
                return _to_user(doc)
        return None

    return _with_users_docs(_mutate)


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
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
        "source": "app_signup",
    }

    def _mutate(docs):
        docs.append(user_doc)
        return _to_user(user_doc)

    return _with_users_docs(_mutate)


def get_chat_history(user_id, limit=50):
    target_id = str(user_id)
    docs = _with_users_docs()
    user_doc = next((d for d in docs if str(d.get("_id")) == target_id), None)
    if not user_doc:
        return []

    chat_docs = user_doc.get("_chat_messages", [])
    if not isinstance(chat_docs, list):
        return []

    chat_docs = sorted(chat_docs, key=lambda x: x.get("created_at", ""))[-limit:]
    return [MongoChatMessage(d) for d in chat_docs]


def append_chat_message(user_id, role, message):
    target_id = str(user_id)
    chat_doc = {
        "_id": uuid.uuid4().hex,
        "user_id": target_id,
        "role": role,
        "message": message,
        "created_at": datetime.utcnow().isoformat(),
    }

    def _mutate(docs):
        for doc in docs:
            if str(doc.get("_id")) == target_id:
                if not isinstance(doc.get("_chat_messages"), list):
                    doc["_chat_messages"] = []
                doc["_chat_messages"].append(chat_doc)
                return True
        return False

    return _with_users_docs(_mutate)


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


@app.route("/api/register-questionnaire")
def api_register_questionnaire():
    questions, source = generate_segment_questions()
    segments = []
    
    mcq_options = {
        1: "Strongly Disagree",
        2: "Disagree",
        3: "Neutral",
        4: "Agree",
        5: "Strongly Agree",
    }
    
    for key, meta in QUESTION_SEGMENTS.items():
        item = {"key": key}
        item.update(meta)
        segments.append(item)

    formatted_questions = {}
    for segment_key, question_list in questions.items():
        if segment_key in QUESTION_SEGMENTS:
            formatted_questions[segment_key] = [
                q if isinstance(q, str) else str(q) for q in question_list
            ]
    
    return jsonify(
        {
            "source": source,
            "generated_at": datetime.utcnow().isoformat(),
            "segments": segments,
            "questions": formatted_questions,
            "mcq_options": mcq_options,
        }
    )


@app.route("/api/admin/regenerate-questions", methods=["POST"])
def api_regenerate_questions():
    """Trigger regeneration of AI questions pool using Gemma 3B."""
    if not current_user or not current_user.is_authenticated:
        return jsonify({"error": "Unauthorized"}), 401
    
    admin_emails = os.getenv("ADMIN_EMAILS", "").split(",")
    if current_user.email not in admin_emails:
        return jsonify({"error": "Admin access required"}), 403
    
    try:
        from generate_ai_questions import generate_all_questions
        questions_db = generate_all_questions()
        
        if questions_db:
            return jsonify({
                "status": "success",
                "message": f"Generated {len(questions_db)} question segments",
                "segments": list(questions_db.keys()),
            })
        else:
            return jsonify({
                "status": "error",
                "message": "No questions generated. Check Gemma availability.",
            }), 500
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": str(e),
        }), 500


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
            "updated_at": datetime.utcnow().isoformat(),
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
    radius = _as_float(max_distance, 120.0)

    # Step 1: geospatial discovery first.
    discovered = discover_candidates_by_location(current_user, all_users, radius_km=radius)

    # If user did not set distance and nothing matched nearby, widen to Odisha-wide radius.
    if not discovered and not max_distance:
        discovered = discover_candidates_by_location(current_user, all_users, radius_km=500.0)

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
    radius = request.args.get("radius", 120, type=float)

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

    append_chat_message(current_user.id, "user", message)

    response = generate_response(message, user=current_user)

    append_chat_message(current_user.id, "bot", response)

    return jsonify({"response": response})


if __name__ == "__main__":
    app.run(debug=True, port=5000)

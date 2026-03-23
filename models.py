"""
CohabitAI - Database Models
Defines all SQLAlchemy ORM models for the platform.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime
import json

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """Core user model with authentication and profile data."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    occupation = db.Column(db.String(50), nullable=False)  # student / working_professional / freelancer
    phone = db.Column(db.String(15), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(300), nullable=True)

    # --- Location ---
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    city = db.Column(db.String(100), nullable=True)
    locality = db.Column(db.String(200), nullable=True)

    # --- Lifestyle Dimensions ---
    sleep_schedule = db.Column(db.Integer, nullable=True)       # 1=Early Bird ... 5=Night Owl
    cleanliness = db.Column(db.Integer, nullable=True)          # 1-5
    noise_tolerance = db.Column(db.Integer, nullable=True)      # 1-5
    cooking_frequency = db.Column(db.Integer, nullable=True)    # 1=Never ... 5=Daily
    guest_frequency = db.Column(db.Integer, nullable=True)      # 1=Never ... 5=Very Often
    workout_habit = db.Column(db.Integer, nullable=True)        # 1=Never ... 5=Daily

    # --- Personality Dimensions ---
    introversion_extroversion = db.Column(db.Integer, nullable=True)  # 1=Very Intro ... 5=Very Extro
    communication_style = db.Column(db.Integer, nullable=True)         # 1=Minimal ... 5=Very Open
    conflict_resolution = db.Column(db.Integer, nullable=True)         # 1=Avoidant ... 5=Confrontational
    social_battery = db.Column(db.Integer, nullable=True)              # 1=Needs lots of alone time ... 5=Always social

    # --- Constraints & Preferences ---
    budget_min = db.Column(db.Integer, nullable=True)
    budget_max = db.Column(db.Integer, nullable=True)
    smoking = db.Column(db.String(20), nullable=True)           # never / occasionally / regularly
    drinking = db.Column(db.String(20), nullable=True)          # never / occasionally / regularly
    pet_friendly = db.Column(db.Boolean, default=False)
    veg_nonveg = db.Column(db.String(20), nullable=True)        # veg / nonveg / eggetarian / vegan
    gender_preference = db.Column(db.String(20), nullable=True) # male / female / any
    preferred_move_in = db.Column(db.String(30), nullable=True) # immediate / within_month / flexible

    # --- Interests (stored as JSON list) ---
    interests = db.Column(db.Text, nullable=True)  # JSON array of strings

    # --- Status ---
    is_looking = db.Column(db.Boolean, default=True)
    profile_complete = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def get_interests_list(self):
        if self.interests:
            return json.loads(self.interests)
        return []

    def set_interests_list(self, lst):
        self.interests = json.dumps(lst)

    def get_feature_vector(self):
        """Return the numerical profile vector P for compatibility scoring."""
        return {
            'sleep_schedule': self.sleep_schedule or 3,
            'cleanliness': self.cleanliness or 3,
            'noise_tolerance': self.noise_tolerance or 3,
            'cooking_frequency': self.cooking_frequency or 3,
            'guest_frequency': self.guest_frequency or 3,
            'workout_habit': self.workout_habit or 3,
            'introversion_extroversion': self.introversion_extroversion or 3,
            'communication_style': self.communication_style or 3,
            'conflict_resolution': self.conflict_resolution or 3,
            'social_battery': self.social_battery or 3,
        }

    def __repr__(self):
        return f'<User {self.full_name}>'


class ChatMessage(db.Model):
    """Stores chatbot conversation history."""
    __tablename__ = 'chat_messages'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    role = db.Column(db.String(10), nullable=False)  # 'user' or 'bot'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref='chat_messages')

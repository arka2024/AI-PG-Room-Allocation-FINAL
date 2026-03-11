"""
CohabitAI - Main Flask Application
AI-Driven Geo-Spatial Compatibility Platform for Roommate Allocation
"""

import os
import json
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, Review, ChatMessage
from compatibility import (
    compute_compatibility,
    compute_feature_differential,
    get_top_overlaps_and_conflicts,
    rank_users_by_compatibility,
    check_hard_constraints,
    haversine_distance,
)
from chatbot import generate_response, generate_conflict_prompts

# ─── App Configuration ────────────────────────────────────────────
app = Flask(__name__)
app.config['SECRET_KEY'] = 'cohabitai-secret-key-2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cohabitai.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# ─── Page Routes ──────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/architecture')
def architecture():
    return render_template('architecture.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        if User.query.filter_by(email=email).first():
            flash('Email already registered. Please login.', 'error')
            return redirect(url_for('register'))

        user = User(
            email=email,
            password_hash=generate_password_hash(password),
            full_name=request.form.get('full_name', '').strip(),
            age=int(request.form.get('age', 25)),
            gender=request.form.get('gender', 'male'),
            occupation=request.form.get('occupation', 'student'),
            phone=request.form.get('phone', ''),
            bio=request.form.get('bio', ''),
            city=request.form.get('city', ''),
            locality=request.form.get('locality', ''),
            latitude=float(request.form.get('latitude') or 0) or None,
            longitude=float(request.form.get('longitude') or 0) or None,
            # Lifestyle
            sleep_schedule=int(request.form.get('sleep_schedule', 3)),
            cleanliness=int(request.form.get('cleanliness', 3)),
            noise_tolerance=int(request.form.get('noise_tolerance', 3)),
            cooking_frequency=int(request.form.get('cooking_frequency', 3)),
            guest_frequency=int(request.form.get('guest_frequency', 3)),
            workout_habit=int(request.form.get('workout_habit', 3)),
            # Personality
            introversion_extroversion=int(request.form.get('introversion_extroversion', 3)),
            communication_style=int(request.form.get('communication_style', 3)),
            conflict_resolution=int(request.form.get('conflict_resolution', 3)),
            social_battery=int(request.form.get('social_battery', 3)),
            # Preferences
            budget_min=int(request.form.get('budget_min') or 0) or None,
            budget_max=int(request.form.get('budget_max') or 0) or None,
            smoking=request.form.get('smoking', 'never'),
            drinking=request.form.get('drinking', 'never'),
            pet_friendly=bool(request.form.get('pet_friendly')),
            veg_nonveg=request.form.get('veg_nonveg', 'nonveg'),
            gender_preference=request.form.get('gender_preference', 'any'),
            preferred_move_in=request.form.get('preferred_move_in', 'flexible'),
            profile_complete=True,
            is_looking=True,
        )
        interests = request.form.get('interests', '')
        if interests:
            user.set_interests_list([i.strip() for i in interests.split(',') if i.strip()])

        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Profile created successfully! Welcome to CohabitAI.', 'success')
        return redirect(url_for('dashboard'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            flash(f'Welcome back, {user.full_name.split()[0]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password.', 'error')

    return render_template('login.html')


@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))


@app.route('/dashboard')
@login_required
def dashboard():
    all_users = User.query.filter(User.id != current_user.id, User.is_looking == True).all()
    top_matches = rank_users_by_compatibility(current_user, all_users)

    # Count nearby users
    nearby_count = 0
    if current_user.latitude and current_user.longitude:
        for u in all_users:
            if u.latitude and u.longitude:
                dist = haversine_distance(current_user.latitude, current_user.longitude,
                                          u.latitude, u.longitude)
                if dist <= 10:
                    nearby_count += 1

    return render_template('dashboard.html',
                           top_matches=top_matches,
                           nearby_count=nearby_count)


@app.route('/profile/<int:user_id>')
@login_required
def profile_view(user_id):
    user = User.query.get_or_404(user_id)
    feature_vector = user.get_feature_vector()

    compatibility_score = None
    constraint_issues = []
    if current_user.id != user.id:
        compatibility_score = compute_compatibility(
            current_user.get_feature_vector(), feature_vector
        )
        constraint_issues = check_hard_constraints(current_user, user)

    return render_template('profile.html',
                           user=user,
                           feature_vector=feature_vector,
                           compatibility_score=compatibility_score,
                           constraint_issues=constraint_issues,
                           review_model=Review)


@app.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    if request.method == 'POST':
        u = current_user
        u.full_name = request.form.get('full_name', u.full_name)
        u.age = int(request.form.get('age', u.age))
        u.gender = request.form.get('gender', u.gender)
        u.occupation = request.form.get('occupation', u.occupation)
        u.city = request.form.get('city', u.city)
        u.locality = request.form.get('locality', u.locality)
        u.bio = request.form.get('bio', u.bio)

        lat = request.form.get('latitude', '')
        lng = request.form.get('longitude', '')
        if lat and lng:
            u.latitude = float(lat)
            u.longitude = float(lng)

        u.sleep_schedule = int(request.form.get('sleep_schedule', 3))
        u.cleanliness = int(request.form.get('cleanliness', 3))
        u.noise_tolerance = int(request.form.get('noise_tolerance', 3))
        u.cooking_frequency = int(request.form.get('cooking_frequency', 3))
        u.guest_frequency = int(request.form.get('guest_frequency', 3))
        u.workout_habit = int(request.form.get('workout_habit', 3))
        u.introversion_extroversion = int(request.form.get('introversion_extroversion', 3))
        u.communication_style = int(request.form.get('communication_style', 3))
        u.conflict_resolution = int(request.form.get('conflict_resolution', 3))
        u.social_battery = int(request.form.get('social_battery', 3))
        u.budget_min = int(request.form.get('budget_min') or 0) or None
        u.budget_max = int(request.form.get('budget_max') or 0) or None
        u.smoking = request.form.get('smoking', 'never')
        u.drinking = request.form.get('drinking', 'never')
        u.pet_friendly = bool(request.form.get('pet_friendly'))
        u.veg_nonveg = request.form.get('veg_nonveg', 'nonveg')
        u.gender_preference = request.form.get('gender_preference', 'any')

        interests = request.form.get('interests', '')
        if interests:
            u.set_interests_list([i.strip() for i in interests.split(',') if i.strip()])
        else:
            u.set_interests_list([])

        u.profile_complete = True
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('profile_view', user_id=current_user.id))

    return render_template('edit_profile.html', user=current_user)


@app.route('/map')
@login_required
def map_view():
    return render_template('map.html')


@app.route('/search')
@login_required
def search_view():
    all_users = User.query.filter(User.id != current_user.id, User.is_looking == True).all()

    # Apply explicit filters
    gender = request.args.get('gender')
    occupation = request.args.get('occupation')
    smoking = request.args.get('smoking')
    veg_nonveg = request.args.get('veg_nonveg')
    max_distance = request.args.get('max_distance')
    min_score = request.args.get('min_score')

    if gender:
        all_users = [u for u in all_users if u.gender == gender]
    if occupation:
        all_users = [u for u in all_users if u.occupation == occupation]
    if smoking:
        all_users = [u for u in all_users if u.smoking == smoking]
    if veg_nonveg:
        all_users = [u for u in all_users if u.veg_nonveg == veg_nonveg]

    radius = float(max_distance) if max_distance else None
    results = rank_users_by_compatibility(current_user, all_users, radius_km=radius)

    if min_score:
        results = [r for r in results if r['score'] >= float(min_score)]

    return render_template('search.html', results=results)


@app.route('/compare')
@login_required
def compare_view():
    all_users = User.query.filter(User.is_looking == True).all()

    user1_id = request.args.get('user1', type=int)
    user2_id = request.args.get('user2', type=int)

    comparison = None
    user_a = user_b = None
    vec_a = vec_b = {}
    score = 0
    overlaps = conflicts = []
    constraint_issues = []
    discussion_prompts = ""

    if user1_id and user2_id:
        user_a = User.query.get(user1_id)
        user_b = User.query.get(user2_id)
        if user_a and user_b:
            vec_a = user_a.get_feature_vector()
            vec_b = user_b.get_feature_vector()
            score = compute_compatibility(vec_a, vec_b)
            comparison = compute_feature_differential(vec_a, vec_b)
            overlaps, conflicts = get_top_overlaps_and_conflicts(vec_a, vec_b, n=5)
            constraint_issues = check_hard_constraints(user_a, user_b)
            discussion_prompts = generate_conflict_prompts(vec_a, vec_b, user_b.full_name)

    return render_template('compare.html',
                           all_users=all_users,
                           comparison=comparison,
                           user_a=user_a, user_b=user_b,
                           vec_a=vec_a, vec_b=vec_b,
                           score=score,
                           overlaps=overlaps,
                           conflicts=conflicts,
                           constraint_issues=constraint_issues,
                           discussion_prompts=discussion_prompts)


@app.route('/reviews')
@login_required
def reviews_view():
    all_users = User.query.filter(User.id != current_user.id).all()
    reviews = Review.query.order_by(Review.created_at.desc()).limit(20).all()
    return render_template('reviews.html', all_users=all_users, reviews=reviews)


@app.route('/reviews/write/<int:user_id>')
@login_required
def write_review(user_id):
    all_users = User.query.filter(User.id != current_user.id).all()
    reviews = Review.query.order_by(Review.created_at.desc()).limit(20).all()
    return render_template('reviews.html', all_users=all_users, reviews=reviews)


@app.route('/reviews/submit', methods=['POST'])
@login_required
def submit_review():
    reviewed_id = request.form.get('reviewed_id', type=int)
    overall_rating = request.form.get('overall_rating', type=float)

    if not reviewed_id or not overall_rating:
        flash('Please select a user and provide an overall rating.', 'error')
        return redirect(url_for('reviews_view'))

    review = Review(
        reviewer_id=current_user.id,
        reviewed_id=reviewed_id,
        overall_rating=overall_rating,
        cleanliness_rating=request.form.get('cleanliness_rating', type=float),
        communication_rating=request.form.get('communication_rating', type=float),
        respect_rating=request.form.get('respect_rating', type=float),
        reliability_rating=request.form.get('reliability_rating', type=float),
        comment=request.form.get('comment', '').strip(),
        duration_months=request.form.get('duration_months', type=int),
        would_recommend=bool(request.form.get('would_recommend')),
    )
    db.session.add(review)
    db.session.commit()
    flash('Review submitted successfully!', 'success')
    return redirect(url_for('reviews_view'))


@app.route('/chatbot')
@login_required
def chatbot_view():
    chat_history = ChatMessage.query.filter_by(user_id=current_user.id).order_by(
        ChatMessage.created_at.asc()
    ).limit(50).all()
    return render_template('chatbot.html', chat_history=chat_history)


# ─── API Endpoints ────────────────────────────────────────────────

@app.route('/api/map-search')
@login_required
def api_map_search():
    """Geo-spatial KNN search API for the map module."""
    radius = request.args.get('radius', 10, type=float)
    min_score = request.args.get('min_score', 0, type=float)

    all_users = User.query.filter(
        User.id != current_user.id,
        User.is_looking == True,
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    ).all()

    results = []
    query_vec = current_user.get_feature_vector()

    for user in all_users:
        if not current_user.latitude or not current_user.longitude:
            continue

        dist = haversine_distance(
            current_user.latitude, current_user.longitude,
            user.latitude, user.longitude
        )
        if dist > radius:
            continue

        score = compute_compatibility(query_vec, user.get_feature_vector())
        if score < min_score:
            continue

        results.append({
            'id': user.id,
            'name': user.full_name,
            'occupation': user.occupation.replace('_', ' ').title(),
            'city': user.city or '',
            'lat': user.latitude,
            'lng': user.longitude,
            'score': score,
            'distance': round(dist, 1),
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return jsonify({'results': results})


@app.route('/api/chat', methods=['POST'])
@login_required
def api_chat():
    """Chatbot API endpoint."""
    data = request.get_json()
    message = data.get('message', '').strip()

    if not message:
        return jsonify({'response': 'Please type a message.'})

    # Save user message
    user_msg = ChatMessage(user_id=current_user.id, role='user', message=message)
    db.session.add(user_msg)

    # Generate response
    response = generate_response(message, user=current_user)

    # Save bot response
    bot_msg = ChatMessage(user_id=current_user.id, role='bot', message=response)
    db.session.add(bot_msg)
    db.session.commit()

    return jsonify({'response': response})


# ─── Seed Data ────────────────────────────────────────────────────

def seed_database():
    """Populate database with demo users for testing."""
    if User.query.count() > 0:
        return  # Already seeded

    demo_users = [
        {
            'email': 'priya@demo.com', 'password': 'demo123',
            'full_name': 'Priya Sharma', 'age': 24, 'gender': 'female',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'Salt Lake',
            'latitude': 22.5800, 'longitude': 88.4150,
            'bio': 'Software developer who loves quiet evenings and clean spaces.',
            'sleep_schedule': 2, 'cleanliness': 5, 'noise_tolerance': 2,
            'cooking_frequency': 4, 'guest_frequency': 2, 'workout_habit': 3,
            'introversion_extroversion': 2, 'communication_style': 3,
            'conflict_resolution': 3, 'social_battery': 2,
            'budget_min': 6000, 'budget_max': 12000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': True, 'veg_nonveg': 'veg',
            'gender_preference': 'female',
            'interests': ['Reading', 'Yoga', 'Cooking', 'Classical Music', 'Gardening'],
        },
        {
            'email': 'arjun@demo.com', 'password': 'demo123',
            'full_name': 'Arjun Patel', 'age': 26, 'gender': 'male',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'New Town',
            'latitude': 22.5920, 'longitude': 88.4720,
            'bio': 'Data analyst, weekend cricketer, love spontaneous hangouts.',
            'sleep_schedule': 4, 'cleanliness': 3, 'noise_tolerance': 4,
            'cooking_frequency': 2, 'guest_frequency': 4, 'workout_habit': 4,
            'introversion_extroversion': 4, 'communication_style': 4,
            'conflict_resolution': 4, 'social_battery': 4,
            'budget_min': 7000, 'budget_max': 15000,
            'smoking': 'occasionally', 'drinking': 'occasionally',
            'pet_friendly': False, 'veg_nonveg': 'nonveg',
            'gender_preference': 'male',
            'interests': ['Cricket', 'Gaming', 'Movies', 'Trekking', 'Photography'],
        },
        {
            'email': 'sneha@demo.com', 'password': 'demo123',
            'full_name': 'Sneha Reddy', 'age': 22, 'gender': 'female',
            'occupation': 'student',
            'city': 'Kolkata', 'locality': 'Jadavpur',
            'latitude': 22.4990, 'longitude': 88.3710,
            'bio': 'Final year CS student. Focused and organized. Love chai conversations.',
            'sleep_schedule': 3, 'cleanliness': 4, 'noise_tolerance': 3,
            'cooking_frequency': 3, 'guest_frequency': 3, 'workout_habit': 2,
            'introversion_extroversion': 3, 'communication_style': 4,
            'conflict_resolution': 3, 'social_battery': 3,
            'budget_min': 4000, 'budget_max': 9000,
            'smoking': 'never', 'drinking': 'never',
            'pet_friendly': True, 'veg_nonveg': 'eggetarian',
            'gender_preference': 'female',
            'interests': ['Coding', 'Reading', 'Art', 'Music', 'Tea'],
        },
        {
            'email': 'rahul@demo.com', 'password': 'demo123',
            'full_name': 'Rahul Das', 'age': 28, 'gender': 'male',
            'occupation': 'freelancer',
            'city': 'Kolkata', 'locality': 'Park Street',
            'latitude': 22.5530, 'longitude': 88.3510,
            'bio': 'Freelance graphic designer. Night owl with headphones always on.',
            'sleep_schedule': 5, 'cleanliness': 3, 'noise_tolerance': 5,
            'cooking_frequency': 1, 'guest_frequency': 2, 'workout_habit': 1,
            'introversion_extroversion': 2, 'communication_style': 2,
            'conflict_resolution': 2, 'social_battery': 1,
            'budget_min': 8000, 'budget_max': 18000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': False, 'veg_nonveg': 'nonveg',
            'gender_preference': 'any',
            'interests': ['Design', 'Anime', 'Gaming', 'Coffee', 'Digital Art'],
        },
        {
            'email': 'meera@demo.com', 'password': 'demo123',
            'full_name': 'Meera Joshi', 'age': 25, 'gender': 'female',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'Howrah',
            'latitude': 22.5850, 'longitude': 88.3300,
            'bio': 'Marketing manager. Social butterfly who keeps things tidy.',
            'sleep_schedule': 3, 'cleanliness': 5, 'noise_tolerance': 4,
            'cooking_frequency': 3, 'guest_frequency': 4, 'workout_habit': 4,
            'introversion_extroversion': 5, 'communication_style': 5,
            'conflict_resolution': 4, 'social_battery': 5,
            'budget_min': 8000, 'budget_max': 16000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': True, 'veg_nonveg': 'nonveg',
            'gender_preference': 'female',
            'interests': ['Dancing', 'Travel', 'Food', 'Social Events', 'Fitness'],
        },
        {
            'email': 'vikram@demo.com', 'password': 'demo123',
            'full_name': 'Vikram Singh', 'age': 23, 'gender': 'male',
            'occupation': 'student',
            'city': 'Kolkata', 'locality': 'Ballygunge',
            'latitude': 22.5270, 'longitude': 88.3630,
            'bio': 'MBA student. Early riser, gym lover, very organized.',
            'sleep_schedule': 1, 'cleanliness': 5, 'noise_tolerance': 2,
            'cooking_frequency': 4, 'guest_frequency': 2, 'workout_habit': 5,
            'introversion_extroversion': 3, 'communication_style': 3,
            'conflict_resolution': 4, 'social_battery': 3,
            'budget_min': 5000, 'budget_max': 10000,
            'smoking': 'never', 'drinking': 'never',
            'pet_friendly': False, 'veg_nonveg': 'veg',
            'gender_preference': 'male',
            'interests': ['Gym', 'Finance', 'Cooking', 'Running', 'Meditation'],
        },
        {
            'email': 'anita@demo.com', 'password': 'demo123',
            'full_name': 'Anita Banerjee', 'age': 27, 'gender': 'female',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'Dum Dum',
            'latitude': 22.6240, 'longitude': 88.4240,
            'bio': 'Teacher by day, bookworm by night. Love quiet, peaceful spaces.',
            'sleep_schedule': 2, 'cleanliness': 4, 'noise_tolerance': 1,
            'cooking_frequency': 5, 'guest_frequency': 1, 'workout_habit': 2,
            'introversion_extroversion': 1, 'communication_style': 2,
            'conflict_resolution': 2, 'social_battery': 1,
            'budget_min': 4000, 'budget_max': 8000,
            'smoking': 'never', 'drinking': 'never',
            'pet_friendly': True, 'veg_nonveg': 'veg',
            'gender_preference': 'female',
            'interests': ['Books', 'Writing', 'Bengali Literature', 'Tea', 'Music'],
        },
        {
            'email': 'sanjay@demo.com', 'password': 'demo123',
            'full_name': 'Sanjay Mukherjee', 'age': 30, 'gender': 'male',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'Esplanade',
            'latitude': 22.5640, 'longitude': 88.3520,
            'bio': 'Senior developer at a startup. Balanced lifestyle, easy-going.',
            'sleep_schedule': 3, 'cleanliness': 4, 'noise_tolerance': 3,
            'cooking_frequency': 3, 'guest_frequency': 3, 'workout_habit': 3,
            'introversion_extroversion': 3, 'communication_style': 4,
            'conflict_resolution': 3, 'social_battery': 3,
            'budget_min': 10000, 'budget_max': 20000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': True, 'veg_nonveg': 'nonveg',
            'gender_preference': 'any',
            'interests': ['Tech', 'Music', 'Movies', 'Board Games', 'Cooking'],
        },
        {
            'email': 'kavya@demo.com', 'password': 'demo123',
            'full_name': 'Kavya Nair', 'age': 21, 'gender': 'female',
            'occupation': 'student',
            'city': 'Kolkata', 'locality': 'Gariahat',
            'latitude': 22.5170, 'longitude': 88.3690,
            'bio': 'Journalism student. Creative, spontaneous, and a great listener.',
            'sleep_schedule': 4, 'cleanliness': 3, 'noise_tolerance': 4,
            'cooking_frequency': 2, 'guest_frequency': 4, 'workout_habit': 2,
            'introversion_extroversion': 4, 'communication_style': 5,
            'conflict_resolution': 4, 'social_battery': 4,
            'budget_min': 3500, 'budget_max': 8000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': True, 'veg_nonveg': 'nonveg',
            'gender_preference': 'female',
            'interests': ['Photography', 'Writing', 'Travel', 'Cafe Hopping', 'Film'],
        },
        {
            'email': 'rohan@demo.com', 'password': 'demo123',
            'full_name': 'Rohan Ghosh', 'age': 25, 'gender': 'male',
            'occupation': 'working_professional',
            'city': 'Kolkata', 'locality': 'Rajarhat',
            'latitude': 22.6010, 'longitude': 88.4850,
            'bio': 'Backend engineer. Loves late-night coding, music, and minimalism.',
            'sleep_schedule': 5, 'cleanliness': 4, 'noise_tolerance': 4,
            'cooking_frequency': 2, 'guest_frequency': 1, 'workout_habit': 3,
            'introversion_extroversion': 2, 'communication_style': 3,
            'conflict_resolution': 3, 'social_battery': 2,
            'budget_min': 7000, 'budget_max': 14000,
            'smoking': 'never', 'drinking': 'occasionally',
            'pet_friendly': False, 'veg_nonveg': 'nonveg',
            'gender_preference': 'male',
            'interests': ['Coding', 'Guitar', 'Anime', 'Minimalism', 'Coffee'],
        },
    ]

    for data in demo_users:
        interests = data.pop('interests')
        password = data.pop('password')
        data['password_hash'] = generate_password_hash(password)
        data['profile_complete'] = True
        data['is_looking'] = True
        user = User(**data)
        user.set_interests_list(interests)
        db.session.add(user)

    db.session.commit()

    # Seed some reviews
    demo_reviews = [
        {'reviewer_id': 1, 'reviewed_id': 3, 'overall_rating': 4.5,
         'cleanliness_rating': 5, 'communication_rating': 4,
         'respect_rating': 5, 'reliability_rating': 4,
         'comment': 'Sneha was a wonderful roommate! Very clean and respectful. We had great chai sessions together.',
         'duration_months': 6, 'would_recommend': True},
        {'reviewer_id': 3, 'reviewed_id': 1, 'overall_rating': 5.0,
         'cleanliness_rating': 5, 'communication_rating': 4,
         'respect_rating': 5, 'reliability_rating': 5,
         'comment': 'Priya is the ideal roommate. Organized, considerate, and great cook!',
         'duration_months': 6, 'would_recommend': True},
        {'reviewer_id': 2, 'reviewed_id': 4, 'overall_rating': 3.5,
         'cleanliness_rating': 3, 'communication_rating': 2,
         'respect_rating': 4, 'reliability_rating': 3,
         'comment': 'Rahul is respectful but our schedules were very different. He is a true night owl.',
         'duration_months': 3, 'would_recommend': True},
        {'reviewer_id': 5, 'reviewed_id': 9, 'overall_rating': 4.0,
         'cleanliness_rating': 3, 'communication_rating': 5,
         'respect_rating': 4, 'reliability_rating': 4,
         'comment': 'Kavya is super fun and communicative. Cleanliness could improve but overall great experience.',
         'duration_months': 4, 'would_recommend': True},
        {'reviewer_id': 6, 'reviewed_id': 8, 'overall_rating': 4.5,
         'cleanliness_rating': 4, 'communication_rating': 4,
         'respect_rating': 5, 'reliability_rating': 5,
         'comment': 'Sanjay is very easy-going and reliable. Perfect balance of social and space.',
         'duration_months': 8, 'would_recommend': True},
        {'reviewer_id': 10, 'reviewed_id': 4, 'overall_rating': 4.0,
         'cleanliness_rating': 4, 'communication_rating': 3,
         'respect_rating': 5, 'reliability_rating': 4,
         'comment': 'Fellow night owl! We worked in compatible silence. Great roommate for introverts.',
         'duration_months': 5, 'would_recommend': True},
    ]

    for rev_data in demo_reviews:
        review = Review(**rev_data)
        db.session.add(review)

    db.session.commit()
    print("✅ Database seeded with 10 demo users and 6 reviews.")


# ─── Main Entry Point ────────────────────────────────────────────

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_database()
    app.run(debug=True, port=5000)

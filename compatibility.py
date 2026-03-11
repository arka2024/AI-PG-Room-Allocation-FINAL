"""
CohabitAI - Compatibility Scoring Engine
Implements the Weighted Cosine Similarity measure for user matching.
"""

import numpy as np
from math import radians, sin, cos, sqrt, atan2

# ────────────────────────────────────────────
# Feature weights w_i  (higher = more important)
# ────────────────────────────────────────────
FEATURE_WEIGHTS = {
    'sleep_schedule':             5.0,
    'cleanliness':                5.0,
    'noise_tolerance':            4.5,
    'cooking_frequency':          2.0,
    'guest_frequency':            3.5,
    'workout_habit':              1.5,
    'introversion_extroversion':  4.0,
    'communication_style':        3.5,
    'conflict_resolution':        3.0,
    'social_battery':             4.0,
}

FEATURE_LABELS = {
    'sleep_schedule':             'Sleep Schedule',
    'cleanliness':                'Cleanliness',
    'noise_tolerance':            'Noise Tolerance',
    'cooking_frequency':          'Cooking Frequency',
    'guest_frequency':            'Guest Frequency',
    'workout_habit':              'Workout Habit',
    'introversion_extroversion':  'Introversion / Extroversion',
    'communication_style':        'Communication Style',
    'conflict_resolution':        'Conflict Resolution',
    'social_battery':             'Social Battery',
}

FEATURE_LOW_LABELS = {
    'sleep_schedule':             'Early Bird',
    'cleanliness':                'Relaxed',
    'noise_tolerance':            'Needs Quiet',
    'cooking_frequency':          'Never Cooks',
    'guest_frequency':            'No Guests',
    'workout_habit':              'Sedentary',
    'introversion_extroversion':  'Introvert',
    'communication_style':        'Reserved',
    'conflict_resolution':        'Avoidant',
    'social_battery':             'Needs Alone Time',
}

FEATURE_HIGH_LABELS = {
    'sleep_schedule':             'Night Owl',
    'cleanliness':                'Very Tidy',
    'noise_tolerance':            'Noise-Friendly',
    'cooking_frequency':          'Daily Cook',
    'guest_frequency':            'Frequent Guests',
    'workout_habit':              'Daily Workout',
    'introversion_extroversion':  'Extrovert',
    'communication_style':        'Very Open',
    'conflict_resolution':        'Direct',
    'social_battery':             'Always Social',
}


def compute_compatibility(vec_a: dict, vec_b: dict) -> float:
    """
    Weighted Cosine Similarity × 100.
    Returns a score in [0, 100].
    """
    features = list(FEATURE_WEIGHTS.keys())
    w = np.array([FEATURE_WEIGHTS[f] for f in features])
    a = np.array([float(vec_a.get(f, 3)) for f in features])
    b = np.array([float(vec_b.get(f, 3)) for f in features])

    numerator = np.sum(w * a * b)
    denom_a = np.sqrt(np.sum(w * a ** 2))
    denom_b = np.sqrt(np.sum(w * b ** 2))

    if denom_a == 0 or denom_b == 0:
        return 0.0

    score = (numerator / (denom_a * denom_b)) * 100
    return round(min(score, 100.0), 1)


def compute_feature_differential(vec_a: dict, vec_b: dict):
    """
    Returns a list of dicts with per-feature comparison info,
    sorted by weighted absolute difference (descending).
    """
    features = list(FEATURE_WEIGHTS.keys())
    diffs = []
    for f in features:
        val_a = float(vec_a.get(f, 3))
        val_b = float(vec_b.get(f, 3))
        diff = abs(val_a - val_b)
        weighted_diff = diff * FEATURE_WEIGHTS[f]
        diffs.append({
            'feature': f,
            'label': FEATURE_LABELS[f],
            'weight': FEATURE_WEIGHTS[f],
            'value_a': val_a,
            'value_b': val_b,
            'diff': diff,
            'weighted_diff': round(weighted_diff, 2),
            'low_label': FEATURE_LOW_LABELS[f],
            'high_label': FEATURE_HIGH_LABELS[f],
        })
    diffs.sort(key=lambda x: x['weighted_diff'], reverse=True)
    return diffs


def get_top_overlaps_and_conflicts(vec_a: dict, vec_b: dict, n=5):
    """
    Returns the top-n overlaps (most similar) and top-n conflicts
    (most different), weighted.
    """
    diffs = compute_feature_differential(vec_a, vec_b)
    conflicts = diffs[:n]
    overlaps = diffs[-n:][::-1] if len(diffs) >= n else list(reversed(diffs))
    # Overlaps are those with the smallest weighted difference
    overlaps = sorted(diffs, key=lambda x: x['weighted_diff'])[:n]
    return overlaps, conflicts


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def rank_users_by_compatibility(query_user, all_users, radius_km=None):
    """
    Given a query user and list of all users, return ranked list with
    compatibility scores and distances.
    """
    query_vec = query_user.get_feature_vector()
    results = []

    for user in all_users:
        if user.id == query_user.id:
            continue
        if not user.is_looking:
            continue

        user_vec = user.get_feature_vector()
        score = compute_compatibility(query_vec, user_vec)

        dist = None
        if query_user.latitude and query_user.longitude and user.latitude and user.longitude:
            dist = round(haversine_distance(
                query_user.latitude, query_user.longitude,
                user.latitude, user.longitude
            ), 1)
            if radius_km and dist > radius_km:
                continue

        results.append({
            'user': user,
            'score': score,
            'distance_km': dist,
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def check_hard_constraints(query_user, candidate_user):
    """Check if hard constraints are satisfied."""
    issues = []

    # Gender preference
    if query_user.gender_preference and query_user.gender_preference != 'any':
        if candidate_user.gender != query_user.gender_preference:
            issues.append(f"Gender mismatch: you prefer {query_user.gender_preference}")

    if candidate_user.gender_preference and candidate_user.gender_preference != 'any':
        if query_user.gender != candidate_user.gender_preference:
            issues.append(f"They prefer {candidate_user.gender_preference} roommate")

    # Smoking compatibility
    if query_user.smoking == 'never' and candidate_user.smoking == 'regularly':
        issues.append("Smoking conflict: you don't smoke, they smoke regularly")
    if candidate_user.smoking == 'never' and query_user.smoking == 'regularly':
        issues.append("Smoking conflict: they don't smoke, you smoke regularly")

    # Budget overlap
    if (query_user.budget_min and candidate_user.budget_max and
            query_user.budget_min > candidate_user.budget_max):
        issues.append("No budget overlap")
    if (candidate_user.budget_min and query_user.budget_max and
            candidate_user.budget_min > query_user.budget_max):
        issues.append("No budget overlap")

    # Pet allergy
    if query_user.pet_friendly and not candidate_user.pet_friendly:
        issues.append("Pet preference mismatch")

    return issues

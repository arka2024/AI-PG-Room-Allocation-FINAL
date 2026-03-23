"""
CohabitAI - Compatibility Scoring Engine
Implements the Weighted Cosine Similarity measure for user matching.
"""

import numpy as np
from math import radians, sin, cos, sqrt, atan2
from sklearn.decomposition import PCA
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.neighbors import NearestNeighbors

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


SCORE_WEIGHTS = {
    'cosine': 0.60,
    'euclidean': 0.25,
    'bio': 0.15,
}


def _feature_keys():
    return list(FEATURE_WEIGHTS.keys())


def _feature_array(vec: dict) -> np.ndarray:
    return np.array([float(vec.get(f, 3)) for f in _feature_keys()], dtype=float)


def compute_weighted_cosine_similarity(vec_a: dict, vec_b: dict) -> float:
    """Weighted cosine similarity in [0, 100]."""
    features = _feature_keys()
    w = np.array([FEATURE_WEIGHTS[f] for f in features], dtype=float)
    a = _feature_array(vec_a)
    b = _feature_array(vec_b)

    numerator = np.sum(w * a * b)
    denom_a = np.sqrt(np.sum(w * a ** 2))
    denom_b = np.sqrt(np.sum(w * b ** 2))

    if denom_a == 0 or denom_b == 0:
        return 0.0

    score = (numerator / (denom_a * denom_b)) * 100
    return round(float(min(score, 100.0)), 1)


def compute_weighted_euclidean_similarity(vec_a: dict, vec_b: dict) -> float:
    """Convert weighted Euclidean distance to similarity score in [0, 100]."""
    features = _feature_keys()
    w = np.array([FEATURE_WEIGHTS[f] for f in features], dtype=float)
    a = _feature_array(vec_a)
    b = _feature_array(vec_b)

    # Features are on a 1-5 scale, so max per-dimension absolute diff is 4.
    dist = np.sqrt(np.sum(w * ((a - b) ** 2)))
    max_dist = np.sqrt(np.sum(w * (4.0 ** 2)))
    if max_dist == 0:
        return 0.0

    score = (1.0 - (dist / max_dist)) * 100.0
    return round(float(max(0.0, min(score, 100.0))), 1)


def compute_bio_similarity(bio_a: str | None, bio_b: str | None) -> float:
    """Compute text similarity for bios in [0, 100] using lightweight TF-IDF."""
    a = (bio_a or "").strip()
    b = (bio_b or "").strip()

    # Neutral prior when one/both bios are missing.
    if not a or not b:
        return 50.0

    try:
        matrix = TfidfVectorizer(stop_words='english').fit_transform([a, b])
        score = float(cosine_similarity(matrix[0], matrix[1])[0][0]) * 100.0
        return round(max(0.0, min(score, 100.0)), 1)
    except Exception:
        return 50.0


def compute_compatibility(vec_a: dict, vec_b: dict, bio_a: str = '', bio_b: str = '') -> float:
    """
    Hybrid compatibility score in [0, 100]:
    - weighted cosine similarity
    - weighted Euclidean similarity
    - bio text similarity

    Falls back safely if bio is unavailable.

    Returns a score in [0, 100].
    """
    cosine_score = compute_weighted_cosine_similarity(vec_a, vec_b)
    euclidean_score = compute_weighted_euclidean_similarity(vec_a, vec_b)
    bio_score = compute_bio_similarity(bio_a, bio_b)

    blended = (
        SCORE_WEIGHTS['cosine'] * cosine_score +
        SCORE_WEIGHTS['euclidean'] * euclidean_score +
        SCORE_WEIGHTS['bio'] * bio_score
    )
    return round(float(max(0.0, min(blended, 100.0))), 1)


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


def build_knn_index(users):
    """Build a cosine KNN index from user feature vectors."""
    if not users:
        return None, [], None

    vectors = np.array([_feature_array(u.get_feature_vector()) for u in users], dtype=float)
    if len(vectors) == 0:
        return None, [], None

    model = NearestNeighbors(metric='cosine')
    model.fit(vectors)
    return model, users, vectors


def analyze_feature_variance(users, n_components=5):
    """
    PCA utility to inspect variance explained by compatibility features.
    Returns dict with explained variance and top loading per component.
    """
    if not users:
        return {'components': 0, 'explained_variance_ratio': [], 'top_features': []}

    matrix = np.array([_feature_array(u.get_feature_vector()) for u in users], dtype=float)
    # Normalize 1-5 scale to 0-1 before PCA.
    matrix = (matrix - 1.0) / 4.0

    k = max(1, min(n_components, matrix.shape[0], matrix.shape[1]))
    pca = PCA(n_components=k)
    pca.fit(matrix)

    feature_names = _feature_keys()
    top_features = []
    for comp in pca.components_:
        idx = int(np.argmax(np.abs(comp)))
        top_features.append(feature_names[idx])

    return {
        'components': k,
        'explained_variance_ratio': [round(float(x), 4) for x in pca.explained_variance_ratio_],
        'cumulative_explained_variance': [round(float(x), 4) for x in np.cumsum(pca.explained_variance_ratio_)],
        'top_features': top_features,
    }


def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points."""
    R = 6371  # Earth radius in km
    dlat = radians(lat2 - lat1)
    dlon = radians(lon2 - lon1)
    a = sin(dlat / 2) ** 2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c


def rank_users_by_compatibility(
    query_user,
    all_users,
    radius_km=None,
    use_knn_prefilter=True,
    knn_k=150,
    knn_trigger_size=250,
):
    """
    Given a query user and list of all users, return ranked list with
    compatibility scores and distances.
    """
    query_vec = query_user.get_feature_vector()
    results = []

    candidate_users = list(all_users)

    # Fast candidate narrowing for larger pools; ranking still uses full hybrid score.
    if use_knn_prefilter and len(candidate_users) >= knn_trigger_size:
        model, users_ref, _ = build_knn_index(candidate_users)
        if model is not None:
            q = _feature_array(query_vec).reshape(1, -1)
            n_neighbors = min(knn_k, len(users_ref))
            try:
                idxs = model.kneighbors(q, n_neighbors=n_neighbors, return_distance=False)[0]
                candidate_users = [users_ref[i] for i in idxs]
            except Exception:
                candidate_users = list(all_users)

    for user in candidate_users:
        if user.id == query_user.id:
            continue
        if not user.is_looking:
            continue

        user_vec = user.get_feature_vector()
        score = compute_compatibility(
            query_vec,
            user_vec,
            bio_a=getattr(query_user, 'bio', ''),
            bio_b=getattr(user, 'bio', ''),
        )

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

"""
CohabitAI - Conversational Guidance Module (Chatbot)
Rule-based system with pattern matching for roommate search assistance.
"""

import re
import random
from compatibility import (
    get_top_overlaps_and_conflicts,
    FEATURE_LABELS,
    FEATURE_LOW_LABELS,
    FEATURE_HIGH_LABELS,
)


# ─── Response Templates ─────────────────────────────────────────
GREETINGS = [
    "Hey there! 👋 I'm your CohabitAI assistant. I can help you find the perfect roommate, optimize your profile, or answer questions about compatibility. What would you like to do?",
    "Welcome to CohabitAI! 🏠 I'm here to help with roommate matching, profile tips, and search advice. How can I assist you today?",
    "Hi! I'm your CohabitAI guide. Ask me about compatibility scores, profile improvements, or roommate search strategies!",
]

PROFILE_TIPS = [
    "📝 **Profile Tip:** Complete all your lifestyle fields (sleep schedule, cleanliness, noise tolerance). These have the highest weights in our compatibility algorithm and dramatically improve match quality.",
    "📝 **Profile Tip:** Be honest about your habits! Stretching the truth on cleanliness or noise tolerance leads to conflicts later. Accurate data = better matches.",
    "📝 **Profile Tip:** Set realistic budget ranges. A wider range gives you more potential matches. You can always negotiate specifics later.",
    "📝 **Profile Tip:** Add your interests! While they don't directly affect compatibility scores, shared hobbies help break the ice with potential roommates.",
    "📝 **Profile Tip:** Update your location on the map for geo-spatial matching. This helps find roommates in your preferred area.",
]

SEARCH_TIPS = [
    "🔍 **Search Tip:** If you're getting low compatibility scores, try expanding your search radius. Great roommates might be just a few km further!",
    "🔍 **Search Tip:** Use the Compare Tool to see exactly where you align and differ with potential matches. Focus on the top conflicts — those are your deal-breakers.",
    "🔍 **Search Tip:** Filter by gender preference and smoking habits first (hard constraints), then sort by compatibility score for the best results.",
    "🔍 **Search Tip:** Don't dismiss scores in the 70-80% range! Perfect matches are rare. Focus on whether the top conflicts are things you can compromise on.",
    "🔍 **Search Tip:** Check the reviews section for candidates. Past roommate experiences are a great predictor of future compatibility.",
]

CONFLICT_DISCUSSION_TEMPLATES = {
    'sleep_schedule': [
        "💡 Since your sleep schedules differ, discuss: What time do you usually go to bed? Would you be okay with headphones after 10 PM?",
        "💡 Sleep schedule mismatch detected. Ask: Are you flexible on weekdays vs weekends? Can you use a sleep mask if lights are on?",
    ],
    'cleanliness': [
        "💡 You have different cleanliness standards. Discuss: How often should common areas be cleaned? Would a cleaning schedule work?",
        "💡 Cleanliness gap found. Key question: What's your definition of 'clean enough'? Can you agree on weekly chore rotation?",
    ],
    'noise_tolerance': [
        "💡 Noise tolerance differs. Discuss: What types of noise bother you most? Would quiet hours (e.g., after 10 PM) work?",
        "💡 Noise sensitivity mismatch. Ask: Do you use headphones for music/calls? How do you feel about TV volume?",
    ],
    'cooking_frequency': [
        "💡 Different cooking habits. Discuss: Would you share cooking duties? How do you handle kitchen cleanup?",
    ],
    'guest_frequency': [
        "💡 Guest frequency differs. Important to discuss: How much notice for overnight guests? Any off-limit days?",
    ],
    'introversion_extroversion': [
        "💡 Personality spectrum differs. Discuss: How much shared social time do you expect? Is it okay to need alone time?",
    ],
    'communication_style': [
        "💡 Communication styles differ. Ask: How do you prefer to handle issues — text, in-person, or a house meeting?",
    ],
    'conflict_resolution': [
        "💡 You handle conflicts differently. Discuss: When something bothers you, do you prefer to address it immediately or cool down first?",
    ],
    'social_battery': [
        "💡 Social energy levels differ. Ask: Do you need quiet evenings to recharge? How do you feel about shared meals?",
    ],
    'workout_habit': [
        "💡 Workout habits differ. Not a major conflict, but discuss: Would early morning alarms for gym be an issue?",
    ],
}

ABOUT_RESPONSES = [
    "🏠 **CohabitAI** uses a Weighted Cosine Similarity algorithm to match you with compatible roommates. We analyze 10 key dimensions including sleep schedule, cleanliness, noise tolerance, and personality traits. Each dimension is weighted by importance — cleanliness and sleep schedule matter most!",
    "📊 Our compatibility score ranges from 0-100%. Scores above 85% indicate excellent compatibility, 70-85% is good with minor adjustments needed, and below 70% may have significant lifestyle conflicts. Use the Compare Tool to understand the specifics!",
]

FAREWELL = [
    "Happy roommate hunting! 🏠 Feel free to come back anytime.",
    "Good luck finding your perfect match! Don't forget to use the Compare Tool before deciding. 👋",
    "See you later! Remember, honest profiles make the best matches. ✨",
]


# ─── Intent Detection ────────────────────────────────────────────
INTENT_PATTERNS = {
    'greeting': r'\b(hi|hello|hey|howdy|sup|good\s*(morning|evening|afternoon)|greet)\b',
    'profile_help': r'\b(profile|improve|complete|update|edit|fill|missing|optimize|tip)\b',
    'search_help': r'\b(search|find|look|discover|match|score|low|result|filter|radius)\b',
    'compare_help': r'\b(compare|comparison|difference|overlap|conflict|versus|vs|heatmap)\b',
    'how_it_works': r'\b(how|algorithm|work|score|calculate|weight|cosine|formula|about|explain)\b',
    'review_help': r'\b(review|rating|rate|feedback|experience|recommend)\b',
    'map_help': r'\b(map|location|area|geo|spatial|nearby|radius|distance|km)\b',
    'budget': r'\b(budget|cost|price|rent|afford|cheap|expensive|money)\b',
    'farewell': r'\b(bye|goodbye|thanks|thank|see\s*you|later|quit|exit)\b',
    'conflict': r'\b(conflict|issue|problem|fight|argue|disagree|tension|incompatible)\b',
}


def detect_intent(message: str) -> str:
    """Detect user intent from message text."""
    message_lower = message.lower().strip()

    for intent, pattern in INTENT_PATTERNS.items():
        if re.search(pattern, message_lower):
            return intent

    return 'unknown'


def generate_response(message: str, user=None, context=None) -> str:
    """Generate a chatbot response based on detected intent and context."""
    intent = detect_intent(message)

    if intent == 'greeting':
        return random.choice(GREETINGS)

    elif intent == 'profile_help':
        response = random.choice(PROFILE_TIPS)
        if user:
            missing = get_missing_fields(user)
            if missing:
                response += f"\n\n⚠️ **Your profile is missing:** {', '.join(missing)}. Completing these will significantly improve your match quality!"
            else:
                response += "\n\n✅ Your profile looks complete! Great job — you'll get the most accurate matches."
        return response

    elif intent == 'search_help':
        return random.choice(SEARCH_TIPS)

    elif intent == 'compare_help':
        response = "📊 **The Compare Tool** lets you select 2-3 potential roommates and see a side-by-side breakdown:\n"
        response += "• **Top 5 Overlaps** — where you're most similar\n"
        response += "• **Top 5 Conflicts** — where you differ most\n"
        response += "• **Weighted Impact** — how much each difference actually matters\n\n"
        response += "Use it from the Search page by selecting candidates and clicking 'Compare'!"
        return response

    elif intent == 'how_it_works':
        return random.choice(ABOUT_RESPONSES)

    elif intent == 'review_help':
        response = "⭐ **Review System:** After living with someone, leave a review rating them on:\n"
        response += "• Overall experience (1-5 stars)\n"
        response += "• Cleanliness, Communication, Respect, Reliability\n\n"
        response += "Reviews help future users make better decisions, and users with good reviews rank higher in search results!"
        return response

    elif intent == 'map_help':
        response = "🗺️ **Geo-Spatial Discovery:** Our map shows potential roommates near you.\n"
        response += "• Set your preferred search radius (1-50 km)\n"
        response += "• Pins are color-coded by compatibility score\n"
        response += "• Click any pin to see their mini-profile and score\n\n"
        response += "Make sure your location is set in your profile for accurate results!"
        return response

    elif intent == 'budget':
        response = "💰 **Budget Matching:** Set your min-max budget range in your profile.\n"
        response += "• We filter out candidates with no budget overlap\n"
        response += "• Wider ranges = more potential matches\n"
        response += "• Budget is a hard constraint — mismatches are flagged automatically."
        return response

    elif intent == 'conflict':
        response = "🤝 **Handling Conflicts:**\n"
        response += "1. Use the **Compare Tool** to identify specific areas of difference\n"
        response += "2. I can generate **discussion prompts** based on your top conflicts\n"
        response += "3. Address potential issues **before** moving in together\n\n"
        response += "Tip: Some conflicts (like sleep schedule) are harder to compromise on than others (like cooking frequency). Focus on the high-weight differences!"
        return response

    elif intent == 'farewell':
        return random.choice(FAREWELL)

    else:
        return (
            "I'm not sure I understand that. Here's what I can help with:\n\n"
            "• **Profile tips** — Ask: 'How can I improve my profile?'\n"
            "• **Search advice** — Ask: 'How do I find better matches?'\n"
            "• **Compare tool** — Ask: 'How does the compare tool work?'\n"
            "• **How it works** — Ask: 'How is compatibility calculated?'\n"
            "• **Reviews** — Ask: 'How do reviews work?'\n"
            "• **Map search** — Ask: 'How does the map work?'\n"
            "• **Budget** — Ask: 'How does budget matching work?'\n"
            "• **Conflicts** — Ask: 'How to handle roommate conflicts?'\n"
        )


def generate_conflict_prompts(vec_a: dict, vec_b: dict, name_b: str = "your match") -> str:
    """Generate pre-move-in discussion prompts based on top conflicts."""
    overlaps, conflicts = get_top_overlaps_and_conflicts(vec_a, vec_b, n=5)

    if not conflicts or conflicts[0]['weighted_diff'] == 0:
        return f"🎉 Great news! You and {name_b} are very well aligned across all dimensions. No major conflicts detected!"

    response = f"📋 **Pre-Move-in Discussion Guide with {name_b}:**\n\n"

    for i, conflict in enumerate(conflicts):
        if conflict['weighted_diff'] < 1.0:
            continue
        feature = conflict['feature']
        templates = CONFLICT_DISCUSSION_TEMPLATES.get(feature, [])
        if templates:
            response += f"**{i+1}. {conflict['label']}** (Difference: {conflict['diff']}/4)\n"
            response += random.choice(templates) + "\n\n"

    if response.endswith(":**\n\n"):
        return f"✅ You and {name_b} have only minor differences. You should be a great fit!"

    return response


def get_missing_fields(user) -> list:
    """Check which critical profile fields are missing/empty."""
    critical_fields = {
        'sleep_schedule': 'Sleep Schedule',
        'cleanliness': 'Cleanliness',
        'noise_tolerance': 'Noise Tolerance',
        'introversion_extroversion': 'Personality Type',
        'budget_min': 'Minimum Budget',
        'budget_max': 'Maximum Budget',
        'smoking': 'Smoking Preference',
        'gender_preference': 'Gender Preference',
        'latitude': 'Location',
    }
    missing = []
    for field, label in critical_fields.items():
        if getattr(user, field, None) is None:
            missing.append(label)
    return missing

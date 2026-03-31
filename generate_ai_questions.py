"""
CohabitAI - AI Question Pool Generator
Uses Gemma 3B to generate a pool of MCQ questions per segment, stores in JSON.
Run this once to generate questions, then they're randomly served to users.
"""

import json
import os
import re
import requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

QUESTIONS_FILE = Path("local_data/ai_questions_pool.json")

SEGMENTS = {
    "sleep_schedule": {
        "label": "Sleep Schedule",
        "left": "Early Bird",
        "right": "Night Owl",
        "context": "Schedule when user sleeps and wakes naturally"
    },
    "cleanliness": {
        "label": "Cleanliness",
        "left": "Relaxed",
        "right": "Very Tidy",
        "context": "How clean and organized user keeps shared spaces"
    },
    "noise_tolerance": {
        "label": "Noise Tolerance",
        "left": "Needs Quiet",
        "right": "Noise-Friendly",
        "context": "How much background noise user can tolerate"
    },
    "cooking_frequency": {
        "label": "Cooking Frequency",
        "left": "Never Cook",
        "right": "Daily Cook",
        "context": "How often user cooks meals at home"
    },
    "guest_frequency": {
        "label": "Guest Frequency",
        "left": "No Guests",
        "right": "Frequent Guests",
        "context": "How often user has friends/family visit"
    },
    "workout_habit": {
        "label": "Workout Habit",
        "left": "Sedentary",
        "right": "Daily Gym",
        "context": "User's exercise and fitness routine"
    },
    "introversion_extroversion": {
        "label": "Introversion / Extroversion",
        "left": "Introvert",
        "right": "Extrovert",
        "context": "User's social energy and how they interact with others"
    },
    "communication_style": {
        "label": "Communication Style",
        "left": "Reserved",
        "right": "Very Open",
        "context": "How openly user expresses thoughts and feelings"
    },
    "conflict_resolution": {
        "label": "Conflict Resolution",
        "left": "Avoidant",
        "right": "Direct",
        "context": "How user handles disagreements and conflicts"
    },
    "social_battery": {
        "label": "Social Battery",
        "left": "Needs Alone Time",
        "right": "Always Social",
        "context": "How much social interaction vs alone time user needs"
    },
}

# MCQ options mapped to 1-5 scores
MCQ_OPTIONS = {
    1: "Strongly Disagree",
    2: "Disagree",
    3: "Neutral",
    4: "Agree",
    5: "Strongly Agree",
}


def _build_generation_prompt(segment_key, segment_info):
    """Build prompt for Gemma to generate MCQ questions."""
    prompt = f"""Generate 5 unique multiple-choice questions about "{segment_info['label']}" for a roommate matching questionnaire.

Context: {segment_info['context']}
Spectrum: {segment_info['left']} (score 1) ←→ {segment_info['right']} (score 5)

Each question should have 5 answer options: 'Strongly Disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly Agree'

Requirements:
- Questions must be clear and concise (max 100 chars)
- Each option maps to 1-5 score (Strongly Disagree=1, Disagree=2, Neutral=3, Agree=4, Strongly Agree=5)
- Questions should help determine where user falls on the {segment_info['left']}-{segment_info['right']} spectrum
- Output ONLY JSON array of 5 questions, no explanation

Example format:
["Question 1 about the topic?", "Question 2 about the topic?", ...]

Generate questions now:"""
    return prompt


def _extract_json_array(text):
    """Extract JSON array from text response."""
    if not text:
        return None
    match = re.search(r'\["[\s\S]*?\]', text)
    if not match:
        return None
    try:
        return json.loads(match.group(0))
    except json.JSONDecodeError:
        return None


def _generate_from_ollama(segment_key, segment_info):
    """Generate questions using local Ollama Gemma model."""
    try:
        ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")
        model = os.getenv("GEMMA_MODEL", "gemma3:4b")
        
        prompt = _build_generation_prompt(segment_key, segment_info)
        
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "top_p": 0.9,
            },
        }
        
        print(f"  Generating from Ollama ({model})...", end=" ")
        response = requests.post(ollama_url, json=payload, timeout=60)
        response.raise_for_status()
        
        body = response.json()
        generated = body.get("response", "")
        questions = _extract_json_array(generated)
        
        if questions and len(questions) >= 5:
            print(f"✓ Got {len(questions)} questions")
            return questions, f"ollama:{model}"
        else:
            print("✗ Invalid format")
            return None, None
            
    except Exception as e:
        print(f"✗ Ollama failed: {e}")
        return None, None


def _generate_from_google(segment_key, segment_info):
    """Generate questions using Google Gemini API."""
    try:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print("  GEMINI_API_KEY not set")
            return None, None
        
        model = os.getenv("GEMINI_MODEL", "gemma-3-4b-it")
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        
        prompt = _build_generation_prompt(segment_key, segment_info)
        
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {
                "temperature": 0.7,
                "topP": 0.9,
            },
        }
        
        print(f"  Generating from Google Gemini ({model})...", end=" ")
        response = requests.post(url, json=payload, timeout=60)
        response.raise_for_status()
        
        data = response.json()
        generated = data["candidates"][0]["content"]["parts"][0].get("text", "")
        questions = _extract_json_array(generated)
        
        if questions and len(questions) >= 5:
            print(f"✓ Got {len(questions)} questions")
            return questions, f"google:{model}"
        else:
            print("✗ Invalid format")
            return None, None
            
    except Exception as e:
        print(f"✗ Google failed: {e}")
        return None, None


def generate_all_questions():
    """Generate question pools for all segments using Gemma 3B."""
    questions_db = {}
    
    print("\n🤖 Generating AI Question Pool using Gemma 3B\n")
    print("=" * 60)
    
    for segment_key, segment_info in SEGMENTS.items():
        print(f"\n[{segment_key}] {segment_info['label']}")
        
        # Try Ollama first
        questions, source = _generate_from_ollama(segment_key, segment_info)
        if questions:
            questions_db[segment_key] = {
                "label": segment_info["label"],
                "source": source,
                "questions": questions[:5],
            }
            continue
        
        # Try Google
        questions, source = _generate_from_google(segment_key, segment_info)
        if questions:
            questions_db[segment_key] = {
                "label": segment_info["label"],
                "source": source,
                "questions": questions[:5],
            }
            continue
        
        print(f"  ✗ Failed to generate questions for {segment_key}")
    
    print("\n" + "=" * 60)
    
    if questions_db:
        QUESTIONS_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(QUESTIONS_FILE, "w", encoding="utf-8") as f:
            json.dump(questions_db, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ Saved {len(questions_db)} segments to {QUESTIONS_FILE}\n")
        return questions_db
    else:
        print("\n❌ No questions generated!\n")
        return {}


if __name__ == "__main__":
    import sys
    questions = generate_all_questions()
    
    if not questions:
        print("⚠️  Question generation failed. Make sure Gemma is available.")
        print("   - Install Ollama: https://ollama.ai")
        print("   - Run: ollama pull gemma3:4b")
        print("   - Or set GEMINI_API_KEY for Google Gemini")
        sys.exit(1)
    
    print(f"📊 Generated {len(questions)} question segments ready for users!")

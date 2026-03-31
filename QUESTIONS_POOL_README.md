# AI Question Pool System

## Overview
The registration questionnaire now uses a **pre-generated question pool** stored in JSON format. Questions are randomly selected for each user during registration, providing variety while maintaining consistent scoring through MCQ answer options.

## File Structure

```
cohabitai/
├── local_data/
│   └── ai_questions_pool.json          # Pre-generated question pool (50 questions total)
├── generate_ai_questions.py             # Script to regenerate pool using Gemma 3B
└── app.py                               # Flask backend with API endpoints
```

## How It Works

### 1. Question Storage (`ai_questions_pool.json`)
- Contains **50 questions total** (5 per segment × 10 segments)
- Questions stored as simple text strings (MCQ format)
- Each segment metadata includes:
  - `label`: Display name
  - `source`: Where questions came from (ollama, google, or local)
  - `questions`: Array of 5 questions

### 2. Random Selection
When users access the registration page:
1. Frontend calls `/api/register-questionnaire`
2. Backend loads JSON file
3. Randomly selects **3 questions per segment**
4. Returns to frontend for rendering as MCQs

Each user gets a **different random subset** of the 50 questions.

### 3. MCQ Scoring
Questions use 5-point Likert scale mapped to compatibility scores:
```
Option 1: Strongly Disagree → Score 1
Option 2: Disagree         → Score 2
Option 3: Neutral          → Score 3
Option 4: Agree            → Score 4
Option 5: Strongly Agree   → Score 5
```

Average score from 3 questions = segment feature value (1-5)

## Regenerating Questions with Gemma 3B

### Option 1: Local Ollama (Recommended)

**Install Ollama:**
```bash
# Download from https://ollama.ai
# Or using Homebrew (Mac): brew install ollama
# Or Windows: Download from ollama.ai
```

**Pull Gemma 3B Model:**
```bash
ollama pull gemma3:4b
```

**Generate questions:**
```bash
python generate_ai_questions.py
```

This will:
- Connect to local Ollama instance (http://localhost:11434)
- Generate 5 new questions per segment
- Save to `local_data/ai_questions_pool.json`

### Option 2: Google Gemini API

**Setup:**
```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key-here"
```

**Generate questions:**
```bash
python generate_ai_questions.py
```

This will:
- Use Google Gemini API (gemma-3-4b-it model by default)
- Generate 5 new questions per segment
- Save to `local_data/ai_questions_pool.json`

### Option 3: Admin API Endpoint

**Trigger regeneration from authenticated admin:**
```bash
curl -X POST http://localhost:5000/api/admin/regenerate-questions \
  -H "Authorization: Bearer <token>"
```

Requires:
- User authentication
- User email in ADMIN_EMAILS environment variable

### Option 4: Manual Edit
Simply edit `local_data/ai_questions_pool.json` and add your own questions in the same format.

## API Reference

### GET `/api/register-questionnaire`
Returns random questions for current registration session.

**Response:**
```json
{
  "source": "json:ai-pool",
  "generated_at": "2026-03-31T10:30:00.000000",
  "segments": [
    {
      "key": "sleep_schedule",
      "label": "Sleep Schedule",
      "group": "lifestyle",
      "impact": "high",
      "left_label": "Early Bird",
      "right_label": "Night Owl"
    },
    ...
  ],
  "questions": {
    "sleep_schedule": [
      "Do you naturally wake up early in the morning?",
      "I prefer going to bed before 10 PM most nights.",
      "My productivity peaks in the early morning hours."
    ],
    ...
  },
  "mcq_options": {
    "1": "Strongly Disagree",
    "2": "Disagree",
    "3": "Neutral",
    "4": "Agree",
    "5": "Strongly Agree"
  }
}
```

### POST `/api/admin/regenerate-questions`
Trigger Gemma 3B generation (admin only).

**Headers:**
```
Authorization: Bearer <token>
```

**Response:**
```json
{
  "status": "success",
  "message": "Generated 10 question segments",
  "segments": [
    "sleep_schedule",
    "cleanliness",
    "noise_tolerance",
    ...
  ]
}
```

## Configuration

Set environment variables in `.env` file:

```bash
# Ollama (Local Gemma)
OLLAMA_URL=http://localhost:11434/api/generate
GEMMA_MODEL=gemma3:4b

# Google Gemini
GEMINI_API_KEY=your-api-key
GEMINI_MODEL=gemma-3-4b-it

# Admin access
ADMIN_EMAILS=admin@example.com,admin2@example.com
```

## Testing

**Verify questions load:**
```bash
curl http://localhost:5000/api/register-questionnaire | jq '.questions | keys'
```

**Check question counts:**
```bash
curl http://localhost:5000/api/register-questionnaire | jq '.questions | map(length)'
```

**View single segment:**
```bash
curl http://localhost:5000/api/register-questionnaire | jq '.questions.sleep_schedule'
```

## Troubleshooting

### JSON file not found
- Ensure `local_data/ai_questions_pool.json` exists
- Run `python generate_ai_questions.py` to create default pool

### Ollama connection failed
- Verify Ollama is running: `ollama serve`
- Check URL in environment: `OLLAMA_URL`
- Pull model: `ollama pull gemma3:4b`

### Google API failed
- Verify API key is set: `echo $GEMINI_API_KEY`
- Check API has quota available
- Ensure model `gemma-3-4b-it` is available

### Questions not loading on registration
- Check browser console for errors
- Verify API returns data: `curl http://localhost:5000/api/register-questionnaire`
- Check Flask logs for exceptions

## Best Practices

1. **Regenerate regularly**: Run generation script weekly to keep questions fresh
2. **Diverse questions**: Gemma generates contextually relevant, varied questions
3. **Backup pool**: Save `ai_questions_pool.json` before regeneration
4. **Monitor diversity**: Ensure different users get different question sets
5. **Track sources**: Keep note of which API generated each pool

## Performance

- **Load time**: < 50ms (reads from JSON)
- **Question generation**: 2-5 minutes (first-time Gemma call)
- **Random selection**: O(n) per request
- **Scalability**: Supports unlimited users simultaneously

## Future Enhancements

- [ ] Dynamic question difficulty levels
- [ ] A/B testing different question sets
- [ ] User feedback on question clarity
- [ ] Admin dashboard for question management
- [ ] Multi-language question support
- [ ] Question versioning and history

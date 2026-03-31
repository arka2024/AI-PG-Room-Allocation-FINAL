#!/bin/bash
# Generate AI Questions Pool using Gemma 3B
# Usage: ./generate_questions.sh

echo "🤖 CohabitAI - Question Pool Generator"
echo "======================================="
echo ""

# Check if Python is available
if ! command -v python &> /dev/null && ! command -v python3 &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

# Use python3 if available, otherwise python
PYTHON_CMD="python"
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
fi

echo "📝 Checking environment..."

# Check .env file
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from .env.example..."
    if [ -f ".env.example" ]; then
        cp .env.example .env
        echo "✓ Created .env from template. Please edit with your settings."
    else
        echo "❌ .env.example not found either."
        exit 1
    fi
fi

echo "✓ .env file ready"
echo ""

echo "🔍 Checking Gemma availability..."
echo ""

# Check Ollama
if command -v ollama &> /dev/null; then
    echo "✓ Ollama found"
    if ollama list | grep -q "gemma3:4b"; then
        echo "✓ Gemma3:4b model installed"
    else
        echo "⚠️  Gemma3:4b not installed"
        echo "   Installing: ollama pull gemma3:4b"
        ollama pull gemma3:4b
    fi
else
    echo "⚠️  Ollama not found. Check GEMMA_API_KEY instead."
fi

echo ""
echo "🚀 Generating questions from Gemma 3B..."
echo ""

# Run the generator
$PYTHON_CMD generate_ai_questions.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Question pool regenerated successfully!"
    echo "📂 Questions saved to: local_data/ai_questions_pool.json"
    echo ""
    echo "📊 Statistics:"
    $PYTHON_CMD -c "
import json
with open('local_data/ai_questions_pool.json') as f:
    pool = json.load(f)
    total = sum(len(seg.get('questions', [])) for seg in pool.values())
    print(f'   Total segments: {len(pool)}')
    print(f'   Total questions: {total}')
    print(f'   Questions per segment: {total // len(pool) if pool else 0}')
"
else
    echo ""
    echo "❌ Question generation failed"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check Ollama is running: ollama serve"
    echo "  2. Check .env has correct GEMINI_API_KEY (if using Google)"
    echo "  3. Verify internet connection for API calls"
    echo ""
    exit 1
fi

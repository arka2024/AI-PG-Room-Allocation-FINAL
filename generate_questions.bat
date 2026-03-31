@echo off
REM Generate AI Questions Pool using Gemma 3B (Windows)
REM Usage: generate_questions.bat

setlocal enabledelayedexpansion

echo 🤖 CohabitAI - Question Pool Generator
echo =====================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8+
    exit /b 1
)

echo 📝 Checking environment...

REM Check .env file
if not exist ".env" (
    echo ⚠️  .env file not found. Copying from .env.example...
    if exist ".env.example" (
        copy .env.example .env
        echo ✓ Created .env from template. Please edit with your settings.
    ) else (
        echo ❌ .env.example not found either.
        exit /b 1
    )
)

echo ✓ .env file ready
echo.

echo 🔍 Checking Gemma availability...
echo.

REM Check for Ollama
where ollama >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Ollama found
    ollama list | findstr "gemma3:4b" >nul 2>&1
    if %errorlevel% equ 0 (
        echo ✓ Gemma3:4b model installed
    ) else (
        echo ⚠️  Gemma3:4b not installed
        echo    Install with: ollama pull gemma3:4b
    )
) else (
    echo ⚠️  Ollama not found. Check GEMINI_API_KEY instead.
)

echo.
echo 🚀 Generating questions from Gemma 3B...
echo.

REM Run the generator
python generate_ai_questions.py

if %errorlevel% equ 0 (
    echo.
    echo ✅ Question pool regenerated successfully!
    echo 📂 Questions saved to: local_data\ai_questions_pool.json
    echo.
    echo 📊 Statistics:
    python -c "
import json
with open('local_data/ai_questions_pool.json') as f:
    pool = json.load(f)
    total = sum(len(seg.get('questions', [])) for seg in pool.values())
    print(f'   Total segments: {len(pool)}')
    print(f'   Total questions: {total}')
    print(f'   Questions per segment: {total // len(pool) if pool else 0}')
"
) else (
    echo.
    echo ❌ Question generation failed
    echo.
    echo Troubleshooting:
    echo   1. Check Ollama is running: ollama serve
    echo   2. Check .env has correct GEMINI_API_KEY (if using Google)
    echo   3. Verify internet connection for API calls
    echo.
    exit /b 1
)

endlocal

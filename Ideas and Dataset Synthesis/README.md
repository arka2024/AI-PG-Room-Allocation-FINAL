# Ideas and Dataset Synthesis

This folder now uses a frontend-aligned synthetic user schema (flat fields) that matches the registration/edit profile forms used in the app.

## Current dataset schema (`odisha_users.json`)

Each record includes:

- `_id`
- `full_name`, `email`, `phone`, `age`, `gender`, `occupation`, `bio`
- `city`, `locality`, `latitude`, `longitude`
- `sleep_schedule`, `cleanliness`, `noise_tolerance`, `cooking_frequency`, `guest_frequency`, `workout_habit`
- `introversion_extroversion`, `communication_style`, `conflict_resolution`, `social_battery`
- `budget_min`, `budget_max`
- `smoking`, `drinking`, `veg_nonveg`, `gender_preference`, `pet_friendly`, `preferred_move_in`
- `interests` (array of strings)
- `avatar_url`, `profile_complete`, `is_looking`

## Scripts

- `migrate_frontend_schema.py`
	- Converts legacy nested synthetic records (`profile/location/preferences/persona_raw`) to the frontend-compatible flat schema.

- `generate_data.py`
	- Generates new synthetic records directly in the frontend-compatible flat schema.

- `validate_data.py`
	- Validates schema completeness, ranges, distributions, and duplicate risk using the frontend-compatible fields.

- `find_matches.py`
	- Runs weighted roommate compatibility matching using the frontend-compatible fields.

## Usage

Run from this directory:

```powershell
python migrate_frontend_schema.py
python validate_data.py
python find_matches.py
```

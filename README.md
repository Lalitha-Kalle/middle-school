# PrepAIR Math Olympiad Studio

An interactive web application for practicing middle school math olympiad problems, now with dynamic question loading from SQLite.

## Setup

### 1. Load Questions into Database

First, populate the SQLite database with questions from the Excel file:

```bash
python upload.py
```

This will:
- Create `olympiad_questions.db` if it doesn't exist
- Load all questions from `Middle_School_Olympiad_Platform_BIDMAS.xlsx`
- Skip duplicates (safe to run multiple times)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask Backend

```bash
python app.py
```

The server will start at `http://127.0.0.1:5000`

### 4. Open in Browser

Open your browser and navigate to:
```
http://127.0.0.1:5000
```

## How It Works

- **Backend (`app.py`)**: Flask server that queries `olympiad_questions.db` and serves data via REST API
  - `/api/exams` - List of all exams
  - `/api/levels?exam=X` - Difficulty levels for an exam
  - `/api/chapters?exam=X&difficulty=Y` - Chapters for exam+level
  - `/api/topics?exam=X&difficulty=Y&chapter=Z` - Topics for exam+level+chapter
  - `/api/questions?exam=X&difficulty=Y&chapter=Z&topic=W` - Questions matching filters
  - `/` - Serves the main HTML app

- **Frontend (`prepair-olympiad-studio.html`)**: Interactive web app that:
  - Fetches questions from the Flask API
  - Allows filtering by exam, difficulty, chapter, topic
  - Provides theory, questions, and solutions
  - Includes an interactive whiteboard for working out problems
  - Tracks XP, streaks, and progress

## Database Schema

The `olympiad_questions.db` SQLite database has a `questions` table with:

| Column | Type | Notes |
|--------|------|-------|
| id | INTEGER | Primary key |
| exam | TEXT | Exam name (AMC 8, JMC, SASMO, etc.) |
| difficulty | TEXT | Level 1, Level 2, Level 3, etc. |
| chapter | TEXT | Topic category (Number Theory, Algebra, etc.) |
| topic | TEXT | Specific topic (Divisibility, Sequences, etc.) |
| question | TEXT | Question stem/problem statement |
| option_a to option_e | TEXT | Multiple choice options |
| solution | TEXT | Solution/working steps |
| source_file | TEXT | Which Excel file it came from |
| loaded_at | DATETIME | When it was loaded |

## Adding New Questions

Edit `Middle_School_Olympiad_Platform_BIDMAS.xlsx` and add rows with the same column headers. Then run:

```bash
python upload.py
```

New questions will be added; existing ones won't be duplicated.

## Troubleshooting

**"Failed to load exams"** - Make sure Flask is running and the database file exists
**Port 5000 in use** - Change `port=5000` in `app.py` to another port
**CORS errors** - Flask-CORS is configured to allow requests from the frontend

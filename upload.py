"""
load_questions.py
-----------------
Loads questions from an Excel file into a SQLite database.

Usage:
    python load_questions.py                          # uses defaults
    python load_questions.py --excel myfile.xlsx      # custom Excel path
    python load_questions.py --db mydb.db             # custom DB path
    python load_questions.py --excel new.xlsx --db questions.db

Behaviour:
    - Creates the database and table if they don't exist yet.
    - Skips rows that are already in the database (no duplicates).
    - Safe to run multiple times — new rows are added, old ones kept.

Duplicate detection key: (Exam, Chapter, Topic, Question)
"""

import sqlite3
import argparse
import os
from pathlib import Path

try:
    import openpyxl
except ImportError:
    raise SystemExit("openpyxl is required. Install it with: pip install openpyxl")


# ── Column name → SQLite column name mapping ──────────────────────────────────
COLUMN_MAP = {
    "Exam":           "exam",
    "Difficulty":     "difficulty",
    "Chapter":        "chapter",
    "Topic":          "topic",
    "Question":       "question",
    "Option A":       "option_a",
    "Option B":       "option_b",
    "Option C":       "option_c",
    "Option D":       "option_d",
    "Option E":       "option_e",
    "Solution":       "solution",
    "Correct Option": "correct_option",
}

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS questions (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    exam            TEXT,
    difficulty      TEXT,
    chapter         TEXT,
    topic           TEXT,
    question        TEXT    NOT NULL,
    option_a        TEXT,
    option_b        TEXT,
    option_c        TEXT,
    option_d        TEXT,
    option_e        TEXT,
    solution        TEXT,
    correct_option  TEXT,
    source_file     TEXT,
    loaded_at       DATETIME DEFAULT (datetime('now'))
);
"""

# Columns used to detect duplicate rows
DUPLICATE_KEY_COLS = ("exam", "chapter", "topic", "question")


def create_table(conn: sqlite3.Connection) -> None:
    conn.execute(CREATE_TABLE_SQL)
    conn.commit()


def row_exists(conn: sqlite3.Connection, row_data: dict) -> bool:
    """Return True if a row with the same duplicate-key values already exists."""
    where_parts = " AND ".join(f"{col} IS ?" for col in DUPLICATE_KEY_COLS)
    values = tuple(row_data.get(col) for col in DUPLICATE_KEY_COLS)
    cur = conn.execute(f"SELECT 1 FROM questions WHERE {where_parts} LIMIT 1", values)
    return cur.fetchone() is not None


def load_excel(excel_path: str, db_path: str) -> None:
    excel_path = Path(excel_path).resolve()
    db_path    = Path(db_path).resolve()

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    print(f"Excel  : {excel_path}")
    print(f"Database: {db_path}")

    wb = openpyxl.load_workbook(excel_path, read_only=True)
    ws = wb.active

    rows_iter = ws.iter_rows(values_only=True)

    # Read header row
    raw_headers = next(rows_iter, None)
    if raw_headers is None:
        raise ValueError("Excel file appears to be empty.")

    headers = [str(h).strip() if h is not None else "" for h in raw_headers]
    unknown = [h for h in headers if h and h not in COLUMN_MAP]
    if unknown:
        print(f"  Warning: unrecognised columns will be ignored: {unknown}")

    conn = sqlite3.connect(db_path)
    create_table(conn)

    inserted = skipped = 0
    filename  = excel_path.name

    insert_sql = """
        INSERT INTO questions
            (exam, difficulty, chapter, topic, question,
             option_a, option_b, option_c, option_d, option_e,
             solution, correct_option, source_file)
        VALUES
            (:exam, :difficulty, :chapter, :topic, :question,
             :option_a, :option_b, :option_c, :option_d, :option_e,
             :solution, :correct_option, :source_file)
    """

    for raw_row in rows_iter:
        # Skip completely empty rows
        if all(v is None for v in raw_row):
            continue

        row_data: dict = {"source_file": filename}
        for col_name, value in zip(headers, raw_row):
            db_col = COLUMN_MAP.get(col_name)
            if db_col:
                row_data[db_col] = str(value).strip() if value is not None else None

        # Must have at least a question
        if not row_data.get("question"):
            skipped += 1
            continue

        if row_exists(conn, row_data):
            skipped += 1
        else:
            conn.execute(insert_sql, row_data)
            inserted += 1

    conn.commit()
    conn.close()
    wb.close()

    print(f"\nDone!")
    print(f"  Inserted : {inserted} new row(s)")
    print(f"  Skipped  : {skipped} row(s) (already exist or empty)")

    total = inserted + skipped
    print(f"  Total processed: {total} data row(s)")


def main() -> None:
    # Default paths: same directory as this script
    script_dir = Path(__file__).parent

    parser = argparse.ArgumentParser(
        description="Load Olympiad questions from Excel into SQLite (no overwrites)."
    )
    parser.add_argument(
        "--excel", "-e",
        default=str(script_dir / "Middle_School_Olympiad_Platform_BIDMAS.xlsx"),
        help="Path to the Excel (.xlsx) file  (default: same folder as script)",
    )
    parser.add_argument(
        "--db", "-d",
        default=str(script_dir / "olympiad_questions.db"),
        help="Path to the SQLite database file (default: same folder as script)",
    )
    args = parser.parse_args()
    load_excel(args.excel, args.db)


if __name__ == "__main__":
    main()
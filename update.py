import pandas as pd
import sqlite3

EXCEL_FILE = "Middle_School_Olympiad_Platform_BIDMAS.xlsx"
DB_FILE = "olympiad_questions.db"

# Read Excel
df = pd.read_excel(EXCEL_FILE)

# Connect to SQLite
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

updated = 0

for _, row in df.iterrows():

    question = str(row["Question"]).strip()
    difficulty = str(row["Difficulty"]).strip()

    cursor.execute(
        """
        UPDATE questions
        SET difficulty = ?
        WHERE question = ?
        """,
        (difficulty, question)
    )

    updated += cursor.rowcount

conn.commit()
conn.close()

print(f"Updated {updated} rows.")
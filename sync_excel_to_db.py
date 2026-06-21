import pandas as pd
import sqlite3

EXCEL_FILE = "Middle_School_Olympiad_Platform_BIDMAS.xlsx"
DB_FILE = "olympiad_questions.db"

# Read Excel file
print("Reading Excel file...")
df = pd.read_excel(EXCEL_FILE)

# Connect to SQLite database
print("Connecting to database...")
conn = sqlite3.connect(DB_FILE)
cursor = conn.cursor()

updated_count = 0
skipped_count = 0

# Iterate through each row in Excel
for idx, row in df.iterrows():
    try:
        question = str(row["Question"]).strip() if pd.notna(row["Question"]) else None

        if not question:
            skipped_count += 1
            continue

        # Get values from Excel
        exam = str(row["Exam"]).strip() if pd.notna(row["Exam"]) else None
        difficulty = str(row["Difficulty"]).strip() if pd.notna(row["Difficulty"]) else None
        chapter = str(row["Chapter"]).strip() if pd.notna(row["Chapter"]) else None
        topic = str(row["Topic"]).strip() if pd.notna(row["Topic"]) else None
        solution = str(row["Solution"]).strip() if pd.notna(row["Solution"]) else None

        # Update database record
        cursor.execute(
            """
            UPDATE questions
            SET exam = ?, difficulty = ?, chapter = ?, topic = ?, solution = ?
            WHERE question = ?
            """,
            (exam, difficulty, chapter, topic, solution, question)
        )

        if cursor.rowcount > 0:
            updated_count += 1
            print(f"Row {idx + 2}: Updated | Exam: {exam} | Topic: {topic}")
        else:
            skipped_count += 1
            print(f"Row {idx + 2}: Skipped (no matching record in DB) | Question: {question[:50]}...")

    except Exception as e:
        print(f"Row {idx + 2}: Error - {str(e)}")
        skipped_count += 1

# Commit changes
conn.commit()
conn.close()

print(f"\n{'='*60}")
print(f"Sync Complete!")
print(f"Total Updated: {updated_count} records")
print(f"Total Skipped: {skipped_count} records")
print(f"{'='*60}")

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

# Update last 8 rows
total_rows = len(df)
start_idx = total_rows - 8  # Last 8 rows
end_idx = total_rows

print(f"\nUpdating last 8 rows (rows {start_idx + 1} to {end_idx})...\n")

for idx in range(start_idx, end_idx):
    try:
        row = df.iloc[idx]
        question = str(row["Question"]).strip() if pd.notna(row["Question"]) else None
        difficulty = str(row["Difficulty"]).strip() if pd.notna(row["Difficulty"]) else None
        exam = str(row["Exam"]).strip() if pd.notna(row["Exam"]) else None

        if not question:
            skipped_count += 1
            continue

        # Update database record
        cursor.execute(
            """
            UPDATE questions
            SET difficulty = ?
            WHERE question = ?
            """,
            (difficulty, question)
        )

        if cursor.rowcount > 0:
            updated_count += 1
            print(f"Row {idx + 1}: Updated | Exam: {exam} | Difficulty: {difficulty}")
        else:
            skipped_count += 1
            print(f"Row {idx + 1}: Skipped (no matching record in DB)")

    except Exception as e:
        print(f"Row {idx + 1}: Error - {str(e)}")
        skipped_count += 1

# Commit changes
conn.commit()
conn.close()

print(f"\n{'='*60}")
print(f"Update Complete!")
print(f"Total Updated: {updated_count} records")
print(f"Total Skipped: {skipped_count} records")
print(f"{'='*60}")

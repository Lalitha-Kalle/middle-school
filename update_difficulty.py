"""
Update database Difficulty column from Excel file
Reads Middle_School_Olympiad_Platform_BIDMAS.xlsx and updates olympiad_questions.db
"""

import pandas as pd
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "olympiad_questions.db"
EXCEL_PATH = Path(__file__).parent / "Middle_School_Olympiad_Platform_BIDMAS.xlsx"

def update_difficulty_from_excel():
    """Read Excel file and update difficulty in database."""

    try:
        # Read Excel file
        print("📖 Reading Excel file...")
        df = pd.read_excel(EXCEL_PATH)

        # Display columns to understand structure
        print(f"\n📋 Excel columns: {list(df.columns)}")
        print(f"📊 Total rows in Excel: {len(df)}")

        # Connect to database
        print("\n🔗 Connecting to database...")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Get database structure
        cursor.execute("PRAGMA table_info(questions)")
        columns = cursor.fetchall()
        db_columns = [col[1] for col in columns]
        print(f"📋 Database columns: {db_columns}")

        # Check if difficulty column exists
        if 'difficulty' not in db_columns:
            print("❌ Error: 'difficulty' column not found in database")
            return

        # Update rows with difficulty from Excel
        updated_count = 0

        for idx, row in df.iterrows():
            # Identify row by question text or ID
            question_text = row.get('question') or row.get('Question') or row.get('stem')
            exam = row.get('exam') or row.get('Exam')
            chapter = row.get('chapter') or row.get('Chapter')
            new_difficulty = row.get('difficulty') or row.get('Difficulty')

            if not question_text or not new_difficulty:
                continue

            # Update database
            try:
                if exam and chapter:
                    cursor.execute(
                        "UPDATE questions SET difficulty = ? WHERE exam = ? AND chapter = ? AND question LIKE ?",
                        (new_difficulty, exam, chapter, f"%{question_text[:50]}%")
                    )
                else:
                    cursor.execute(
                        "UPDATE questions SET difficulty = ? WHERE question LIKE ?",
                        (new_difficulty, f"%{question_text[:50]}%")
                    )

                if cursor.rowcount > 0:
                    updated_count += cursor.rowcount
                    print(f"✅ Updated row {idx + 1}: {new_difficulty}")
            except Exception as e:
                print(f"⚠️ Error updating row {idx + 1}: {e}")

        # Commit changes
        conn.commit()
        conn.close()

        print(f"\n🎉 Success! Updated {updated_count} records")

    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

def verify_updates():
    """Verify the updates in database."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Show sample of updated data
        print("\n📊 Sample of updated data:")
        cursor.execute("SELECT exam, chapter, question, difficulty FROM questions LIMIT 5")
        rows = cursor.fetchall()

        for row in rows:
            print(f"  Exam: {row[0]}, Chapter: {row[1]}, Difficulty: {row[3]}")

        # Show difficulty distribution
        print("\n📈 Difficulty distribution:")
        cursor.execute("SELECT difficulty, COUNT(*) FROM questions GROUP BY difficulty")
        stats = cursor.fetchall()

        for diff, count in stats:
            print(f"  {diff}: {count} questions")

        conn.close()

    except Exception as e:
        print(f"❌ Verification error: {e}")

if __name__ == "__main__":
    print("="*50)
    print("🔄 DIFFICULTY UPDATE SCRIPT")
    print("="*50)

    update_difficulty_from_excel()
    verify_updates()

    print("\n" + "="*50)
    print("✨ Done!")
    print("="*50)

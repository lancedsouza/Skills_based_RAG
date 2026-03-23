import csv
import os
from app.database import SessionLocal
from app.embedding import get_embedding
from app.models import Skill

# Ensure this path is correct relative to the 'backend' folder
CSV_PATH = "app/data/skills_en.csv" 
BATCH_SIZE = 50

def load_esco():
    db = SessionLocal()
    inserted = 0

    if not os.path.exists(CSV_PATH):
        print(f"❌ ERROR: File not found at {CSV_PATH}")
        return

    try:
        # 'utf-8-sig' handles hidden characters (BOM) often added by Excel
        with open(CSV_PATH, newline='', encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)
            
            # DEBUG: Print the headers to see exactly what Python reads
            print(f"🔍 CSV Headers found: {reader.fieldnames}")

            for i, row in enumerate(reader):
                # DEBUG: Print the first 3 rows to verify data structure
                if i < 3:
                    print(f"Row {i} sample: {row}")

                # 1. Try 'ext' (from your snippet) OR 'preferredLabel' (from ESCO)
                name = (row.get("Text") or row.get("preferredLabel") or "").strip()

                # 2. Check the Label (only if it exists in your CSV)
                label = str(row.get("Label", "1")).strip() # Defaults to '1' if missing

                if not name or label != "1":
                    continue

                # 3. Check for duplicates
                existing = db.query(Skill).filter(Skill.name == name).first()
                if existing:
                    continue

                # 4. Process Embedding
                try:
                    print(f"🚀 Embedding: {name}")
                    embedding = get_embedding(name)
                    db.add(Skill(name=name, embedding=embedding))
                    inserted += 1
                except Exception as e:
                    print(f"⚠️ Failed embedding for '{name}': {e}")
                    continue

                if inserted % BATCH_SIZE == 0:
                    db.commit()
                    print(f"✅ {inserted} skills committed to DB")

        db.commit()
        print(f"🏁 Finished. Total inserted: {inserted}")

    except Exception as e:
        db.rollback()
        print(f"🔥 Critical Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    load_esco()
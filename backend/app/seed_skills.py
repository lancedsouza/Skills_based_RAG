from .database import SessionLocal
from .embedding import get_embedding
from .crud import create_skill
import time

skills = [
    "Supply Chain Management",
    "Logistics Management",
    "Inventory Planning",
    "Demand Forecasting",
    "Procurement",
    "Warehouse Management"
]

BATCH_SIZE = 3  # for demo; use 200–300 in real case

def seed():
    db = SessionLocal()
    
    try:
        for i, skill in enumerate(skills, start=1):
            print(f"Processing: {skill}")

            emb = get_embedding(skill)
            create_skill(db, skill, emb)

            if i % BATCH_SIZE == 0:
                db.commit()
                print("Batch committed")

        db.commit()
        print("Seeding completed")

    except Exception as e:
        db.rollback()
        print("Error occurred:", e)

    finally:
        db.close()


if __name__ == "__main__":
    seed()
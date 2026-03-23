import requests
import os
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Skill
from app.embedding import get_embedding

API_KEY = os.getenv("SHARP_API_KEY")

HEADERS = {
    "Authorization": f"Bearer {API_KEY}"
}

BASE_URL = "https://sharpapi.com/api/v1/utilities/skills_list"

BATCH_SIZE = 100


def load_skills():
    db: Session = SessionLocal()
    page = 1
    total_inserted = 0

    try:
        while True:
            print(f"Fetching page {page}...")

            response = requests.get(
                BASE_URL,
                headers=HEADERS,
                params={
                    "include_related": "true",
                    "page": page
                }
            )

            if response.status_code != 200:
                raise Exception(response.text)

            data = response.json()

            if not data:
                print("No more pages.")
                break

            for skill in data:
                name = skill["name"].strip()

                existing = db.query(Skill).filter(Skill.name == name).first()
                if existing:
                    continue

                embedding = get_embedding(name)

                db.add(Skill(name=name, embedding=embedding))
                total_inserted += 1

                if total_inserted % BATCH_SIZE == 0:
                    db.commit()
                    print(f"{total_inserted} skills committed")

            db.commit()
            page += 1

        print(f"Finished. Total inserted: {total_inserted}")

    except Exception as e:
        db.rollback()
        print("Error:", e)

    finally:
        db.close()


if __name__ == "__main__":
    load_skills()
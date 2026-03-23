from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from .database import SessionLocal, engine, Base
from .embedding import get_embedding
from fastapi.middleware.cors import CORSMiddleware
from .schemas import SuggestResponse, SkillResponse
from .crud import hybrid_search_skills
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/suggest", response_model=SuggestResponse)
def suggest(query: str, limit: int = 10, db: Session = Depends(get_db)):

    embedding = get_embedding(query)

    rows = hybrid_search_skills(db, query, embedding, limit)

    suggestions = [
        SkillResponse(
            id=row[0],
            name=row[1],
            similarity=float(row[2])
        )
        for row in rows
    ]

    return SuggestResponse(suggestions=suggestions)

# -----------------------------------------------------------------------
# Multi-Skill Search
from typing import List
from fastapi import Body
from .crud import search_multiple_skills
from .embedding import get_embedding

@app.post("/multi-skill-search")
def multi_skill_search(skills: List[str] = Body(...), db: Session = Depends(get_db)):
    embeddings = [get_embedding(skill) for skill in skills]
    results = search_multiple_skills(db, embeddings)

    return {
        "input_skills": skills,
        "results": [
            {
                "id": r[0],          # Changed from r.id
                "name": r[1],        # Changed from r.name
                "similarity": float(r[2]) # Changed from r.similarity
            }
            for r in results
        ]
    }
from sqlalchemy.orm import Session
from sqlalchemy import text
from .models import Skill, JobRole


# -------------------------------
# SKILL CRUD
# -------------------------------

def create_skill(db: Session, name: str, embedding):

    skill = Skill(
        name=name,
        embedding=embedding
    )

    db.add(skill)
    return skill


def get_skill_by_name(db: Session, name: str):
    return db.query(Skill).filter(Skill.name == name).first()


# -------------------------------
# VECTOR SEARCH
# -------------------------------

def search_similar(db: Session, embedding, limit: int = 10):

    # Convert Python list → pgvector format
    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    # Tune HNSW recall
    db.execute(text("SET hnsw.ef_search = 60;"))

    query = text("""
        SELECT id, name,
        1 - (embedding <=> :embedding) AS similarity
        FROM skills
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    result = db.execute(query, {
        "embedding": embedding_str,
        "limit": limit
    })

    return result.fetchall()


# -------------------------------
# JOB ROLE CRUD
# -------------------------------

def create_job_role(db: Session, title: str, embedding, api_score: float):

    role = JobRole(
        title=title,
        embedding=embedding,
        api_score=api_score
    )

    db.add(role)
    return role


def search_similar_roles(db: Session, embedding, limit: int = 10):

    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    db.execute(text("SET hnsw.ef_search = 60;"))

    query = text("""
        SELECT id, title,
        1 - (embedding <=> :embedding) AS similarity,
        api_score
        FROM job_roles
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    result = db.execute(query, {
        "embedding": embedding_str,
        "limit": limit
    })

    return result.fetchall()

    # -----------------------------------------------------------------------------------
    # Htbrid search example (combining vector similarity + API score)from sqlalchemy import text

def hybrid_search_skills(db: Session, query_text: str, embedding, limit: int = 10):

    embedding_str = "[" + ",".join(map(str, embedding)) + "]"

    tokens = query_text.lower().split()

    token1 = f"%{tokens[0]}%" if len(tokens) > 0 else "%"
    token2 = f"%{tokens[1]}%" if len(tokens) > 1 else "%"

    full_phrase = f"%{query_text}%"

    db.execute(text("SET hnsw.ef_search = 80;"))

    query = text("""
        SELECT id, name,
        (
            CASE WHEN name ILIKE :full_phrase THEN 1.0 ELSE 0 END * 0.5
            +
            CASE WHEN name ILIKE :token1 THEN 0.25 ELSE 0 END
            +
            CASE WHEN name ILIKE :token2 THEN 0.25 ELSE 0 END
            +
            (1 - (embedding <=> :embedding)) * 0.4
        ) AS final_score
        FROM skills
        WHERE (1 - (embedding <=> :embedding)) > 0.50
        ORDER BY final_score DESC
        LIMIT :limit
    """)

    result = db.execute(query, {
        "embedding": embedding_str,
        "full_phrase": full_phrase,
        "token1": token1,
        "token2": token2,
        "limit": limit
    })

    return result.fetchall()

# -----------------------------------------------------------------------------------
# Multi-skill search example (averaging embeddings of multiple skills)

import numpy as np
from sqlalchemy import text
from sqlalchemy.orm import Session

def search_multiple_skills(db: Session, embeddings, limit: int = 20):

    avg_embedding = np.mean(embeddings, axis=0)

    embedding_str = "[" + ",".join(map(str, avg_embedding)) + "]"

    query = text("""
        SELECT id, name,
        1 - (embedding <=> :embedding) AS similarity
        FROM skills
        ORDER BY embedding <=> :embedding
        LIMIT :limit
    """)

    result = db.execute(query, {
        "embedding": embedding_str,
        "limit": limit
    })

    return result.fetchall()
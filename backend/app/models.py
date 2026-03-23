from sqlalchemy import Column, Integer, String, Float
from pgvector.sqlalchemy import Vector
from .database import Base


class Skill(Base):

    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True)

    embedding = Column(Vector(1024))


class JobRole(Base):

    __tablename__ = "job_roles"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)

    embedding = Column(Vector(1024))

    api_score = Column(Float)
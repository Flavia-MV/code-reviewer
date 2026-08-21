from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy import Float

import enum

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    github_id = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=False)
    email = Column(String, nullable=True)
    avatar_url = Column(String, nullable=True)
    access_token = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    repos = relationship("Repo", back_populates="owner")


class IndexStatus(str, enum.Enum):
    pending = "pending"
    indexing = "indexing"
    ready = "ready"
    failed = "failed"


class Repo(Base):
    __tablename__ = "repos"

    id = Column(Integer, primary_key=True, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    full_name = Column(String, nullable=False)
    default_branch = Column(String, default="main")
    index_status = Column(Enum(IndexStatus), default=IndexStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    owner = relationship("User", back_populates="repos")
    files = relationship("RepoFile", back_populates="repo")


class RepoFile(Base):
    __tablename__ = "repo_files"

    id = Column(Integer, primary_key=True, index=True)
    repo_id = Column(Integer, ForeignKey("repos.id"), nullable=False)
    path = Column(String, nullable=False)
    language = Column(String, nullable=True)
    content = Column(Text, nullable=True)
    sha = Column(String, nullable=True)

    repo = relationship("Repo", back_populates="files")
    chunks = relationship("CodeChunk", back_populates="file")

class CodeChunk(Base):
    __tablename__ = "code_chunks"
    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("repo_files.id"), nullable=False)
    content = Column(Text, nullable=False)
    chunk_type = Column(String, nullable=True)
    name = Column(String, nullable=True)
    start_line = Column(Integer, nullable=False)
    end_line = Column(Integer, nullable=False)
    embedding = Column(ARRAY(Float), nullable=True)

    file = relationship("RepoFile", back_populates="chunks")
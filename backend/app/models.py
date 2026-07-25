from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
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
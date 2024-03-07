from __future__ import annotations
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column


class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    clerk_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    portfolio: Mapped[List["Portfolio"]] = relationship(back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    mongo_id = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    owner = relationship("User", back_populates="portfolio")
    project: Mapped[List["Project"]] = relationship(back_populates="portfolio")

class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True)
    repository_url = Column(String, index=True)
    title = Column(String, index=True)
    description = Column(String, index=True)
    duration = Column(String, index=True)
    skill = Column(JSON, default=[])
    gpt_data = Column(JSON, default=[]) # gpt 결과
    document_url = Column(String, index=True) # 문서(블로그) url
    portfolio_id: Mapped[int] = mapped_column(ForeignKey("portfolios.id"))
    portfolio = relationship("Portfolio", back_populates="project")

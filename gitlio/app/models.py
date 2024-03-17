from __future__ import annotations
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'user'
    user_id = Column('userId', Integer, primary_key=True, index=True, autoincrement=True)
    clerk_id = Column('clerkId', String(255), unique=True, index=True)
    email = Column('email', String(255))
    name = Column('name', String(255))
    
    # Establishing the relationship to Portfolio and Repository
    portfolios = relationship("Portfolio", back_populates="user")
    repositories = relationship("Repository", back_populates="user")


class Portfolio(Base):
    __tablename__ = 'portfolio'
    portfolio_id = Column('portfolioId', Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column('userId', Integer, ForeignKey('user.userId'))
    title = Column('title', String(255))
    mongo_id = Column('mongoId', String(255))
    domain_name = Column('domainName', String(255))
    deployed = Column('deployed', Boolean)
    updated_at = Column('updatedAt', DateTime, onupdate=func.now())
    created_at = Column('createdAt', DateTime, default=func.now())
    
    # Establishing the relationship to User
    user = relationship("User", back_populates="portfolios")


class Repository(Base):
    __tablename__ = 'repository'
    repository_id = Column('repositoryId', Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column('userId', Integer, ForeignKey('user.userId'))
    repository_url = Column('repositoryUrl', String(255))
    main_image = Column('mainImage', String(255))
    user_data = Column('userData', JSON)
    gpt_result = Column('gptResult', JSON)
    
    # Establishing the relationship to User
    user = relationship("User", back_populates="repositories")

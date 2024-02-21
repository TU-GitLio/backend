from __future__ import annotations
from typing import List

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from ..database import Base

class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(primary_key=True)
    email = Column(String, unique=True, index=True)
    is_active = Column(Boolean, default=True)
    portfolio: Mapped[List["Portfolio"]] = relationship(back_populates="user")

class Portfolio(Base):
    __tablename__ = "portfolios"

    id = Column(Integer, primary_key=True)
    mongo_id = Column(String, index=True)
    title = Column(String)
    description = Column(String)
    owner_id: Mapped[String] = mapped_column(ForeignKey("users.id"))

    user: Mapped["User"] = relationship(back_populates="portfolios")
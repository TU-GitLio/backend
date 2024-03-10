from sqlalchemy.orm import Session
from ..models import User, Portfolio
from .. import schemas

def get_user(db: Session, user_id: int):
    return db.query(User).filter(User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(User).offset(skip).limit(limit).all()

def create_user(db: Session, user: schemas.UserCreate):
    db_user = User(email=user.email, id=user.id)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_portfolios(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Portfolio).offset(skip).limit(limit).all()

def create_user_portfolio(db: Session, portfolio: schemas.PortfolioCreate, user_id: str):
    db_portfolio = Portfolio(**portfolio.dict(), owner_id=user_id)
    db.add(db_portfolio)
    db.commit()
    db.refresh(db_portfolio)
    return db_portfolio
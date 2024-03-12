from ...models import User, Portfolio
from sqlalchemy.orm import Session
from sqlalchemy import select
from .user_schema import UserCreateRequest, UserCreateResponse, UserPortfolio
from ..portfolio.portfolio_schema import PortfolioModel

def get_user_data_by_clerk(db: Session, clerk_id: str):
    user_portfolio_query = select(
    User.user_id, User.clerk_id, User.email, User.name,
    Portfolio.portfolio_id, Portfolio.title, Portfolio.mongo_id,
    Portfolio.domain_name, Portfolio.deployed, Portfolio.updated_at, Portfolio.created_at
    ).join(Portfolio, User.user_id == Portfolio.user_id).where(User.clerk_id == clerk_id)
    result = db.execute(user_portfolio_query).fetchall()
    
    if not result:
        return None
    
    # 사용자 정보 및 포트폴리오 데이터를 분리하여 처리
    user_info = result[0][:4]  # 처음 4개 필드는 사용자 정보
    portfolios = [
        PortfolioModel(
            portfolio_id=row[4],
            title=row[5],
            mongo_id=row[6],
            domain_name=row[7],
            deployed=row[8],
            updated_at=row[9],
            created_at=row[10]
        ) for row in result
    ]

    #UserPortfolio 모델로 데이터 조합
    user_response = UserPortfolio(
        user_id=user_info[0],
        clerk_id=user_info[1],
        email=user_info[2],
        name=user_info[3],
        portfolio=portfolios if portfolios else None
    )

    return user_response

def get_user_by_clerk(db: Session, user: UserCreateResponse):
    _user = db.query(User).filter(User.clerk_id==user.clerk_id).first()

    if not _user:
        db_user = User(clerk_id=user.clerk_id, email=user.email, name=user.name)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return { "user": db_user, "created": True}

    
    return {"user": _user, "created": False}


def create_user(db: Session, user: UserCreateRequest):
    db_user = User(clerk_id=user.clerk_id, email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return { "user": db_user, "created": True}
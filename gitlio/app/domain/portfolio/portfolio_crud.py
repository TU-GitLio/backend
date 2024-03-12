from sqlalchemy.orm import Session
from ...models import Portfolio
from ...config.mongo import portfolios_collection

def create_portfolio(db: Session, portfolio_data):

    mongo_document = {
        "title": portfolio_data.title,
        "domain_name": portfolio_data.domainName,
        "portfolio_data": None
    }
    result = portfolios_collection.insert_one(mongo_document)
    mongo_id = result.inserted_id

    new_portfolio = Portfolio(
        user_id=portfolio_data.userId,
        title=portfolio_data.title,
        domain_name=portfolio_data.domainName,
        mongo_id=str(mongo_id),
        deployed=False,  # 초기 상태는 비배포로 설정
    )
    db.add(new_portfolio)
    db.commit()
    db.refresh(new_portfolio)
    return new_portfolio

def get_portfolio_by_domain_name(db: Session, domain_name: str):
    return db.query(Portfolio).filter(Portfolio.domain_name == domain_name).first()
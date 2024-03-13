from fastapi import APIRouter, Depends, Response, status, HTTPException
from sqlalchemy.orm import Session

from . import portfolio_crud, portfolio_schema
from ...database import get_db

router = APIRouter(
    prefix="/api/portfolios"
)

@router.post("/")
def create_portfolio_endpoint(portfolio_data: portfolio_schema.PortfolioCreate, db: Session = Depends(get_db)):
    # 도메인 이름 중복 체크
    db_portfolio = portfolio_crud.get_portfolio_by_domain_name(db, portfolio_data.domainName)
    if db_portfolio:
        raise HTTPException(status_code=409, detail="Domain name already in use")
    
    # 새 포트폴리오 생성 및 저장
    return portfolio_crud.create_portfolio(db, portfolio_data)
from pydantic import BaseModel
from datetime import datetime

# Portfolio 모델 정의
class PortfolioModel(BaseModel):
    portfolio_id: int
    title: str
    mongo_id: str
    domain_name: str
    deployed: bool
    updated_at: datetime
    created_at: datetime
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class PortfolioCreate(BaseModel):
    user_id: int
    title: str
    domain_name: str

# Portfolio 모델 정의
class PortfolioModel(BaseModel):
    portfolio_id: int
    title: str
    mongo_id: Optional[str] = None  # `None`을 기본값으로 사용하거나, Optional 표시
    domain_name: str
    deployed: bool
    updated_at: Optional[datetime] = None  # 여기도 마찬가지로 `None` 허용
    created_at: datetime
from pydantic import BaseModel, Json
from typing import List, Optional
from ..portfolio import portfolio_schema


class UserCreateRequest(BaseModel):
    clerk_id: str
    email: str
    name: str

class UserCreateResponse(BaseModel):
    user_id: int
    clerk_id: str
    email: str
    name: str
    

class UserPortfolio(UserCreateResponse):
    portfolio: Optional[List[portfolio_schema.PortfolioModel]] = None


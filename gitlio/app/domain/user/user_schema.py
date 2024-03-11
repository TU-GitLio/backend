from pydantic import BaseModel, Json
from typing import List, Optional


class UserCreateRequest(BaseModel):
    clerk_id: str
    email: str
    name: str

class UserCreateResponse(BaseModel):
    user_id: int
    clerk_id: str
    portfolio: Optional[List[Json]] = None
from pydantic import BaseModel

class PortfolioBase(BaseModel):
    title: str
    description: str | None = None

class PortfolioCreate(PortfolioBase):
    mongo_id: str
    pass

class Portfolio(PortfolioBase):

    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    email: str

class UserCreate(UserBase):
    id: str

class User(UserBase):
    is_active: bool
    portfolio: list[Portfolio] = []


    class Config:
        orm_mode = True
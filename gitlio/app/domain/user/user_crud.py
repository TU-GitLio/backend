from ...models import User
from sqlalchemy.orm import Session
from .user_schema import UserCreateRequest

def get_user_by_clerk(db: Session, clerk_id: str):
    return db.query(User).filter(User.clerk_id == clerk_id).first()

def create_user(db: Session, user: UserCreateRequest):
    db_user = User(clerk_id=user.clerk_id, email=user.email, name=user.name)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user
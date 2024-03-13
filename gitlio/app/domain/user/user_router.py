from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.orm import Session

from . import user_schema, user_crud
from ...database import get_db

router = APIRouter(
    prefix="/api/users"
)

@router.post("/", response_model=user_schema.UserCreateResponse, status_code=201)
def create_user(user: user_schema.UserCreateRequest, response: Response, db: Session = Depends(get_db)):
    _user = user_crud.get_user_by_clerk(db, user)
    user_data = _user["user"]

    user_response = user_schema.UserCreateResponse( 
        user_id=user_data.user_id,
        clerk_id=user_data.clerk_id,
        email=user_data.email,
        name=user_data.name
    )

    if not _user["created"]:
        #존재하니까 200 리턴
        response.status_code = status.HTTP_200_OK
        return user_response
    
    return user_response
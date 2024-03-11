from fastapi import APIRouter, Depends, Response, status
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import user_schema, user_crud
from ...database import get_db
import requests
from typing import Optional
from urllib.parse import urlparse

router = APIRouter(
    prefix="/api/users"
)

@router.post("/", response_model=user_schema.UserCreateResponse, status_code=201)
def create_user(user: user_schema.UserCreateRequest, response: Response, db: Session = Depends(get_db)):
    _user = user_crud.get_user_by_clerk(db, clerk_id = user.clerk_id)

    if _user:
        #존재하니까 존재하는 포트폴리오 가져오고 리턴
        response.status_code = status.HTTP_200_OK
        return

    _user = user_crud.create_user(db, user)
    
    user_response = user_schema.UserCreateResponse(
        user_id=_user.user_id,
        clerk_id=_user.clerk_id,
    )
    
    return user_response
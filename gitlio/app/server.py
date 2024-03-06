from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.responses import RedirectResponse
from langchain_openai import ChatOpenAI
from langserve import add_routes
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .repository import user_repository

from .models import Base

from . import schemas
from .database import engine, get_db

from .domain.project import project_router
Base.metadata.create_all(bind=engine)   # FastAPI 실행시 필요한 테이블 모두 생성


app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)


templates = Jinja2Templates(directory="templates")

@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

@app.get("/template/{name}", response_class=HTMLResponse)
async def read_item(request: Request, name: str):
    return templates.TemplateResponse(
        request=request, name="hello.html", context={"name": name}
)

@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = user_repository.get_user_by_email(db, email=user.email)

    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return user_repository.create_user(db=db, user=user)


@app.get("/users/", response_model=list[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = user_repository.get_users(db, skip=skip, limit=limit)
    return users


app.include_router(project_router.router)

add_routes(
    app,
    ChatOpenAI(),
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

import shutil
import os
from fastapi import FastAPI, Request, Depends, HTTPException, UploadFile, File, Response
from fastapi.responses import RedirectResponse
from langchain.chat_models import ChatAnthropic, ChatOpenAI
from langserve import add_routes
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from .repository import user_repository
from .service import user_service

from .model.models import Base
from .config.mongo import client
import boto3

from . import schemas

from .database import SessionLocal, engine

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="LangChain Server",
    version="1.0",
    description="Spin up a simple api server using Langchain's Runnable interfaces",
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

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

@app.post("/profile/")
async def update_profile(response: Response, clerk_id: str, profile_picture: UploadFile = File(...)):
    with open(f"{profile_picture.filename}", "wb") as buffer:
        shutil.copyfileobj(profile_picture.file, buffer)

    result = user_service.upload_profile(clerk_id, profile_picture.filename)
    os.remove(profile_picture.filename)
    if not result:
        response.status_code = 400
        return {"message": "Failed to upload profile picture"}
    return {"message": "Profile picture uploaded successfully"}


add_routes(
    app,
    ChatOpenAI(),
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

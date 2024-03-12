import shutil
import os
from fastapi import FastAPI, Request, UploadFile, File, Response
from fastapi.responses import RedirectResponse
from langchain_openai import ChatOpenAI
from langserve import add_routes
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from .service import user_service

from .models import Base
from .config.mongo import client

from .database import engine

from .domain.project import project_router
from .domain.user import user_router
from .domain.portfolio import portfolio_router
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


app.include_router(project_router.router)
app.include_router(user_router.router)
app.include_router(portfolio_router.router)

add_routes(
    app,
    ChatOpenAI(),
    path="/openai",
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)

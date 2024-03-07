from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import project_schema, project_crud
from ...database import get_db
import requests
from typing import Optional
from urllib.parse import urlparse

router = APIRouter(
    prefix="/api/projects"
)


@router.get("/list")
def project_list(db: Session = Depends(get_db)):
    _project_list = project_crud.get_project_list(db)
    return _project_list


@router.get("/gpt", response_model=project_schema.ProjectGpt)
def project_gpt(repo_url: Optional[str] = None) -> JSONResponse:
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")

    # GitHub 레포지토리 URL 파싱
    parsed_url = urlparse(repo_url)
    path_segments = parsed_url.path.strip("/").split("/")
    if len(path_segments) != 2:
        raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

    user, repo = path_segments

    url = f"https://api.github.com/repos/{user}/{repo}/commits"
    response = requests.get(url)

    if response.status_code != 200:
        # GitHub API 호출 실패시 에러 응답 반환
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch commits from GitHub API")

    commits = response.json()
    commit_messages = [commit['commit']['message'] for commit in commits]

    # GPTContents 모델에 맞게 데이터 조합
    gpt_contents = project_schema.ProjectGpt(
        repository_url=f"https://github.com/{user}/{repo}",
        gpt_data=commit_messages,
        status=True
    )
    return JSONResponse(content={
        "message": "성공",
        "data": gpt_contents.dict()
    }, status_code=200)


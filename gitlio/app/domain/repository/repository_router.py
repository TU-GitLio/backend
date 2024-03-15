import base64

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import repository_schema, repository_crud
from ...database import get_db
import requests
from typing import List
from urllib.parse import urlparse

router = APIRouter(
    prefix="/api/repositories"
)

# GitHub Personal Access Token
token = '토큰'
headers = {
    'Authorization': f'token {token}',
}


@router.get("/list")
def repository_list(db: Session = Depends(get_db)):
    _repository_list = repository_crud.get_repository_list(db)
    return _repository_list


# 커밋 기록 반환
def get_commit(user: str, repo: str):
    commit_url = f"https://api.github.com/repos/{user}/{repo}/commits"
    response = requests.get(commit_url, headers=headers)

    if response.status_code == 200:
        commits = response.json()
        commit_messages = [commit['commit']['message'] for commit in commits]
        return commit_messages
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to fetch commits from GitHub API")


# 패키지 파일 찾기
def find_package_file(user: str, repo: str, path: str, target_files: list):
    package_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    response = requests.get(package_url, headers=headers)

    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item['type'] == 'file' and item['name'] in target_files:
                print(f"이게 찐이다!!!", item['path'])
                return item['path']
            elif item['type'] == 'dir':
                # 하위 디렉토리를 재귀적으로 탐색
                found_path = find_package_file(user, repo, item['path'], target_files)
                if found_path:
                    return found_path
    elif response.status_code == 404:
        print(f"{path} not found in the repository.")


# 패키지 파일 내용 반환
def get_package_contents(user: str, repo: str, path: str):
    package_url = f"https://api.github.com/repos/{user}/{repo}/contents/{path}"
    print(package_url)
    response = requests.get(package_url, headers=headers)

    if response.status_code == 200:
        item = response.json()
        contents = base64.b64decode(item['content']).decode('utf-8')
        return contents
    else:
        raise HTTPException(status_code=response.status_code, detail=f"Failed to fetch {path}: {response.status_code}")


# TODO: readme 이미지 반환

# user-data 조회
@router.post("/user-data", response_model=List[repository_schema.RepositoryUserData], status_code=201)
def get_user_data(request: repository_schema.RepositoryCreateRequest, db: Session = Depends(get_db)) -> JSONResponse:
    created_repositories = []
    for repo_url in request.repository_url:
        if not repo_url:
            raise HTTPException(status_code=400, detail="Repository URL is required")

        # GitHub repository URL 파싱 TODO: repo_url을 패키지 파일이 있는 최상위 디렉토리 url로 할 수 있는지 확인
        parsed_url = urlparse(repo_url)
        path_segments = parsed_url.path.strip("/").split("/")
        if len(path_segments) != 2:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")

        user, repo = path_segments

        # 커밋 기록
        commit_messages = get_commit(user, repo)

        # 패키지 파일 내용
        package_files = ['requirements.txt', 'Pipfile', 'setup.py', 'build.gradle', 'pom.xml', 'package.json']
        package_path = find_package_file(user, repo, "", package_files)
        package_contents = get_package_contents(user, repo, package_path)

        # 매핑
        user_data = repository_schema.RepositoryUserData(
            repository_url=f"https://github.com/{user}/{repo}",
            commit_list=commit_messages,
            package_contents=package_contents,
            readme_images=["이미지", "이미지2"]
        )

        repository_data = {
            "user_id": request.user_id,
            "repository_url": repo_url,
            "main_image": "default_image.png",
            "user_data": user_data.dict(),
            "gpt_result": []
        }
        db_repository = repository_crud.create_repository(db, repository_data)
        created_repositories.append(user_data)

        if not db_repository:
            raise HTTPException(status_code=500, detail="Failed to save repository")

    user_data_json = jsonable_encoder(created_repositories)

    return JSONResponse(content={
        "message": "레포지토리 저장 성공",
        "data": user_data_json
    }, status_code=200)

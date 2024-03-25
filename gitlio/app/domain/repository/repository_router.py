import base64
import re

from fastapi import APIRouter, Depends, HTTPException
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from . import repository_schema, repository_crud
from ...database import get_db
import requests
from typing import List
from urllib.parse import urlparse
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

router = APIRouter(
    prefix="/api/repositories"
)

# GitHub Personal Access Token
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
headers = {
    'Authorization': f'Bearer {GITHUB_TOKEN}',
}


@router.get("/list")
def repository_list(db: Session = Depends(get_db)):
    _repository_list = repository_crud.get_repository_list(db)
    return _repository_list


# 커밋 기록 반환
def get_commit(org: str, repo: str, username: str):
    commit_messages = []
    page = 1
    while True:
        commit_url = f"https://api.github.com/repos/{org}/{repo}/commits?author={username}&page={page}&per_page=100"
        response = requests.get(commit_url, headers=headers)

        if response.status_code == 200:
            commits = response.json()
            if not commits:
                break  # 더 이상 가져올 커밋이 없으면 반복 종료
            commit_messages.extend([commit['commit']['message'] for commit in commits])
            page += 1
        else:
            raise HTTPException(status_code=response.status_code, detail="Failed to fetch commits from GitHub API")
    return commit_messages


# 패키지 파일 찾기
def find_package_file(org: str, repo: str, path: str, target_files: list):
    package_url = f"https://api.github.com/repos/{org}/{repo}/contents/{path}"
    response = requests.get(package_url, headers=headers)

    if response.status_code == 200:
        items = response.json()
        for item in items:
            if item['type'] == 'file' and item['name'] in target_files:
                return item['path']
            elif item['type'] == 'dir':
                # 하위 디렉토리를 재귀적으로 탐색
                found_path = find_package_file(org, repo, item['path'], target_files)
                if found_path:
                    return found_path
    elif response.status_code == 404:
        print(f"{path} not found in the repository.")


# 패키지 파일 내용 반환
def get_package_contents(org: str, repo: str, path: str):
    package_url = f"https://api.github.com/repos/{org}/{repo}/contents/{path}"
    print(package_url)
    response = requests.get(package_url, headers=headers)

    if response.status_code == 200:
        item = response.json()
        contents = base64.b64decode(item['content']).decode('utf-8')
        return contents
    else:
        print(f"Failed to fetch {path}")


# org의 Overview readme 이미지 반환
# TODO: 로직 수정하기
def get_readme_images(org: str):
    readme_url = f"https://api.github.com/repos/{org}/.github/contents/profile/README.md"
    response = requests.get(readme_url, headers=headers)

    if response.status_code == 200:
        readme_data = response.json()
        readme_content = readme_data['content']
        readme_content_decoded = base64.b64decode(readme_content).decode('utf-8')
        # HTML <img> 태그 내의 src 속성 값을 추출
        image_urls = re.findall(r'<img [^>]*src="([^"]+)"', readme_content_decoded)

        # https://github.com/ 시작하는 URL만 필터링
        github_image_urls = [url for url in image_urls if url.startswith("https://github.com/")]
        return github_image_urls
    else:
        return []


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

        org, repo = path_segments
        username = request.github_username

        # 커밋 기록
        commit_messages = get_commit(org, repo, username)

        # 패키지 파일 내용
        package_files = ['requirements.txt', 'Pipfile', 'setup.py', 'build.gradle', 'pom.xml', 'package.json', 'go.mod']
        package_path = find_package_file(org, repo, "", package_files)
        package_contents = get_package_contents(org, repo, package_path)

        # README 이미지
        readme_images = get_readme_images(org)

        # 매핑
        user_data = repository_schema.RepositoryUserData(
            repository_url=f"https://github.com/{org}/{repo}",
            commit_list=commit_messages,
            package_contents=package_contents,
            readme_images=readme_images
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

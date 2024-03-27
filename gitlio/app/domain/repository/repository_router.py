import base64
import re

from bs4 import BeautifulSoup
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


# readme 이미지 반환
def get_readme_images(org: str, repo: str):
    urls = [
        f"https://api.github.com/repos/{org}/.github/contents/profile/README.md",
        f"https://api.github.com/repos/{org}/{repo}/readme"
    ]

    for url in urls:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            readme_data = response.json()
            readme_content_encoded = readme_data['content']
            readme_content_decoded = base64.b64decode(readme_content_encoded).decode('utf-8')

            # 마크다운 이미지 링크 추출
            markdown_image_urls = re.findall(r'!\[.*?\]\((.*?)\)', readme_content_decoded)

            # HTML 이미지 링크 추출
            soup = BeautifulSoup(readme_content_decoded, 'html.parser')
            html_image_urls = [img['src'] for img in soup.find_all('img')]

            image_urls = markdown_image_urls + html_image_urls

            filtered_image_urls = [url for url in image_urls if
                                   "github.com/" in url or "githubusercontent.com/" in url]

            if filtered_image_urls:
                return filtered_image_urls
        else:
            print(f"Failed to fetch README from {url}")
    return []


# user-data 조회
@router.post("/user-data", response_model=List[repository_schema.RepositoryUserData], status_code=201)
def get_user_data(request: repository_schema.RepositoryCreateRequest, db: Session = Depends(get_db)) -> JSONResponse:
    org_repositories = {}
    personal_repositories = []
    errors = []
    for repo_url in request.repository_url:
        # GitHub repository URL 파싱
        parsed_url = urlparse(repo_url)
        path_segments = parsed_url.path.strip("/").split("/")
        if len(path_segments) < 2 or not repo_url:
            errors.append({"url": repo_url, "message": "Invalid or empty GitHub repository URL"})
            continue

        org, repo = path_segments
        username = request.github_username
        try:
            # 커밋 기록
            commit_messages = get_commit(org, repo, username)

            # 패키지 파일 내용
            package_files = ['requirements.txt', 'Pipfile', 'setup.py', 'build.gradle', 'pom.xml', 'package.json', 'go.mod']
            package_path = find_package_file(org, repo, "", package_files)
            package_contents = get_package_contents(org, repo, package_path)

            # README 이미지
            readme_images = get_readme_images(org, repo)

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

            if not db_repository:
                raise HTTPException(status_code=500, detail="Failed to save repository")

            # org 명으로 프로젝트 구분
            if org == username:
                # 개인 프로젝트로 처리
                personal_repositories.append(user_data)
            else:
                if org not in org_repositories:
                    org_repositories[org] = []
                org_repositories[org].append(user_data)

        except Exception as e:
            errors.append({"url": repo_url, "message": str(e)})

    results = {
        "success": {
            "organizations": jsonable_encoder(org_repositories),
            "personal": jsonable_encoder(personal_repositories)
        },
        "errors": errors
    }

    return JSONResponse(content={
        "message": "repository 저장 성공",
        "data": results
    }, status_code=201)

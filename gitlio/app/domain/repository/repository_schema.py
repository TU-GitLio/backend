from typing import List, Optional
from pydantic import BaseModel


class RepositoryModel(BaseModel):
    repository_id: int
    repository_url: str
    main_image: str
    user_data: List[str] = []
    gpt_result: List[str] = []


class RepositoryGPT(BaseModel):
    repository_url: str
    main_image: str             # 추후에 List 형식으로 변경
    gpt_result: List[str] = []
    status: bool


class RepositoryCreateRequest(BaseModel):
    user_id: int
    github_username: str
    repository_url: List[str] = []


class RepositoryUserData(BaseModel):
    repository_url: str
    commit_list: List[str] = []
    package_contents: Optional[str] = None
    readme_images: List[str] = []


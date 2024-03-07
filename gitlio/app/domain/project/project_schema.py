from typing import List
from pydantic import BaseModel


class Project(BaseModel):
    id: int
    repository_url: str
    title: str
    description: str
    duration: str
    skill : List[str] = []
    gpt_data: List[str] = []
    document_url: str

class ProjectGpt(BaseModel):
    repository_url: str
    gpt_data: List[str] = []
    status: bool

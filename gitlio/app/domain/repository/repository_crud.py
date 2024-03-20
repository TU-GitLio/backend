from .repository_schema import *
from ... import models
from ...models import Repository
from sqlalchemy.orm import Session


def create_repository(db: Session, repository: RepositoryCreateRequest):
    # repository_data 딕셔너리에서 필요한 정보를 추출하여 Repository 인스턴스 생성
    db_repository = models.Repository(**repository)
    db.add(db_repository)
    db.commit()
    db.refresh(db_repository)
    return db_repository


def get_repository_list(db: Session):
    repository_list = db.query(Repository)\
        .all()
    return repository_list


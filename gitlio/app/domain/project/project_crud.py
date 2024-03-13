from ...models import Repository
from sqlalchemy.orm import Session


def get_project_list(db: Session):
    project_list = db.query(Repository)\
        .all()
    return project_list
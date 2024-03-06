from ...models import Project
from sqlalchemy.orm import Session


def get_project_list(db: Session):
    project_list = db.query(Project)\
        .all()
    return project_list
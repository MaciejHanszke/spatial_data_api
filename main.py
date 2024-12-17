from typing import List

from fastapi import FastAPI

from project_model import Project, ProjectOutput
from sqlalchemy_setup import SQL_ALCHEMY_BASE, SQL_ALCHEMY_DB, SQL_ALCHEMY_SESSION

def main():
    SQL_ALCHEMY_BASE.metadata.create_all(SQL_ALCHEMY_DB)

    return FastAPI()

app = main()

@app.get("/list", response_model=List[ProjectOutput])
async def list_projects():
    with SQL_ALCHEMY_SESSION() as session:
        projects = session.query(Project).all()
        return [ProjectOutput.from_orm(project) for project in projects]
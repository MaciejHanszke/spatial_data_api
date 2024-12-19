from typing import List

from fastapi import FastAPI

from project_entity import ProjectOutput, CreateProjectProjectRequestModel, Project, UpdateProjectRequestModel
from sqlalchemy_setup import SQL_ALCHEMY_BASE, SQL_ALCHEMY_DB, SQL_ALCHEMY_SESSION

def main():
    SQL_ALCHEMY_BASE.metadata.create_all(SQL_ALCHEMY_DB)

    return FastAPI()

app = main()

@app.get('/health')
def health():
    return {"detail": "OK"}

# TODO HANDLE FEATURE COLLECTION - MAYBE MANY-TO-MANY RELATION?
@app.post("/project/create")
async def create_project(request: CreateProjectProjectRequestModel):
    return Project(SQL_ALCHEMY_SESSION).insert(request)

@app.get("/project/{project_id}", response_model=ProjectOutput)
async def get_project(project_id: str):
    return Project(SQL_ALCHEMY_SESSION).get(project_id)

@app.get("/list_projects", response_model=List[ProjectOutput])
async def list_projects():
    return Project(SQL_ALCHEMY_SESSION).list()

@app.delete("/project/{project_id}")
async def delete_project(project_id: str):
    return Project(SQL_ALCHEMY_SESSION).delete(project_id)

@app.put("/project/{project_id}")
async def update_project(project_id: str, request: UpdateProjectRequestModel):
    return Project(SQL_ALCHEMY_SESSION).update(project_id, request)


import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from project_entity import CreateProjectRequestModel, UpdateProjectRequestModel, ProjectCRUD
from sqlalchemy_setup import SQL_ALCHEMY_BASE, SQL_ALCHEMY_DB, SQL_ALCHEMY_SESSION

MAX_RECONNECT_RETRIES = 4

# TODO replace prints with logger
# TODO Unit tests
def main():
    for retry in range(MAX_RECONNECT_RETRIES):
        try:
            print(f"Attempting database connection {retry+1}/{MAX_RECONNECT_RETRIES}")
            SQL_ALCHEMY_BASE.metadata.create_all(SQL_ALCHEMY_DB)
            break
        except OperationalError as e:
            # TODO Maybe do a health check call?
            print(e)
            if (retry + 1) == MAX_RECONNECT_RETRIES:
                raise OperationalError("Max retries for connecting database reached. Exiting.", None, e)
            exponential_backoff_time = (retry + 1) * 5
            print(f"Failed DB connection. Retrying after {exponential_backoff_time} seconds")
            time.sleep(exponential_backoff_time)
    print("DB Connection established.")

    return FastAPI(
        title="Spatial Data API",
        description="Basic CRUD application allowing to interact with so called \"Projects\".",
        version="0.0.1"
    )

app = main()

@app.get('/health')
def health():
    return {"detail": "OK"}

# TODO HANDLE FASTAPI DOCS
@app.post("/project/create")
async def create_project(request: CreateProjectRequestModel):
    return ProjectCRUD(SQL_ALCHEMY_SESSION).insert(request)

@app.get("/project/{project_id}")
async def get_project(project_id: str):
    return ProjectCRUD(SQL_ALCHEMY_SESSION).get(project_id)

@app.get("/list_projects")
async def list_projects():
    return ProjectCRUD(SQL_ALCHEMY_SESSION).list()

@app.delete("/project/{project_id}")
async def delete_project(project_id: str):
    return ProjectCRUD(SQL_ALCHEMY_SESSION).delete(project_id)

@app.put("/project/{project_id}")
async def update_project(project_id: str, request: UpdateProjectRequestModel):
    return ProjectCRUD(SQL_ALCHEMY_SESSION).update(project_id, request)


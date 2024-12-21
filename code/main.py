import logging
import time

from fastapi import FastAPI
from sqlalchemy.exc import OperationalError

from project_entity import CreateProjectRequestModel, UpdateProjectRequestModel, ProjectCRUD
from project_entity_docs import create_project_sample_response, get_project_sample_response, \
    delete_project_sample_response, service_healthy_sample_response, update_project_sample_response, \
    list_project_sample_response
from sqlalchemy_setup import SQL_ALCHEMY_BASE, SQL_ALCHEMY_DB, SQL_ALCHEMY_SESSION

logger = logging.getLogger('uvicorn.error')

MAX_RECONNECT_RETRIES = 4

def main():
    for retry in range(MAX_RECONNECT_RETRIES):
        try:
            logger.info(f"Attempting database connection {retry+1}/{MAX_RECONNECT_RETRIES}")
            SQL_ALCHEMY_BASE.metadata.create_all(SQL_ALCHEMY_DB)
            break
        except OperationalError as e:
            logger.warning(e)
            if (retry + 1) == MAX_RECONNECT_RETRIES:
                raise OperationalError("Max retries for connecting database reached. Exiting.", None, e)
            exponential_backoff_time = (retry + 1) * 5
            logger.warning(f"Failed DB connection. Retrying after {exponential_backoff_time} seconds")
            time.sleep(exponential_backoff_time)
    logger.info("DB Connection established.")

    return FastAPI(
        title="Spatial Data API",
        description="Basic CRUD application allowing to interact with so called \"Projects\".",
        version="0.0.1"
    )

app = main()

@app.get('/health', responses=service_healthy_sample_response)
def health():
    """
    Check the health of the service (used, for example, for ECS).

    - **status_code 200**: Service healthy.
    """
    return {"detail": "OK"}

@app.post("/project/create", responses=create_project_sample_response)
async def create_project(request: CreateProjectRequestModel):
    """
    Create a new project.

    - **name**: The name of the project.
    - **description**: Optional description of the project.
    - **date_range**: The start and end dates for the project.
    - **area_of_interest**: GeoJSON data representing the area of interest.

    Returns the newly created project object.

    - **status_code 200**: Project created successfully.
    - **status_code 422**: Invalid data provided.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).insert(request)

@app.get("/project/{project_id}", responses=get_project_sample_response)
async def get_project(project_id: str):
    """
    Fetch a single project by its ID.

    - **project_id**: The unique identifier of the project.

    Returns the project if found, else raises a 404 error.

    - **status_code 200**: Project found and returned.
    - **status_code 404**: Project not found.
    - **status_code 422**: Invalid UUID project_id provided.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).get(project_id)

@app.get("/list_projects", responses=list_project_sample_response)
async def list_projects():
    """
    Fetch a list of all projects.

    - **status_code 200**: Successfully returned a list of projects, each with ID, name, description, and other details.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).list()

@app.delete("/project/{project_id}", responses=delete_project_sample_response)
async def delete_project(project_id: str):
    """
    Delete a project by its ID.

    - **project_id**: The unique identifier of the project to delete.

    - **status_code 200**: Project deleted successfully.
    - **status_code 404**: Project not found.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).delete(project_id)

@app.put("/project/{project_id}", responses=update_project_sample_response)
async def update_project(project_id: str, request: UpdateProjectRequestModel):
    """
    Update a project by its ID.

    - **project_id**: The unique identifier of the project to update.
    - **request**: The data to update the project with (e.g., new name, description, area of interest, etc.).

    Returns the updated project object.

    - **status_code 200**: Project updated successfully.
    - **status_code 404**: Project not found.
    - **status_code 422**: Invalid data provided.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).update(project_id, request)


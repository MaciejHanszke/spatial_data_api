from fastapi import APIRouter

from .docs import create_project_sample_response, get_project_sample_response, \
    list_project_sample_response, delete_project_sample_response, update_project_sample_response
from .crud import ProjectCRUD, CreateProjectRequestModel, UpdateProjectRequestModel
from sqlalchemy_setup import SQL_ALCHEMY_SESSION

project_router = APIRouter()

@project_router.post("/", responses=create_project_sample_response)
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

@project_router.get("/", responses=list_project_sample_response)
async def list_projects():
    """
    Fetch a list of all projects.

    - **status_code 200**: Successfully returned a list of projects, each with ID, name, description, and other details.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).list()

@project_router.get("/{project_id}", responses=get_project_sample_response)
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

@project_router.delete("/{project_id}", responses=delete_project_sample_response)
async def delete_project(project_id: str):
    """
    Delete a project by its ID.

    - **project_id**: The unique identifier of the project to delete.

    - **status_code 200**: Project deleted successfully.
    - **status_code 404**: Project not found.
    """
    return ProjectCRUD(SQL_ALCHEMY_SESSION).delete(project_id)

@project_router.put("/{project_id}", responses=update_project_sample_response)
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
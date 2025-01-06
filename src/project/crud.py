from datetime import datetime, date
from typing import List

import geojson
import geojson_validator
from fastapi import HTTPException
from geoalchemy2.functions import ST_GeomFromGeoJSON
from pydantic import ValidationError
from sqlalchemy.dialects.postgresql import Range
from sqlalchemy.orm import Session, sessionmaker

from .schemas import FetchSingleProjectModel, CreateProjectRequestModel, UpdateProjectRequestModel
from .models import ProjectGeneralEntity, ProjectAOIEntity

geojson_validator.configure_logging(enabled=False)

class ProjectCRUD:
    """
    Provides CRUD (Create, Read, Update, Delete) operations for project entities in the database.

    Attributes:
        SQL_ALCHEMY_SESSION (Session): The SQLAlchemy session for interacting with the database.

    Methods:
        transform_date_range(): Transforms the date range dictionary into a Range object.
        insert(): Inserts a new project into the database.
        get(): Retrieves a project by its ID from the database.
        list(): Retrieves all projects from the database.
        delete(): Deletes a project by its ID from the database.
        update(): Updates a project by its ID with the provided data.
    """
    def __init__(self, sql_alchemy_session: sessionmaker):
        """
        Initializes the ProjectCRUD class with a given SQLAlchemy session.

        Args:
            sql_alchemy_session (sessionmaker): The SQLAlchemy session to interact with the database.
        """
        super().__init__()
        self.SQL_ALCHEMY_SESSION = sql_alchemy_session

    @staticmethod
    def transform_date_range(date_range: dict[str, str]) -> Range[date]:
        """
        Transforms a dictionary containing 'lower' and 'upper' date values into a Range object.

        Args:
            date_range (dict[str, str]): A dictionary containing the 'lower' and 'upper' dates as strings.

        Returns:
            Range[date]: A Range object representing the date range.

        Raises:
            ValueError: If the date range is invalid.
        """
        lower = datetime.strptime(date_range['lower'], '%Y-%m-%d').date()
        upper = datetime.strptime(date_range['upper'], '%Y-%m-%d').date()
        return Range(lower, upper, bounds='[)' if upper > lower else '[]')

    @staticmethod
    def _get_project_by_id(project_id: str, session: Session) -> ProjectGeneralEntity:
        """
        Retrieves a project entity by ID.
        """
        try:
            FetchSingleProjectModel(project_id=project_id)
        except ValidationError:
            raise HTTPException(status_code=400, detail="Invalid project ID format")

        project = session.query(ProjectGeneralEntity).filter(ProjectGeneralEntity.id == project_id).first()
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        return project

    @staticmethod
    def __prepare_aoi_entity(single_area_of_interest: dict, fetch_geometry: bool = True) -> ProjectAOIEntity:
        """
        Prepares an Area of Interest (AOI) entity for insertion into the database.

        Args:
            single_area_of_interest (dict): The GeoJSON-like dictionary representing the AOI.
            fetch_geometry (bool): Whether to extract the 'geometry' key (default is True).

        Returns:
            ProjectAOIEntity: The prepared AOI entity.
        """
        if fetch_geometry:
            single_area_of_interest = single_area_of_interest['geometry']
        geometry_wkt = geojson.dumps(single_area_of_interest)
        return ProjectAOIEntity(
            area_of_interest=ST_GeomFromGeoJSON(geometry_wkt)
        )

    def __prepare_aoi_list(self, area_of_interest: dict) -> List[ProjectAOIEntity]:
        """
        Prepares a list of AOI entities from a GeoJSON-like dictionary representing the area of interest.

        Args:
            area_of_interest (dict): The GeoJSON-like dictionary representing the area of interest.

        Returns:
            List[ProjectAOIEntity]: A list of AOI entities.
        """
        if area_of_interest['type'] == 'FeatureCollection':
            return [self.__prepare_aoi_entity(single_aoi) for single_aoi in area_of_interest.get("features", [])]
        elif area_of_interest['type'] == 'GeometryCollection':
            return [self.__prepare_aoi_entity(single_aoi, False) for single_aoi in area_of_interest.get("geometries", [])]
        return [self.__prepare_aoi_entity(area_of_interest)]


    def insert(self, request: CreateProjectRequestModel) -> dict[str, str]:
        """
        Inserts a new project into the database.

        Args:
            request (CreateProjectRequestModel): The request model containing project data.

        Returns:
            dict: A dictionary containing a message with the new project ID.
        """
        project = ProjectGeneralEntity(
            name=request.name,
            description=request.description,
            date_range=self.transform_date_range(request.date_range),
            area_of_interest_list=self.__prepare_aoi_list(request.area_of_interest),
            area_of_interest_json=request.area_of_interest
        )
        with self.SQL_ALCHEMY_SESSION() as session:
            session.add(project)
            session.commit()
            return {"detail": f"New project added: {project.id}"}

    def get(self, project_id: str) -> dict:
        """
        Retrieves a project by its ID from the database.

        Args:
            project_id (str): The unique identifier of the project.

        Returns:
            dict: A dictionary containing the project's data.

        Raises:
            HTTPException: If the project cannot be found.
        """
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self._get_project_by_id(project_id, session)
            return project.to_dict()

    def list(self) -> List[dict]:
        """
        Retrieves all projects from the database.

        Returns:
            List[dict]: A list of dictionaries containing data for all projects.
        """
        with self.SQL_ALCHEMY_SESSION() as session:
            projects = session.query(ProjectGeneralEntity).all()
            return [project.to_dict() for project in projects]

    def delete(self, project_id: str) -> dict[str, str]:
        """
        Deletes a project by its ID from the database.

        Args:
            project_id (str): The unique identifier of the project to delete.

        Returns:
            dict: A dictionary containing a message confirming the deletion.

        Raises:
            HTTPException: If the project cannot be found.
        """
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self._get_project_by_id(project_id, session)
            session.delete(project)
            session.commit()
        return {"detail": f"Project {project_id} deleted"}

    def update(self, project_id: str, request: UpdateProjectRequestModel) -> dict[str, str]:
        """
        Updates an existing project with new data.

        Args:
            project_id (str): The unique identifier of the project to update.
            request (UpdateProjectRequestModel): The request model containing updated project data.

        Returns:
            dict: A dictionary containing a message confirming the update.

        Raises:
            HTTPException: If the project cannot be found.
        """
        request_dict = request.initialized_fields()
        if not request_dict:
            raise HTTPException(status_code=422, detail=f"No fields to update. Omitting.")
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self._get_project_by_id(project_id, session)
            if 'date_range' in request_dict:
                request_dict['date_range'] = self.transform_date_range(request.date_range)
            if 'area_of_interest' in request_dict:
                request_dict['area_of_interest_json'] = request.area_of_interest
                request_dict['area_of_interest_list'] = self.__prepare_aoi_list(request.area_of_interest)
                del request_dict['area_of_interest']

            for field in request_dict:
                setattr(project, field, request_dict[field])

            session.commit()
        return {"detail": f"Project {project_id} updated"}

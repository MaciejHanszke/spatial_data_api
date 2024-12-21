import copy
from datetime import datetime, date
from typing import Optional, Annotated, List
from uuid import UUID, uuid4

import geojson
import geojson_validator
from fastapi import HTTPException
from geoalchemy2 import Geometry
from geoalchemy2.functions import ST_GeomFromGeoJSON
from pydantic import BaseModel, Field, model_validator, UUID4, Strict, ValidationError
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import DATERANGE, Range
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session, sessionmaker
from project_entity_docs import create_project_sample_request, update_project_sample_request
from sqlalchemy_setup import SQL_ALCHEMY_BASE

geojson_validator.configure_logging(enabled=False)

class ProjectGeneralEntity(SQL_ALCHEMY_BASE):
    """
    Entity representing a generic Project.

    Attributes:
        id (UUID): The unique identifier for the project (auto-generated).
        name (str): The name of the project.
        description (Optional[str]): An optional description of the project.
        date_range (DATERANGE): The start and end dates for the project.
        area_of_interest_list (List[ProjectAOIEntity]): A list of Area of Interest (AOI) entities associated with the project.
        area_of_interest_json (JSON): A GeoJSON representation of the project's area of interest.

    Methods:
        __repr__(): Returns a string representation of the project.
        to_dict(): Converts the project entity into a dictionary for serialization.
    """
    __tablename__ = "projects_general"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[Optional[str]]
    date_range: Mapped[DATERANGE] = mapped_column(DATERANGE, nullable=False)
    area_of_interest_list: Mapped[List["ProjectAOIEntity"]] = relationship("ProjectAOIEntity",
                                                                           back_populates="general_entities",
                                                                           cascade="all, delete-orphan")
    area_of_interest_json: Mapped[JSON] = mapped_column(JSON, nullable=False)

    def __repr__(self) -> str:
        """
        Returns a string representation of the project entity.

        Returns:
            str: A string representing the project with its ID, name, and description.
        """
        return f"<Project(id={self.id}, name={self.name}, description={self.description})"

    def to_dict(self) -> dict:
        """
        Converts the project entity into a dictionary for serialization.

        Returns:
            dict: A dictionary representation of the project with relevant fields.
        """
        area_of_interest_code = [str(aoi_entity.area_of_interest) for aoi_entity in self.area_of_interest_list]

        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "date_range": self.date_range,
            "area_of_interest": self.area_of_interest_json,
            "area_of_interest_geom": area_of_interest_code
        }

class ProjectAOIEntity(SQL_ALCHEMY_BASE):
    """
    Represents an Area of Interest (AOI) entity associated with a project.

    Attributes:
        id (UUID): The unique identifier for the AOI. (auto-generated)
        general_id (UUID): The foreign key referring to the associated project (from project_general table).
        area_of_interest (Geometry): The geometry data representing the area of interest.
        general_entities (List[ProjectGeneralEntity]): A list of general project entities associated with the AOI.
    """
    __tablename__ = "projects_aoi"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    general_id: Mapped[UUID] = mapped_column(ForeignKey('projects_general.id', ondelete='CASCADE'), nullable=False)
    area_of_interest: Mapped[Geometry] = mapped_column(Geometry('GEOMETRY', srid=4326), nullable=False)
    general_entities: Mapped[List["ProjectGeneralEntity"]] = relationship("ProjectGeneralEntity", back_populates="area_of_interest_list")

class BasicProjectRequestModel(BaseModel):
    """
    Base model for project request validation.

    Provides methods to validate the project date range and area of interest fields after model initialization.

    Methods:
        perform_after_validations(): Validates the date range and area of interest fields after model initialization.
    """
    @model_validator(mode='after')
    def perform_after_validations(self):
        """
        Performs validation checks on the date range and area of interest fields.

        Raises:
            ValueError: If the date range or area of interest is invalid.

        Returns:
            self: The validated instance.
        """
        self._validate_date_range()
        self._validate_area_of_interest()
        return self

    def _validate_date_range(self) -> None:
        """
        Validates the date range to ensure it contains both 'lower' and 'upper' dates in the correct format.

        Raises:
            ValueError: If the date range is invalid or the lower date is after the upper date.
        """
        if not self.date_range:
            raise ValueError("date_range field is an empty dictionary")

        if not self.date_range.get('lower') or not self.date_range.get('upper'):
            raise ValueError("date_range field has to contain both 'lower' and 'upper' fields")

        transformed_date_range = {}
        for field_name in ["lower", "upper"]:
            try:
                transformed_date_range[field_name] = datetime.strptime(self.date_range[field_name], '%Y-%m-%d').date()
            except TypeError:
                raise ValueError(f"You need to provide string following YYYY-MM-DD format for {field_name}")
            except ValueError:
                raise ValueError(f"The field {field_name} does not follow YYYY-MM-DD format")
        if transformed_date_range['lower'] > transformed_date_range['upper']:
            raise ValueError("The lower range cannot be equal or higher than upper range!")

    def _validate_area_of_interest(self) -> None:
        """
        Validates the area of interest geometry using geojson_validator.

        Raises:
            ValueError: If the area of interest has invalid geometry.
        """
        test_area_of_interest = copy.deepcopy(self.area_of_interest)

        if geojson_validator.validate_structure(test_area_of_interest):
            raise ValueError("area_of_interest has invalid structure")

        if geojson_validator.validate_geometries(test_area_of_interest).get('invalid'):
            raise ValueError("area_of_interest has invalid geometry")

class CreateProjectRequestModel(BasicProjectRequestModel):
    """
    Request model for creating a new project.

    Attributes:
        name (str): The name of the project.
        description (Optional[str]): Optional description of the project.
        date_range (dict): The start and end dates for the project.
        area_of_interest (dict): The GeoJSON representation of the area of interest.
    """
    name: str = Field(..., max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: dict
    area_of_interest: dict

    model_config = create_project_sample_request

class UpdateProjectRequestModel(BasicProjectRequestModel):
    """
    Request model for updating an existing project.
    This model has an optional validation, if the fields do exist (CreateProject model MUST contain some of the fields).

    Attributes:
        name (Optional[str]): The new name of the project (optional).
        description (Optional[str]): The new description of the project (optional).
        date_range (Optional[dict]): The new date range for the project (optional).
        area_of_interest (Optional[dict]): The new geojson representation of the area of interest (optional).

    Methods:
        initialized_fields(): Returns a dictionary containing initialized fields with their respective values.
    """
    name: Optional[str] = Field(None, max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: Optional[dict] = None
    area_of_interest: Optional[dict] = None

    model_config = update_project_sample_request

    def initialized_fields(self) -> dict:
        """
        Returns a dictionary of fields that have been initialized (i.e., are not None).

        Returns:
            dict: A dictionary containing initialized fields with their respective values.
        """
        return {field: value for field, value in self.model_dump().items() if value is not None}

    def _validate_date_range(self) -> None:
        """
        Validates the date range if it is provided in the request.

        Calls the base class validation if a date range is provided.
        """
        if self.date_range:
            super()._validate_date_range()

    def _validate_area_of_interest(self) -> None:
        """
        Validates the area of interest if it is provided in the request.

        Calls the base class validation if an area of interest is provided.
        """
        if self.area_of_interest:
            super()._validate_area_of_interest()

class FetchSingleProjectModel(BaseModel):
    """
    Model for fetching a single project by its UUID.

    Attributes:
        project_id (UUID4): The unique identifier of the project to fetch.
    """
    project_id: Annotated[UUID4, Strict(False)]

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
        if upper > lower:
            date_range = Range(lower, upper, bounds='[)')
        else:
            date_range = Range(lower, upper, bounds='[]')
        return date_range

    @staticmethod
    def __perform_single_entity_op(project_id: str, session: Session, function_type: str = 'first') -> ProjectGeneralEntity:
        """
        Performs a single query operation to retrieve or manipulate a project entity.

        Args:
            project_id (str): The unique identifier of the project.
            session (Session): The SQLAlchemy session to query the database.
            function_type (str): The query operation to perform (default is 'first').

        Returns:
            ProjectGeneralEntity: The retrieved project entity.

        Raises:
            HTTPException: If the project ID is invalid or the project cannot be found.
        """
        try:
            FetchSingleProjectModel(project_id=project_id)
        except ValidationError:
            raise HTTPException(status_code=400, detail=f"The project id path parameter should follow UUID convention")

        basic_query = session.query(ProjectGeneralEntity).filter(ProjectGeneralEntity.id == project_id)
        func = getattr(basic_query, function_type, None)
        if not func:
            raise ValueError("Invalid function passed in")
        project = func()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project not found")
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
            project = self.__perform_single_entity_op(project_id, session)
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
            self.__perform_single_entity_op(project_id, session, 'delete')
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
            project = self.__perform_single_entity_op(project_id, session)
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

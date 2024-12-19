import copy
from datetime import datetime
from typing import Optional, Annotated
from uuid import UUID, uuid4

import geojson
import geojson_validator
from fastapi import HTTPException
from geoalchemy2.functions import ST_GeomFromGeoJSON
from pydantic import BaseModel, Field, model_validator, UUID4, Strict, ValidationError
from shapely import wkb
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import DATERANGE, Range
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from sqlalchemy_setup import SQL_ALCHEMY_BASE

geojson_validator.configure_logging(enabled=False)

# TODO DOCSTRINGS! Annotation Types!

class ProjectEntity(SQL_ALCHEMY_BASE):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[Optional[str]]
    date_range: Mapped[DATERANGE] = mapped_column(DATERANGE, nullable=False)
    area_of_interest: Mapped[Geometry] = mapped_column(Geometry('GEOMETRY', srid=4326))

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, description={self.description})"

class BasicProjectRequestModel(BaseModel):
    @model_validator(mode='after')
    def perform_after_validations(self):
        self._validate_date_range()
        self._validate_area_of_interest()
        return self

    def _validate_date_range(self):
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

    def _validate_area_of_interest(self):
        test_area_of_interest = copy.deepcopy(self.area_of_interest)

        if geojson_validator.validate_geometries(test_area_of_interest).get('invalid'):
            raise ValueError("area_of_interest has invalid geometry")

class CreateProjectProjectRequestModel(BasicProjectRequestModel):
    name: str = Field(..., max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: dict
    area_of_interest: dict

class UpdateProjectRequestModel(BasicProjectRequestModel):
    name: Optional[str] = Field(None, max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: Optional[dict] = None
    area_of_interest: Optional[dict] = None

    def initialized_fields(self) -> list:
        # TODO add a docstring that this function returns the names of fields that are not None
        return [field for field, value in self.model_dump().items() if value is not None]

    def _validate_date_range(self):
        if self.date_range:
            super()._validate_date_range()

    def _validate_area_of_interest(self):
        if self.area_of_interest:
            super()._validate_area_of_interest()

class FetchSingleProjectModel(BaseModel):
    project_id: Annotated[UUID4, Strict(False)]

class ProjectOutput(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: UUID
    name: str
    description: Optional[str]
    date_range: Range
    area_of_interest: dict
    area_of_interest_geom: str

    @classmethod
    def from_orm(cls, project: 'ProjectEntity') -> 'ProjectOutput':
        geojson_output = wkb.loads(bytes.fromhex(str(project.area_of_interest))).__geo_interface__

        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            date_range=project.date_range,
            area_of_interest=geojson_output,
            area_of_interest_geom=str(project.area_of_interest)

        )

class Project:
    def __init__(self, sql_alchemy_session):
        super().__init__()
        self.SQL_ALCHEMY_SESSION = sql_alchemy_session

    @staticmethod
    def __prepare_model_for_insertion(project):
        if project.area_of_interest:
            geometry_wkt = geojson.dumps(project.area_of_interest['geometry'])
            project.area_of_interest = ST_GeomFromGeoJSON(geometry_wkt)
        if project.date_range:
            lower = datetime.strptime(project.date_range['lower'], '%Y-%m-%d').date()
            upper = datetime.strptime(project.date_range['upper'], '%Y-%m-%d').date()
            if upper > lower:
                project.date_range = Range(lower, upper, bounds='[)')
            else:
                project.date_range = Range(lower, upper, bounds='[]')

    @staticmethod
    def __perform_single_entity_op(project_id, session, function_type = 'first'):
        try:
            FetchSingleProjectModel(project_id=project_id)
        except ValidationError:
            raise HTTPException(status_code=400, detail=f"The project id path parameter should follow UUID convention")

        basic_query = session.query(ProjectEntity).filter(ProjectEntity.id == project_id)
        func = getattr(basic_query, function_type, None)
        if not func:
            raise ValueError("Invalid function passed in")
        project = func()
        if not project:
            raise HTTPException(status_code=404, detail=f"Project not found")
        return project

    def insert(self, request: CreateProjectProjectRequestModel):
        project = ProjectEntity(
            name=request.name,
            description=request.description,
            date_range=request.date_range,
            area_of_interest=request.area_of_interest
        )
        self.__prepare_model_for_insertion(project)
        with self.SQL_ALCHEMY_SESSION() as session:
            session.add(project)
            session.commit()
            return {"detail": f"New project added: {project.id}"}

    def list(self):
        with self.SQL_ALCHEMY_SESSION() as session:
            projects = session.query(ProjectEntity).all()
            return [ProjectOutput.from_orm(project) for project in projects]

    def get(self, project_id: str):
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self.__perform_single_entity_op(project_id, session)
            return ProjectOutput.from_orm(project)

    def delete(self, project_id: str):
        with self.SQL_ALCHEMY_SESSION() as session:
            self.__perform_single_entity_op(project_id, session, 'delete')
            session.commit()
        return {"detail": f"Project {project_id} deleted"}

    def update(self, project_id, request: UpdateProjectRequestModel):
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self.__perform_single_entity_op(project_id, session)
            for field in request.initialized_fields():
                setattr(project, field, getattr(request, field))
            self.__prepare_model_for_insertion(project)
            session.commit()
        return {"detail": f"Project {project_id} updated"}

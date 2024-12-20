import copy
from datetime import datetime
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
from sqlalchemy.orm import Mapped, mapped_column, relationship
from project_entity_docs import create_project_sample_request
from sqlalchemy_setup import SQL_ALCHEMY_BASE

geojson_validator.configure_logging(enabled=False)

# TODO DOCSTRINGS! Annotation Types!

class ProjectGeneralEntity(SQL_ALCHEMY_BASE):
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
        return f"<Project(id={self.id}, name={self.name}, description={self.description})"

    def to_dict(self) -> dict:
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
    __tablename__ = "projects_aoi"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    general_id: Mapped[UUID] = mapped_column(ForeignKey('projects_general.id', ondelete='CASCADE'), nullable=False)
    area_of_interest: Mapped[Geometry] = mapped_column(Geometry('GEOMETRY', srid=4326))
    general_entities: Mapped[List["ProjectGeneralEntity"]] = relationship("ProjectGeneralEntity", back_populates="area_of_interest_list")

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

class CreateProjectRequestModel(BasicProjectRequestModel):
    name: str = Field(..., max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: dict
    area_of_interest: dict

    model_config = create_project_sample_request

class UpdateProjectRequestModel(BasicProjectRequestModel):
    name: Optional[str] = Field(None, max_length=32, min_length=1)
    description: Optional[str] = Field(None, max_length=256)
    date_range: Optional[dict] = None
    area_of_interest: Optional[dict] = None

    def initialized_fields(self):
        return {field: value for field, value in self.model_dump().items() if value is not None}

    def _validate_date_range(self):
        if self.date_range:
            super()._validate_date_range()

    def _validate_area_of_interest(self):
        if self.area_of_interest:
            super()._validate_area_of_interest()

class FetchSingleProjectModel(BaseModel):
    project_id: Annotated[UUID4, Strict(False)]

class ProjectCRUD:
    def __init__(self, sql_alchemy_session):
        super().__init__()
        self.SQL_ALCHEMY_SESSION = sql_alchemy_session

    @staticmethod
    def transform_date_range(date_range):
        lower = datetime.strptime(date_range['lower'], '%Y-%m-%d').date()
        upper = datetime.strptime(date_range['upper'], '%Y-%m-%d').date()
        if upper > lower:
            date_range = Range(lower, upper, bounds='[)')
        else:
            date_range = Range(lower, upper, bounds='[]')
        return date_range

    @staticmethod
    def __perform_single_entity_op(project_id, session, function_type = 'first'):
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
    def __prepare_aoi_entity(single_area_of_interest, fetch_geometry = True):
        if fetch_geometry:
            single_area_of_interest = single_area_of_interest['geometry']
        geometry_wkt = geojson.dumps(single_area_of_interest)
        return ProjectAOIEntity(
            area_of_interest=ST_GeomFromGeoJSON(geometry_wkt)
        )

    def __prepare_aoi_list(self, area_of_interest):
        if area_of_interest['type'] == 'FeatureCollection':
            return [self.__prepare_aoi_entity(single_aoi) for single_aoi in area_of_interest.get("features", [])]
        elif area_of_interest['type'] == 'GeometryCollection':
            return [self.__prepare_aoi_entity(single_aoi, False) for single_aoi in area_of_interest.get("geometries", [])]
        return [self.__prepare_aoi_entity(area_of_interest)]


    def insert(self, request: CreateProjectRequestModel):
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

    def get(self, project_id: str):
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self.__perform_single_entity_op(project_id, session)
            return project.to_dict()

    def list(self):
        with self.SQL_ALCHEMY_SESSION() as session:
            projects = session.query(ProjectGeneralEntity).all()
            return [project.to_dict() for project in projects]

    def delete(self, project_id: str):
        with self.SQL_ALCHEMY_SESSION() as session:
            self.__perform_single_entity_op(project_id, session, 'delete')
            session.commit()
        return {"detail": f"Project {project_id} deleted"}

    def update(self, project_id, request: UpdateProjectRequestModel):
        with self.SQL_ALCHEMY_SESSION() as session:
            project = self.__perform_single_entity_op(project_id, session)

            request_dict = request.initialized_fields()
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

from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel
from shapely import wkb
from sqlalchemy import String
from sqlalchemy.dialects.postgresql import DATERANGE, Range
from sqlalchemy.orm import Mapped, mapped_column
from geoalchemy2 import Geometry
from sqlalchemy_setup import SQL_ALCHEMY_BASE


class Project(SQL_ALCHEMY_BASE):
    __tablename__ = "projects"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    name: Mapped[str] = mapped_column(String(32), nullable=False)
    description: Mapped[Optional[str]]
    date_range: Mapped[DATERANGE] = mapped_column(DATERANGE, nullable=False)
    area_of_interest: Mapped[Geometry] = mapped_column(Geometry('GEOMETRY', srid=4326))

    def __repr__(self) -> str:
        return f"<Project(id={self.id}, name={self.name}, description={self.description})"

class ProjectOutput(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    id: UUID
    name: str
    description: Optional[str]
    date_range: Range
    area_of_interest: str
    area_of_interest_geojson: dict

    @classmethod
    def from_orm(cls, project: 'Project') -> 'ProjectOutput':
        geojson = wkb.loads(bytes.fromhex(str(project.area_of_interest))).__geo_interface__

        return cls(
            id=project.id,
            name=project.name,
            description=project.description,
            date_range=project.date_range,
            area_of_interest=str(project.area_of_interest),
            area_of_interest_geojson=geojson
        )
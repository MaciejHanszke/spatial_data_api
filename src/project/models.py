from typing import Optional, List
from uuid import UUID, uuid4

from geoalchemy2 import Geometry
from sqlalchemy import String, JSON, ForeignKey
from sqlalchemy.dialects.postgresql import DATERANGE
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy_setup import SQL_ALCHEMY_BASE


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
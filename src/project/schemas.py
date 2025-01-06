import copy
from datetime import datetime
from typing import Optional, Annotated

import geojson_validator
from pydantic import BaseModel, model_validator, Field, UUID4, Strict

from .docs import create_project_sample_request, update_project_sample_request


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
from typing import Optional

import pytest
from fastapi import HTTPException

from tests.test_project_entity_constants import test_cu, test_cu_no_date, \
    test_cu_no_lower, test_cu_no_upper, \
    test_cu_invalid_type, test_cu_invalid_value, \
    test_cu_lower_higher_than_upper, test_cu_invalid_aoi, test_cu_no_date_expected, \
    test_cu_no_lower_expected, test_cu_no_upper_expected, \
    test_cu_invalid_type_expected, test_cu_invalid_value_expected, \
    test_cu_lower_higher_than_upper_expected, test_cu_invalid_aoi_expected, \
    test_cu_no_aoi, test_cu_no_aoi_expected, test_init_fields_1, test_init_fields_2, test_init_fields_3, \
    test_date_range_transform_1, test_date_range_transform_2, test_date_range_transform_1_expected, \
    test_date_range_transform_2_expected, test_cu_date_empty_dict, test_cu_date_empty_dict_expected, test_cu_2, \
    test_cu_3


@pytest.mark.parametrize("test_input,expected",
     [
         (test_cu, None),
         (test_cu_no_date, test_cu_no_date_expected),
         (test_cu_date_empty_dict, test_cu_date_empty_dict_expected),
         (test_cu_no_lower, test_cu_no_lower_expected),
         (test_cu_no_upper, test_cu_no_upper_expected),
         (test_cu_invalid_type, test_cu_invalid_type_expected),
         (test_cu_invalid_value, test_cu_invalid_value_expected),
         (test_cu_lower_higher_than_upper, test_cu_lower_higher_than_upper_expected),
         (test_cu_no_aoi, test_cu_no_aoi_expected),
         (test_cu_invalid_aoi, test_cu_invalid_aoi_expected),
     ])
def test_create_project_request_model(test_input: dict, expected: Optional[tuple]):
    from src.project.crud import CreateProjectRequestModel
    from pydantic_core import ValidationError
    raised = False
    try:
        CreateProjectRequestModel(**test_input)
    except ValidationError as e:
        raised = True
        assert e.errors()[0]['type'] == expected[0]
        assert e.errors()[0]['loc'] == expected[1]
        assert e.errors()[0]['msg'] == expected[2]
    if expected is None:
        assert raised == False


@pytest.mark.parametrize("test_input,expected",
     [
         (test_cu, None),
         (test_cu_no_date, None),
         (test_cu_no_lower, test_cu_no_lower_expected),
         (test_cu_no_upper, test_cu_no_upper_expected),
         (test_cu_invalid_type, test_cu_invalid_type_expected),
         (test_cu_invalid_value, test_cu_invalid_value_expected),
         (test_cu_lower_higher_than_upper,
          test_cu_lower_higher_than_upper_expected),
         (test_cu_no_aoi, None),
         (test_cu_invalid_aoi, test_cu_invalid_aoi_expected),
     ])
def test_update_project_request_model(test_input: dict, expected):
    from src.project.crud import UpdateProjectRequestModel
    from pydantic_core import ValidationError
    raised = False
    try:
        UpdateProjectRequestModel(**test_input)
    except ValidationError as e:
        raised = True
        assert e.errors()[0]['type'] == expected[0]
        assert e.errors()[0]['loc'] == expected[1]
        assert e.errors()[0]['msg'] == expected[2]
    if expected is None:
        assert raised == False

@pytest.mark.parametrize("test_input_expected",
     [
         test_init_fields_1,
         test_init_fields_2,
         test_init_fields_3,
     ])
def test_initialized_fields(test_input_expected):
    from src.project.crud import UpdateProjectRequestModel
    assert UpdateProjectRequestModel(**test_input_expected).initialized_fields() == test_input_expected

@pytest.mark.parametrize("test_input,expected",
     [
         (test_date_range_transform_1, test_date_range_transform_1_expected),
         (test_date_range_transform_2, test_date_range_transform_2_expected),
     ])
def test_transform_date_range(project_crud, test_input, expected):
    assert str(project_crud.transform_date_range(test_input)) == expected

@pytest.mark.parametrize("test_input",
     [
         test_cu,
         test_cu_2,
         test_cu_3
     ])
def test_insert(mock_session, project_crud, test_input):
    from src.project.crud import CreateProjectRequestModel
    new_project = CreateProjectRequestModel(**test_input)

    result = project_crud.insert(new_project)

    assert "New project added" in result["detail"]
    assert mock_session.internal_counter["add"] == 1
    assert mock_session.internal_counter["commit"] == 1

def test_get(mock_session, project_crud):
    result = project_crud.get("3c8e58d8-953d-41e6-a27c-29d0a228121b")
    assert result == {'id': '3c8e58d8-953d-41e6-a27c-29d0a228121b', 'name': None, 'description': None, 'date_range': None, 'area_of_interest': None, 'area_of_interest_geom': []}
    assert mock_session.internal_counter["query_filter_first"] == 1

@pytest.mark.parametrize("test_uuid, response_code",
     [
         ("test_uuid", 400),
         ("3c8e58d8-953d-41e6-a27c-29d0a228121b", 404),
     ])
def test_invalid_get(mock_session, project_crud, test_uuid, response_code):
    mock_session.return_empty = True
    try:
        project_crud.get(test_uuid)
    except HTTPException as e:
        assert e.status_code == response_code

def test_list(mock_session, project_crud):
    result = project_crud.list()
    assert result == [{'id': '3c8e58d8-953d-41e6-a27c-29d0a228121b', 'name': None, 'description': None, 'date_range': None, 'area_of_interest': None, 'area_of_interest_geom': []}, {'id': '3c8e58d8-953d-41e6-a27c-29d0a228123d', 'name': None, 'description': None, 'date_range': None, 'area_of_interest': None, 'area_of_interest_geom': []}]
    assert mock_session.internal_counter["query_all"] == 1

def test_delete(mock_session, project_crud):
    project_id = "3c8e58d8-953d-41e6-a27c-29d0a228121b"
    result = project_crud.delete(project_id)

    assert result["detail"] == f"Project {project_id} deleted"
    assert mock_session.internal_counter["delete"] == 1
    assert mock_session.internal_counter["commit"] == 1

def test_update(mock_session, project_crud):
    from src.project.crud import UpdateProjectRequestModel
    project_id = "3c8e58d8-953d-41e6-a27c-29d0a228121b"
    result = project_crud.update(project_id, UpdateProjectRequestModel(**test_init_fields_2))
    assert result["detail"] == f"Project {project_id} updated"
    assert mock_session.internal_counter["query_filter_first"] == 1
    assert mock_session.internal_counter["commit"] == 1
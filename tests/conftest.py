from unittest import mock

import pytest

class MockSession:
    def __init__(self):
        super().__init__()
        self.internal_counter = {}
        self.return_empty = False

    def __add_internal_count(self, function_name):
        if function_name not in self.internal_counter:
            self.internal_counter[function_name] = 1
            return
        self.internal_counter[function_name] += 1

    def add(self, *args, **kwargs):
        self.__add_internal_count("add")

    def commit(self):
        self.__add_internal_count("commit")

    def delete(self, *args, **kwargs):
        self.__add_internal_count("delete")
        from src.project.crud import ProjectGeneralEntity
        return ProjectGeneralEntity(**{'id': "3c8e58d8-953d-41e6-a27c-29d0a228121b"})

    def query(self, *args, **kwargs):
        return self

    def filter(self, *args, **kwargs):
        return self

    def first(self, *args, **kwargs):
        self.__add_internal_count("query_filter_first")
        from src.project.crud import ProjectGeneralEntity
        if self.return_empty:
            return None
        return ProjectGeneralEntity(**{'id': "3c8e58d8-953d-41e6-a27c-29d0a228121b"})

    def all(self, *args, **kwargs):
        self.__add_internal_count("query_all")
        from src.project.crud import ProjectGeneralEntity
        return [ProjectGeneralEntity(**{'id': "3c8e58d8-953d-41e6-a27c-29d0a228121b"}),
                ProjectGeneralEntity(**{'id': "3c8e58d8-953d-41e6-a27c-29d0a228123d"})]

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass

@pytest.fixture(autouse=True)
def set_env_vars(monkeypatch):
    # Set environment variables for tests
    monkeypatch.setenv('DB_HOST', 'test_host')
    monkeypatch.setenv('DB_PORT', '1234')
    monkeypatch.setenv('DB_NAME', 'test_name')
    monkeypatch.setenv('DB_USER', 'test_user')
    monkeypatch.setenv('DB_PASSWORD', 'test_pass')

@pytest.fixture
def mock_session():
    return MockSession()

@pytest.fixture
def project_crud(mock_session):
    from src.project.crud import ProjectCRUD
    return ProjectCRUD(sql_alchemy_session=mock.Mock(return_value=mock_session))
import pytest

from engine.tests.conftest import (
    JSON_FILE_SUBCLASSES,
    TEST_ROOT_FOLDER
)


@pytest.fixture(params=JSON_FILE_SUBCLASSES)
def model(request, monkeypatch):
    model = request.param
    monkeypatch.setattr(model, 'ROOT_FOLDER', TEST_ROOT_FOLDER, raising=True)
    return model


def test_initial_content_is_dictionary(model, path):
    json_file = model(path)
    initial_content = json_file._get_initial_content()
    assert isinstance(initial_content, dict)

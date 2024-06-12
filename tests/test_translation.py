from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from io import BytesIO

from src.database import Base
from src.main import app
from src.schemas.auth_schemas import UserRead
from src.services.auth_services import get_current_user
from src.utils import get_db
from src.services.ml_services import MLServices
from src.services.translation_services import GCPStorageServices
from tests.database import override_get_db, engine


@pytest.fixture(autouse=True)
def refresh_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)


@pytest.fixture()
def client_authenticated():
    def override_auth():
        return UserRead(id=1, username="johndoe")

    app.dependency_overrides[get_current_user] = override_auth
    return TestClient(app)


@pytest.fixture()
def client_not_authenticated():
    app.dependency_overrides[get_current_user] = get_current_user
    return TestClient(app)


def test_create_translation_success(client_authenticated, mocker, freezer):  # freeze time using freezer
    mocker.patch.object(MLServices, "do_translation", return_value="translation_text")
    mocker.patch.object(GCPStorageServices, "upload_file", return_value="https://video_url")

    video_file = ("video.mp4", BytesIO(b"video_file"), "video/mp4")

    response = client_authenticated.post(
        "api/v1/translations/",
        files={"file": video_file}
    )

    assert response.status_code == 201
    assert response.json()["user_id"] == 1
    assert response.json()["translation_text"] == "translation_text"
    assert response.json()["video_url"] == "https://video_url"
    assert response.json()["date_time_created"] == datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")
    assert response.json()["feedback"] is None


def test_create_translation_unauthorized(client_not_authenticated):
    video_file = ("video.mp4", BytesIO(b"video_file"), "video/mp4")
    response = client_not_authenticated.post(
        "api/v1/translations/",
        files={"file": video_file}
    )
    assert response.status_code == 401

# TODO belom exception buat videonya









from typing import Any

import pytest
from fastapi.testclient import TestClient

from imprint.api.app import create_app
from imprint.api.container import ApiContainer
from imprint.api.settings import ApiSettings
from imprint.core.container import CoreContainer
from imprint.core.settings import Settings


@pytest.fixture(scope="session")
async def core_settings() -> dict[str, Any]:
    return Settings().dict()


@pytest.fixture(scope="session")
async def api_settings() -> dict[str, Any]:
    return ApiSettings().dict()


@pytest.fixture(scope="session")
async def core_container(core_settings):
    yield CoreContainer(settings=core_settings)


@pytest.fixture(scope="session")
async def api_container(api_settings, core_container):
    yield ApiContainer(settings=api_settings, core_container=core_container)


@pytest.fixture(scope="session")
async def api_app(api_container):
    yield create_app(api_container)


@pytest.fixture(scope="session")
def rest_client(api_app):
    with TestClient(api_app) as c:
        yield c


@pytest.fixture(scope="session")
async def controllers(core_container):
    yield core_container.controllers


@pytest.fixture(scope="session")
async def imprint_controller(controllers):
    yield controllers.imprint()

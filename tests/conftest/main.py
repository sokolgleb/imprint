from typing import Any, AsyncGenerator

import pytest

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
async def core_container(
    core_settings: dict[str, Any],
) -> AsyncGenerator[CoreContainer, None]:
    container = CoreContainer(settings=core_settings)
    yield container


@pytest.fixture(scope="session")
async def api_container(
    api_settings: dict[str, Any],
    core_container: CoreContainer,
) -> AsyncGenerator[ApiContainer, None]:
    container = ApiContainer(
        settings=api_settings,
        core_container=core_container,
    )
    yield container


@pytest.fixture(scope="session")
async def api_app(api_container: ApiContainer):
    app = create_app(api_container)
    yield app

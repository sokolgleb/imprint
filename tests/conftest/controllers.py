import pytest

from imprint.core.container import (
    CoreContainer,
    ControllersContainer,
)


@pytest.fixture(scope="session", autouse=True)
def controllers(core_container: CoreContainer) -> ControllersContainer:
    return core_container.controllers()

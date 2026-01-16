from imprint.core.container import CoreContainer


async def test_container(core_container: CoreContainer):
    assert core_container

    assert core_container.controllers()

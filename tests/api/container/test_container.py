from imprint.api.container import ApiContainer


async def test_container(api_container: ApiContainer):
    assert api_container

    assert api_container.core_container

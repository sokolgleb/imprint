from fastapi import Request, Depends

from imprint.api.container import ApiContainer
from imprint.core.container import CoreContainer


async def api_container_dep(request: Request) -> ApiContainer:
    return request.app.container


async def core_container_dep(request: Request) -> CoreContainer:
    return request.app.container.core_container

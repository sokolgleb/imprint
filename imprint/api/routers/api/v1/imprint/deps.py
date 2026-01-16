from fastapi import Depends

from imprint.api.routers.api.v1.deps import core_container_dep
from imprint.core.container import CoreContainer
from imprint.core.controllers.imprint import ImprintController


def imprint_controller_dep(
    core_container: CoreContainer = Depends(core_container_dep),
) -> ImprintController:
    return core_container.controllers.imprint()

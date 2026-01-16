from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from imprint.core.container import CoreContainer


class ApiContainer(DeclarativeContainer):
    __self__: providers.Self["ApiContainer"] = providers.Self()
    settings = providers.Configuration()

    core_container = providers.Container(CoreContainer, settings=settings.core)

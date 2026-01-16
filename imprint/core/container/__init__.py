from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from imprint.core.container.controllers import ControllersContainer


class CoreContainer(DeclarativeContainer):
    __self__: providers.Self["CoreContainer"] = providers.Self()
    settings = providers.Configuration()

    controllers: ControllersContainer = providers.Container(
        ControllersContainer,
        settings=settings,
    )

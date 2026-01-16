from dependency_injector import providers
from dependency_injector.containers import DeclarativeContainer

from imprint.core.controllers.graphic_engine.base import GraphicEngineController
from imprint.core.controllers.imprint import ImprintController
from imprint.core.controllers.stego_crypt.base import StegoCryptController
from imprint.core.controllers.text_analyzer.base import TextAnalyzerController


class ControllersContainer(DeclarativeContainer):
    settings = providers.Configuration()

    text_analyzer = providers.Singleton(TextAnalyzerController)
    graphic_engine = providers.Singleton(GraphicEngineController)
    stego_crypt = providers.Singleton(StegoCryptController)
    imprint = providers.Singleton(
        ImprintController,
        text_analyzer_controller=text_analyzer,
        graphic_engine_controller=graphic_engine,
        stego_crypt_controller=stego_crypt,
    )

from fastapi import FastAPI

from .container import ApiContainer
from .routers.api.v1._router import api_v1_router
from .settings import ApiSettings


def create_app(container: ApiContainer | None = None) -> FastAPI:
    if not container:
        container = ApiContainer()
        container.settings.from_pydantic(ApiSettings())

    app = FastAPI(title="ImPrint API", version="0.1.0")

    app.container = container

    app.include_router(api_v1_router)

    return app

from io import BytesIO

from fastapi import APIRouter, Depends, Response
from fastapi.concurrency import run_in_threadpool

from imprint.api.routers.api.v1.imprint.deps import imprint_controller_dep
from imprint.api.routers.api.v1.imprint.schemas import CreateImprintRequest
from imprint.core.controllers.imprint import ImprintController

imprint_router = APIRouter(prefix="/imprint", tags=["Imprint"])


@imprint_router.post(
    "",
    name="create_imprint",
)
async def create_imprint(
    request: CreateImprintRequest,
    imprint_controller: ImprintController = Depends(imprint_controller_dep),
):

    image = await run_in_threadpool(
        imprint_controller.create,
        text=request.text,
        password=request.password,
    )

    buffer = BytesIO()
    image.save(buffer, format="PNG")

    return Response(content=buffer.getvalue(), media_type="image/png")

import io
from http import HTTPStatus
from io import BytesIO
from typing import Annotated

from fastapi import APIRouter, Depends, File, Form, HTTPException, Response, UploadFile
from fastapi.concurrency import run_in_threadpool
from PIL import Image

from imprint.api.routers.api.v1.imprint.deps import imprint_controller_dep
from imprint.api.routers.api.v1.imprint.schemas import (
    CreateImprintRequest,
    ParseImprintResponse,
)
from imprint.core.controllers.imprint import ImprintController

imprint_router = APIRouter(prefix="/imprint", tags=["Imprint"])


@imprint_router.post("", name="create_imprint")
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


@imprint_router.post(
    "/parse",
    name="parse_imprint",
    response_model=ParseImprintResponse,
)
async def parse_imprint(
    file: Annotated[UploadFile, File()],
    password: Annotated[str | None, Form()] = None,
    imprint_controller: ImprintController = Depends(imprint_controller_dep),
):
    if file.content_type != "image/png":
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid content type",
        )

    content = await file.read()

    try:
        image = Image.open(io.BytesIO(content))
        image.verify()

        image = Image.open(io.BytesIO(content))

        text = imprint_controller.parse(image, password)

        return ParseImprintResponse(text=text)

    except Exception:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail="Invalid image",
        )

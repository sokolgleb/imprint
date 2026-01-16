from pydantic import BaseModel


class CreateImprintRequest(BaseModel):
    text: str
    password: str | None = None

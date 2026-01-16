from pydantic import Field
from pydantic_settings import BaseSettings

from imprint.core.settings import Settings


class ApiSettings(BaseSettings):
    core: Settings = Field(default_factory=Settings)

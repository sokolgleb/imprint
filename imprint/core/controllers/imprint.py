from typing import Optional

from PIL import Image

from imprint.core.controllers.graphic_engine.base import GraphicEngineController
from imprint.core.controllers.graphic_engine.drawers.base import DrawSettings
from imprint.core.controllers.stego_crypt.base import StegoCryptController
from imprint.core.controllers.text_analyzer.base import (
    TextAnalyzerController,
    TextMetrics,
)


class ImprintController:

    def __init__(
        self,
        text_analyzer_controller: TextAnalyzerController,
        graphic_engine_controller: GraphicEngineController,
        stego_crypt_controller: StegoCryptController,
    ):
        self.text_analyzer_controller = text_analyzer_controller
        self.graphic_engine_controller = graphic_engine_controller
        self.stego_crypt_controller = stego_crypt_controller

    def create(
        self,
        text: str,
        password: Optional[str] = None,
        drawers=None,
    ) -> Image.Image:
        metrics: TextMetrics = self.text_analyzer_controller.analyze(text)
        image: Image.Image = self.graphic_engine_controller.draw(
            DrawSettings(
                hash=metrics.hash,
                canvas_size=metrics.canvas_size,
                chars_stats=metrics.chars_stats,
                symbols_count=metrics.symbols_count,
            ),
            drawers=drawers,
        )
        stego_image: Image.Image = self.stego_crypt_controller.encode(
            image,
            text,
            password,
        )

        # import time
        # file_name = f"{int(time.time() * 1000)}.png"
        # stego_image.convert("RGB").save(file_name, "PNG")

        return stego_image

    def parse(self, image: Image, password: Optional[str] = None) -> str:
        image = image.convert("RGB")
        return self.stego_crypt_controller.decode(image, password)

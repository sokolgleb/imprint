import time
from typing import Optional

from PIL import Image

from graphic_engine.base import GraphicEngine, DrawSettings
from stego_crypt.stego_crypt import StegoCrypt
from text_analyzer.text_analyzer import TextAnalyzer, TextMetrics


class Imprint:

    def __init__(
        self,
        text_analyzer_service: TextAnalyzer,
        graphic_engine_service: GraphicEngine,
        stego_crypt_service: StegoCrypt,
    ):
        self.text_analyzer_service = text_analyzer_service
        self.graphic_engine_service = graphic_engine_service
        self.stego_crypt_service = stego_crypt_service

    def create(self, text: str, password: Optional[str] = None) -> str:
        metrics: TextMetrics = self.text_analyzer_service.analyze(text)
        image: Image.Image = self.graphic_engine_service.draw(
            DrawSettings(
                hash=metrics.hash,
                canvas_size=metrics.canvas_size,
                chars_stats=metrics.chars_stats,
                symbols_count=metrics.symbols_count,
            )
        )
        stego_image: Image.Image = self.stego_crypt_service.encode(
            image, text, password
        )

        file_name = f"{int(time.time() * 1000)}.png"
        stego_image.convert("RGB").save(file_name, "PNG")

        return file_name

    def parse(self, image_path: str, password: Optional[str] = None) -> str:
        image = Image.open(image_path).convert("RGB")
        return self.stego_crypt_service.decode(image, password)


if __name__ == "__main__":
    text_analyzer = TextAnalyzer()
    graphic_engine = GraphicEngine()
    stego_crypt = StegoCrypt()

    imprint = Imprint(text_analyzer, graphic_engine, stego_crypt)

    text = "Hello, world!"
    password = "123"
    filename = imprint.create(text, password)

    parsed_text = imprint.parse(filename, password)

    assert text == parsed_text

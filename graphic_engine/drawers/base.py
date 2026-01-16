import colorsys
from typing import Optional

from PIL import ImageDraw
from pydantic import BaseModel


class DrawSettings(BaseModel):
    hash: str
    canvas_size: int
    symbols_count: int
    chars_stats: list[tuple]

    @property
    def scale_factor(self):
        return self.canvas_size / 1000

    @property
    def bytes_list(self):
        return [int(self.hash[i : i + 2], 16) for i in range(0, len(self.hash), 2)]


class DrawerBase:

    def __init__(
        self,
        color: Optional[str] = None,
        alpha: int = 128,
        line_width: Optional[float] = None,
        density: Optional[int] = None,
    ):
        self.color = color
        self.alpha = alpha
        self.line_width = line_width
        self.density = density

    def get_base_color_from_hash(self, bytes_list: list[int]):
        return (bytes_list[0] * 1.41) % 360

    @staticmethod
    def get_rgb_color(h, s, v):
        rgb = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
        return tuple(int(c * 255) for c in rgb)

    def draw(
        self,
        canvas: ImageDraw,
        draw_settings: DrawSettings,
        **kwargs,
    ) -> ImageDraw:
        raise NotImplementedError

import colorsys
from typing import Optional

from PIL import ImageColor, ImageDraw
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

    name: str = None

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

    def get_base_hue_color(self, bytes_list: list[int]):
        hash_sum = sum(bytes_list[i] for i in range(0, len(bytes_list), 4))
        base_hue = hash_sum % 360

        if self.color is not None:
            if isinstance(self.color, str):
                try:
                    rgb = ImageColor.getrgb(self.color)
                    import colorsys

                    h, s, v = colorsys.rgb_to_hsv(
                        rgb[0] / 255, rgb[1] / 255, rgb[2] / 255
                    )
                    base_hue = h * 360
                except Exception:
                    ...
            else:
                # Если передан кортеж (R, G, B)
                import colorsys

                h, s, v = colorsys.rgb_to_hsv(
                    self.color[0] / 255,
                    self.color[1] / 255,
                    self.color[2] / 255,
                )
                base_hue = h * 360

        return base_hue

    @staticmethod
    def get_rgb_base_color(h, s, v):
        rgb = colorsys.hsv_to_rgb(h / 360.0, s / 100.0, v / 100.0)
        return tuple(int(c * 255) for c in rgb)

    def draw(
        self,
        canvas: ImageDraw,
        draw_settings: DrawSettings,
        **kwargs,
    ) -> ImageDraw:
        raise NotImplementedError

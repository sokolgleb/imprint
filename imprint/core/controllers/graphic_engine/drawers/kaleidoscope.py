import math
import random
from typing import Optional

from PIL import ImageDraw

from imprint.core.controllers.graphic_engine.drawers.base import (
    DrawerBase,
    DrawSettings,
)


class KaleidoscopeDrawer(DrawerBase):
    name = "kaleidoscope"

    def __init__(
        self,
        color: Optional[str] = None,
        alpha: int = 255,
        line_width: Optional[float] = 2.0,
        density: Optional[int] = 800,
    ):
        super().__init__(
            color=color,
            alpha=alpha,
            line_width=line_width,
            density=density,
        )

    def draw(
        self, canvas: ImageDraw, draw_settings: DrawSettings, **kwargs
    ) -> ImageDraw:
        center_x = center_y = draw_settings.canvas_size // 2
        base_hue = self.get_base_color_from_hash(draw_settings.bytes_list)
        line_width = max(1, int(self.line_width * draw_settings.scale_factor))

        if self.color is None:
            pattern_rgb = self.get_rgb_color(base_hue, 90, 60)
        else:
            pattern_rgb = (
                ImageDraw._color_diff(self.color, "RGB")
                if isinstance(self.color, str)
                else self.color
            )

        rgba_pattern = (*pattern_rgb[:3], self.alpha)

        seed = int(draw_settings.hash, 16) % (2**32)
        rng = random.Random(seed)
        num_sectors = 4 + (draw_settings.bytes_list[0] % 9)
        angle_step = 2 * math.pi / num_sectors
        curr_x, curr_y = (
            draw_settings.canvas_size * 0.02,
            draw_settings.canvas_size * 0.02,
        )
        step_dist = 9 * draw_settings.scale_factor

        for _ in range(self.density):
            angle = rng.uniform(0, 2 * math.pi)
            prev_x, prev_y = curr_x, curr_y
            curr_x += math.cos(angle) * step_dist
            curr_y += math.sin(angle) * step_dist

            for i in range(num_sectors):
                sector_angle = i * angle_step

                def rotate(px, py, a):
                    return px * math.cos(a) - py * math.sin(a), px * math.sin(
                        a
                    ) + py * math.cos(a)

                x1, y1 = rotate(prev_x, prev_y, sector_angle)
                x2, y2 = rotate(curr_x, curr_y, sector_angle)
                start_p = (x1 + center_x, y1 + center_y)
                end_p = (x2 + center_x, y2 + center_y)

                canvas.line([start_p, end_p], fill=rgba_pattern, width=line_width)

            if math.hypot(curr_x, curr_y) > (draw_settings.canvas_size * 0.45):
                curr_x, curr_y = prev_x, prev_y

        return canvas

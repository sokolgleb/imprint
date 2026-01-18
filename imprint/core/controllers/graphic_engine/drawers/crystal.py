import math
import random
from typing import Optional

from PIL import ImageDraw

from imprint.core.controllers.graphic_engine.drawers.base import (
    DrawerBase,
    DrawSettings,
)


class CrystalDrawer(DrawerBase):
    name = "crystal"

    def __init__(
        self,
        color: Optional[str] = None,
        alpha: int = 180,
        line_width: Optional[float] = 0.5,
    ):
        super().__init__(
            color=color,
            alpha=alpha,
            line_width=line_width,
        )

    def draw(
        self,
        canvas: ImageDraw,
        draw_settings: DrawSettings,
        **kwargs,
    ) -> ImageDraw:
        center_x = center_y = draw_settings.canvas_size // 2
        base_hue = self.get_base_hue_color(draw_settings.bytes_list)
        core_rgb = self.get_rgb_base_color(base_hue, 90, 60)

        line_width = max(1, int(self.line_width * draw_settings.scale_factor))
        max_radius = (draw_settings.canvas_size // 2) * 0.85
        current_angle = 0.0
        seed = int(draw_settings.hash, 16) % (2**32)
        rng = random.Random(seed)

        for i, (char, count) in enumerate(draw_settings.chars_stats):
            percentage = count / draw_settings.symbols_count
            angle_sweep = percentage * 360
            s_val, v_val = max(0, min(100, 40 + (i % 20))), 90

            rgb_base = self.get_rgb_base_color(base_hue, s_val, v_val)
            rgba_crystal = (*rgb_base, self.alpha)

            num_rays = int(
                60 * (1 + 0.3 * math.log10(max(1, draw_settings.symbols_count)))
            )
            radius = min(max_radius * (percentage * 10), max_radius)

            for _ in range(min(num_rays, 800)):
                rad_angle = math.radians(
                    rng.uniform(current_angle, current_angle + angle_sweep)
                )
                length = radius * rng.uniform(0.7, 1.1)
                x_end = center_x + math.cos(rad_angle) * length
                y_end = center_y + math.sin(rad_angle) * length

                canvas.line(
                    [(center_x, center_y), (x_end, y_end)],
                    fill=rgba_crystal,
                    width=line_width,
                )

            current_angle += angle_sweep

        return canvas

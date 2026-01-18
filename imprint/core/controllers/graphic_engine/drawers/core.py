import math
from typing import Optional

from PIL import ImageDraw

from imprint.core.controllers.graphic_engine.drawers.base import (
    DrawerBase,
    DrawSettings,
)


class CoreDrawer(DrawerBase):
    name = "core"

    def __init__(self, color: Optional[str] = None, alpha: int = 200):
        super().__init__(color=color, alpha=alpha)

    def draw(
        self,
        canvas: ImageDraw,
        draw_settings: DrawSettings,
        **kwargs,
    ) -> ImageDraw:
        center_x = center_y = draw_settings.canvas_size // 2
        base_hue = self.get_base_hue_color(draw_settings.bytes_list)
        core_rgb = self.get_rgb_base_color(base_hue, 90, 60)

        rgba_core = (*core_rgb[:3], self.alpha)
        core_radius = int(
            25
            * draw_settings.scale_factor
            * (1 + math.log10(max(1, draw_settings.symbols_count)))
        )

        # Рисуем круг в Pillow
        canvas.ellipse(
            [
                center_x - core_radius,
                center_y - core_radius,
                center_x + core_radius,
                center_y + core_radius,
            ],
            fill=rgba_core,
        )

        return canvas

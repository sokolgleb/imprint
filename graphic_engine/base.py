from PIL import Image, ImageDraw

from graphic_engine.drawers.base import DrawerBase, DrawSettings
from graphic_engine.drawers.core import CoreDrawer
from graphic_engine.drawers.crystal import CrystalDrawer
from graphic_engine.drawers.kaleidoscope import KaleidoscopeDrawer


class GraphicEngine:

    def __init__(self, default_drawers: list[DrawerBase] = None):
        if not default_drawers:
            default_drawers = [CrystalDrawer(), CoreDrawer(), KaleidoscopeDrawer()]

        self.default_drawers = default_drawers

    def draw(
        self,
        draw_settings: DrawSettings,
        drawers: list[DrawerBase] = None,
    ) -> Image:
        main_img = Image.new(
            "RGBA",
            (draw_settings.canvas_size, draw_settings.canvas_size),
            (255, 255, 255, 255),
        )
        overlay = Image.new(
            "RGBA", (draw_settings.canvas_size, draw_settings.canvas_size), (0, 0, 0, 0)
        )
        canvas = ImageDraw.Draw(overlay)

        for drawer in drawers or self.default_drawers:
            canvas = drawer.draw(canvas, draw_settings)

        return Image.alpha_composite(main_img, overlay)

import collections
import colorsys
import math
import random
import time
from typing import Optional

from PIL import Image, ImageDraw
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


class CrystalDrawer(DrawerBase):

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
        base_hue = self.get_base_color_from_hash(draw_settings.bytes_list)
        line_width = max(1, int(self.line_width * draw_settings.scale_factor))
        max_radius = (draw_settings.canvas_size // 2) * 0.85
        current_angle = 0.0

        for i, (char, count) in enumerate(draw_settings.chars_stats):
            percentage = count / draw_settings.symbols_count
            angle_sweep = percentage * 360
            s_val, v_val = max(0, min(100, 40 + (i % 20))), 90

            rgb_base = self.get_rgb_color(base_hue, s_val, v_val)
            rgba_crystal = (*rgb_base, self.alpha)

            num_rays = int(
                60 * (1 + 0.3 * math.log10(max(1, draw_settings.symbols_count)))
            )
            radius = min(max_radius * (percentage * 10), max_radius)

            for _ in range(min(num_rays, 800)):
                rad_angle = math.radians(
                    random.uniform(current_angle, current_angle + angle_sweep)
                )
                length = radius * random.uniform(0.7, 1.1)
                x_end = center_x + math.cos(rad_angle) * length
                y_end = center_y + math.sin(rad_angle) * length

                canvas.line(
                    [(center_x, center_y), (x_end, y_end)],
                    fill=rgba_crystal,
                    width=line_width,
                )

            current_angle += angle_sweep

        return canvas


class CoreDrawer(DrawerBase):

    def __init__(self, color: Optional[str] = None, alpha: int = 76):
        super().__init__(color=color, alpha=alpha)

    def draw(
        self,
        canvas: ImageDraw,
        draw_settings: DrawSettings,
        **kwargs,
    ) -> ImageDraw:
        center_x = center_y = draw_settings.canvas_size // 2
        base_hue = self.get_base_color_from_hash(draw_settings.bytes_list)

        if self.color is None:
            core_rgb = self.get_rgb_color(base_hue, 90, 60)
        else:
            # Если цвет задан строкой (напр. 'red'), Pillow его поймет
            core_rgb = (
                ImageDraw._color_diff(self.color, "RGB")
                if isinstance(self.color, str)
                else self.color
            )

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


class KaleidoscopeDrawer(DrawerBase):

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


if __name__ == "__main__":
    hashes = [
        "23844022601385088e4966aa08851486",
        "473f76a0eed32deea5dd6dc94c0d75fa",
        "473f66a0ec932deca5dd6d6dc80d659a",
        "323ee3000a9590d321e60593d699b45",
    ]

    graphic_engine = GraphicEngine()
    for h in hashes:
        text = "Привет"
        char_stats = collections.Counter(text)
        sorted(char_stats.items(), key=lambda item: ord(item[0]))

        for drawers in [
            [CrystalDrawer(), CoreDrawer(), KaleidoscopeDrawer()],
        ]:
            image = graphic_engine.draw(
                DrawSettings(
                    hash=h,
                    canvas_size=2000,
                    chars_stats=char_stats.items(),
                    symbols_count=len(text),
                ),
                drawers=drawers,
            )

            image.convert("RGB").save(f"{int(time.time() * 1000)}.png", "PNG")

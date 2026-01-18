import colorsys
import math
import random
from typing import Optional

from PIL import ImageColor, ImageDraw

from imprint.core.controllers.graphic_engine.drawers.base import (
    DrawerBase,
    DrawSettings,
)


class GenesisDrawer(DrawerBase):
    name = "genesis"

    def __init__(
        self,
        color: Optional[str] = None,
        alpha: int = 255,
        line_width: Optional[float] = 2.0,
    ):
        super().__init__(
            color=color,
            alpha=alpha,
            line_width=line_width,
        )

    def draw(
        self, canvas: ImageDraw, draw_settings: DrawSettings, **kwargs
    ) -> ImageDraw:
        center_x = center_y = draw_settings.canvas_size // 2
        line_width = max(1, int(self.line_width * draw_settings.scale_factor))
        sc = draw_settings.symbols_count if draw_settings.symbols_count > 0 else 1

        # Динамические параметры
        final_density = max(300, min(1000, 300 + 50 * int(math.log(sc, 3))))
        num_sectors = max(4, min(18, 4 + int(math.log(sc, 4))))
        angle_step = 2 * math.pi / num_sectors
        max_radius = draw_settings.canvas_size * 0.45

        # Логика цвета (Hue)
        if self.color:
            rgb = (
                ImageColor.getrgb(self.color)
                if isinstance(self.color, str)
                else self.color
            )
            h, s, v = colorsys.rgb_to_hsv(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255)
            base_hue = h * 360
        else:
            # Тот самый "хитрый" хэш каждого 4-го байта
            hash_sum = sum(
                draw_settings.bytes_list[i]
                for i in range(0, len(draw_settings.bytes_list), 4)
            )
            base_hue = hash_sum % 360

        # --- ГЕНЕРАЦИЯ ПУТИ С НАСЛЕДОВАНИЕМ ---
        hex_hash = draw_settings.hash
        chunks = [hex_hash[i : i + 4] for i in range(0, len(hex_hash), 4)]
        points_per_chunk = 50  # Фиксированный шаг, чтобы старые линии не двигались

        path_points = [
            (draw_settings.canvas_size * 0.05, draw_settings.canvas_size * 0.05)
        ]
        curr_x, curr_y = path_points[0]
        step_dist = 12 * draw_settings.scale_factor

        points_drawn = 0
        for chunk in chunks:
            if points_drawn >= final_density:
                break
            chunk_rng = random.Random(int(chunk, 16))

            for _ in range(points_per_chunk):
                if points_drawn >= final_density:
                    break
                angle = chunk_rng.uniform(0, 2 * math.pi)
                new_x = curr_x + math.cos(angle) * step_dist
                new_y = curr_y + math.sin(angle) * step_dist

                if math.hypot(new_x, new_y) < max_radius:
                    curr_x, curr_y = new_x, new_y
                    path_points.append((curr_x, curr_y))
                points_drawn += 1

        # --- ОТРИСОВКА ---
        for i in range(num_sectors):
            sector_angle = i * angle_step
            rotated = []
            for px, py in path_points:
                rx = px * math.cos(sector_angle) - py * math.sin(sector_angle)
                ry = px * math.sin(sector_angle) + py * math.cos(sector_angle)
                rotated.append((rx + center_x, ry + center_y))

            if len(rotated) < 3:
                continue

            for j in range(1, len(rotated) - 1):
                p0, p1, p2 = rotated[j - 1], rotated[j], rotated[j + 1]
                steps = 4
                for t_idx in range(steps):
                    t, t_n = t_idx / steps, (t_idx + 1) / steps

                    def get_bezier(time):
                        m1x, m1y = (p0[0] + p1[0]) / 2, (p0[1] + p1[1]) / 2
                        m2x, m2y = (p1[0] + p2[0]) / 2, (p1[1] + p2[1]) / 2
                        return (1 - time) * m1x + time * m2x, (
                            1 - time
                        ) * m1y + time * m2y

                    ps, pe = get_bezier(t), get_bezier(t_n)

                    # Градиент: темный/насыщенный в центре -> светлый/прозрачный по краям
                    dist = math.hypot(ps[0] - center_x, ps[1] - center_y)
                    ratio = min(1.0, dist / max_radius)

                    sat = 100 - (ratio * 70)
                    val = 40 + (ratio * 60)
                    alpha = int(self.alpha * (1.0 - ratio * 0.8))

                    rgb = [
                        int(x * 255)
                        for x in colorsys.hsv_to_rgb(
                            base_hue / 360, sat / 100, val / 100
                        )
                    ]
                    canvas.line([ps, pe], fill=(*rgb, alpha), width=line_width)

        return canvas

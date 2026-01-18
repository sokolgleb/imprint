import math
import random
from typing import Optional

from PIL import ImageDraw

from imprint.core.controllers.graphic_engine.drawers.base import (
    DrawerBase,
    DrawSettings,
)


class FlowDrawer(DrawerBase):
    name = "flow"

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

        dynamic_density = 300 + 50 * int(math.log(sc, 3))

        final_density = max(300, min(1000, int(dynamic_density)))

        # Определение цвета
        if self.color is None:
            base_hue = self.get_base_color_from_hash(draw_settings.bytes_list)
            pattern_rgb = self.get_rgb_color(base_hue, 90, 60)
        else:
            pattern_rgb = (
                ImageDraw._color_diff(self.color, "RGB")
                if isinstance(self.color, str)
                else self.color
            )
        rgba_pattern = (*pattern_rgb[:3], self.alpha)

        # Параметры генерации
        seed = int(draw_settings.hash, 16) % (2**32)
        rng = random.Random(seed)

        step_dist = 12 * draw_settings.scale_factor

        # num_sectors = 4 + (draw_settings.bytes_list[0] % 9)
        dynamic_sectors = 4 + int(math.log(sc, 4))
        num_sectors = max(4, min(18, dynamic_sectors))

        angle_step = 2 * math.pi / num_sectors

        # 1. Генерируем "скелет" пути (набор точек одного сектора)
        path_points = [
            (draw_settings.canvas_size * 0.05, draw_settings.canvas_size * 0.05)
        ]
        curr_x, curr_y = path_points[0]

        for _ in range(final_density):
            angle = rng.uniform(0, 2 * math.pi)
            new_x = curr_x + math.cos(angle) * step_dist
            new_y = curr_y + math.sin(angle) * step_dist

            # Ограничение радиуса
            if math.hypot(new_x, new_y) < (draw_settings.canvas_size * 0.45):
                curr_x, curr_y = new_x, new_y
                path_points.append((curr_x, curr_y))

        # 2. Отрисовка сглаженных путей для каждого сектора
        for i in range(num_sectors):
            sector_angle = i * angle_step

            # Трансформируем и сглаживаем точки "на лету"
            rotated_points = []
            for px, py in path_points:
                # Поворот
                rx = px * math.cos(sector_angle) - py * math.sin(sector_angle)
                ry = px * math.sin(sector_angle) + py * math.cos(sector_angle)
                # Смещение к центру
                rotated_points.append((rx + center_x, ry + center_y))

            # Сглаживание: создаем кривую через средние точки (Quadratic Spline)
            if len(rotated_points) > 2:
                smoothed_path = [rotated_points[0]]
                for j in range(1, len(rotated_points) - 1):
                    p0 = rotated_points[j]
                    p1 = rotated_points[j + 1]

                    # Генерируем промежуточные точки кривой между p0 и p1
                    # используя p0 как контрольную точку
                    for t_step in range(1, 5):
                        t = t_step / 4
                        # Берем среднюю точку как целевую для плавности
                        mid_x = (p0[0] + p1[0]) / 2
                        mid_y = (p0[1] + p1[1]) / 2

                        # Упрощенная интерполяция для эффекта скругления
                        last_p = smoothed_path[-1]
                        qx = (
                            (1 - t) ** 2 * last_p[0]
                            + 2 * (1 - t) * t * p0[0]
                            + t**2 * mid_x
                        )
                        qy = (
                            (1 - t) ** 2 * last_p[1]
                            + 2 * (1 - t) * t * p0[1]
                            + t**2 * mid_y
                        )
                        smoothed_path.append((qx, qy))

                # Рисуем всю кривую целиком одним методом
                canvas.line(
                    smoothed_path, fill=rgba_pattern, width=line_width, joint="curve"
                )

        return canvas

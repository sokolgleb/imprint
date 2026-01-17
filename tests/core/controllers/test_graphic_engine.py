import pytest

from imprint.core.controllers.graphic_engine.drawers.core import CoreDrawer
from imprint.core.controllers.graphic_engine.drawers.crystal import CrystalDrawer
from imprint.core.controllers.graphic_engine.drawers.flow import FlowDrawer
from imprint.core.controllers.graphic_engine.drawers.kaleidoscope import (
    KaleidoscopeDrawer,
)

crystal_drawer = CrystalDrawer()
core_drawer = CoreDrawer()
kaleidoscope_drawer = KaleidoscopeDrawer(density=500)
flow_drawer = FlowDrawer()


@pytest.mark.parametrize(
    ["drawers"],
    [
        [
            [
                crystal_drawer,
                core_drawer,
                kaleidoscope_drawer,
            ]
        ],
        [
            [
                crystal_drawer,
                core_drawer,
                flow_drawer,
            ]
        ],
    ],
)
def test_drawers_with_text(
    imprint_controller,
    drawers,
):
    for text in [
        "Привет!",
        "Пока",
        "Привет! Как дела?",
        "Привет! Как дела?" * 100,
    ]:
        image = imprint_controller.create(text, password=None, drawers=drawers)

        file_name = f"{text[:10]}___{'_'.join([d.name for d in drawers])}.png"
        image.convert("RGB").save(file_name, "PNG")

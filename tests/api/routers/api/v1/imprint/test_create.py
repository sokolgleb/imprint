import io

import pytest
from PIL import Image


@pytest.mark.parametrize(
    ["text", "password"],
    [
        ["Hello, world!", None],
        ["Hello, world!", "test"],
        ["Hello, world!" * 10, None],
        ["Hello, world!" * 10, "test_password"],
        ["Hello, world!" * 1000, None],
        ["Hello, world!" * 1000, "test_password_new"],
    ],
)
def test_create_imprint_success(rest_client, text, password):
    payload = {"text": text, "password": password}
    response = rest_client.post("/api/v1/imprint/", json=payload)

    assert response.status_code == 200
    assert response.headers["content-type"] == "image/png"

    image_bytes = response.content
    image = Image.open(io.BytesIO(image_bytes))

    assert image.format == "PNG"
    assert image.width > 0
    assert image.height > 0

    image.save("test_output.png")

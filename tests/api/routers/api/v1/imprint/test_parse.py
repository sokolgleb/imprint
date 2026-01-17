import io

import pytest


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
def test_parse_imprint_success(rest_client, text, password):
    payload = {"text": text, "password": password}
    create_response = rest_client.post("/api/v1/imprint/", json=payload)
    assert create_response.status_code == 200

    image_bytes = create_response.content
    files = {"file": ("imprint.png", io.BytesIO(image_bytes), "image/png")}
    data = {"password": password}

    parse_response = rest_client.post("/api/v1/imprint/parse", files=files, data=data)

    assert parse_response.status_code == 200
    result = parse_response.json()
    assert result["text"] == text

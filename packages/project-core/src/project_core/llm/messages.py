from __future__ import annotations

import base64
from pathlib import Path
from typing import Any

from PIL import Image, UnidentifiedImageError


_IMAGE_MIME_TYPES = {
    "PNG": "image/png",
    "JPEG": "image/jpeg",
    "WEBP": "image/webp",
    "GIF": "image/gif",
}


def encode_image_data_url(path: Path, *, max_image_bytes: int | None = None) -> str:
    resolved = path.resolve(strict=True)
    size = resolved.stat().st_size
    if size <= 0:
        raise ValueError("image file is empty")
    if max_image_bytes is not None and size > max_image_bytes:
        raise ValueError("image exceeds byte limit")
    try:
        with Image.open(resolved) as image:
            image.verify()
            mime = _IMAGE_MIME_TYPES.get(str(image.format).upper())
    except (UnidentifiedImageError, OSError, SyntaxError) as exc:
        raise ValueError("image is not decodable") from exc
    if mime is None:
        raise ValueError("unsupported image format")
    b64 = base64.standard_b64encode(resolved.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def text_content(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def image_url_content(data_url: str) -> dict[str, Any]:
    return {"type": "image_url", "image_url": {"url": data_url}}


def build_user_message(
    text: str,
    image_paths: list[Path] | None = None,
    *,
    max_image_bytes: int | None = None,
) -> dict[str, Any]:
    if not image_paths:
        return {"role": "user", "content": text}
    parts: list[dict[str, Any]] = [text_content(text)]
    for path in image_paths:
        parts.append(
            image_url_content(encode_image_data_url(path, max_image_bytes=max_image_bytes))
        )
    return {"role": "user", "content": parts}

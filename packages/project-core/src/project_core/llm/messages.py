from __future__ import annotations

import base64
import mimetypes
from pathlib import Path
from typing import Any


def encode_image_data_url(path: Path) -> str:
    mime, _ = mimetypes.guess_type(str(path))
    if not mime:
        mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def text_content(text: str) -> dict[str, Any]:
    return {"type": "text", "text": text}


def image_url_content(data_url: str) -> dict[str, Any]:
    return {"type": "image_url", "image_url": {"url": data_url}}


def build_user_message(text: str, image_paths: list[Path] | None = None) -> dict[str, Any]:
    if not image_paths:
        return {"role": "user", "content": text}
    parts: list[dict[str, Any]] = [text_content(text)]
    for path in image_paths:
        parts.append(image_url_content(encode_image_data_url(path)))
    return {"role": "user", "content": parts}

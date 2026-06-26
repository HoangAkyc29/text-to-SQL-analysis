"""Test khả năng đọc ảnh qua OpenRouter (theo mẫu sample_API_code.py)."""

import base64
import json
import os
import sys
from pathlib import Path

import requests

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

ROOT = Path(__file__).resolve().parent
IMAGE_PATH = ROOT / "image.png"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "xiaomi/mimo-v2.5"

PROMPT = """Bạn có thể nhìn thấy ảnh đính kèm không?
Hãy trả lời bằng tiếng Việt và mô tả chi tiết:
1) Nhân vật đang cầm gì?
2) Màu tóc và trang phục nổi bật?
3) Có chữ/dấu hiệu gì ở dưới ảnh không?
Nếu không nhìn được ảnh, hãy nói rõ là không nhìn được."""


def load_api_key() -> str:
    env_path = ROOT / ".env"
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ[key.strip()] = value.strip()
    api_key = os.environ.get("openroute_api_key") or os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("Thiếu openroute_api_key trong .env")
    return api_key


def image_to_data_url(path: Path) -> str:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.standard_b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def main() -> None:
    if not IMAGE_PATH.exists():
        raise FileNotFoundError(f"Không tìm thấy {IMAGE_PATH}")

    api_key = load_api_key()
    data_url = image_to_data_url(IMAGE_PATH)

    payload = {
        "model": MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
        "reasoning": {"enabled": True},
    }

    print(f"Model: {MODEL}")
    print(f"Ảnh: {IMAGE_PATH.name}")
    print("Đang gọi API...\n")

    response = requests.post(
        url=OPENROUTER_URL,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=120,
    )

    if not response.ok:
        print(f"Lỗi HTTP {response.status_code}")
        try:
            print(json.dumps(response.json(), ensure_ascii=False, indent=2))
        except json.JSONDecodeError:
            print(response.text)
        return

    message = response.json()["choices"][0]["message"]
    print("--- TRẢ LỜI MODEL ---")
    print(message.get("content") or "(không có content)")

    reasoning = message.get("reasoning") or message.get("reasoning_details")
    if reasoning:
        print("\n--- REASONING ---")
        if isinstance(reasoning, str):
            print(reasoning[:1500])
        else:
            print(json.dumps(reasoning, ensure_ascii=False, indent=2)[:1500])


if __name__ == "__main__":
    main()

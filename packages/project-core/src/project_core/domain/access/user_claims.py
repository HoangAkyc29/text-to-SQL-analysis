from __future__ import annotations

from typing import Any


def normalize_store_ids(raw: Any) -> list[int] | None:
    if raw is None:
        return None
    if isinstance(raw, list):
        out: list[int] = []
        for item in raw:
            if item is None or item == "":
                continue
            out.append(int(item))
        return out or None
    if isinstance(raw, str):
        parts = [p.strip() for p in raw.split(",") if p.strip()]
        return [int(p) for p in parts] if parts else None
    return [int(raw)]


def claims_from_user_dict(user: dict[str, Any]) -> tuple[str, str, list[int] | None]:
    actor_id = str(user["sub"])
    role = str(user.get("role") or "hq_analyst")
    store_ids = normalize_store_ids(user.get("store_ids"))
    return actor_id, role, store_ids

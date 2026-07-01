from __future__ import annotations

from typing import Any


class InMemoryCollection:
    def __init__(self) -> None:
        self.docs: list[dict[str, Any]] = []

    def insert_one(self, doc: dict[str, Any]) -> None:
        self.docs.append(doc)

    def update_one(self, filt: dict[str, Any], update: dict[str, Any], upsert: bool = False) -> None:
        matched = [d for d in self.docs if all(d.get(k) == v for k, v in filt.items())]
        if matched:
            matched[0].update(update.get("$set", {}))
        elif upsert:
            self.docs.append({**filt, **update.get("$set", {})})

    def find_one(self, filt: dict[str, Any]) -> dict[str, Any] | None:
        for d in self.docs:
            if all(d.get(k) == v for k, v in filt.items()):
                return d
        return None

    def find(self, filt: dict[str, Any]) -> list[dict[str, Any]]:
        out = []
        for d in self.docs:
            if self._matches(d, filt):
                out.append(d)
        return out

    @staticmethod
    def _matches(doc: dict[str, Any], filt: dict[str, Any]) -> bool:
        for key, expected in filt.items():
            if key == "$or":
                if not any(InMemoryCollection._matches(doc, clause) for clause in expected):
                    return False
                continue
            if isinstance(expected, dict) and "$in" in expected:
                if doc.get(key) not in expected["$in"]:
                    return False
                continue
            if doc.get(key) != expected:
                return False
        return True

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "packages" / "project-core" / "src"))
sys.path.insert(0, str(ROOT / "packages" / "project-test" / "src"))

os.environ.setdefault("ALLOW_LLM_STUB", "1")
os.environ.setdefault("ALLOW_DEV_AUTH", "1")


@pytest.fixture
def fake_redis(monkeypatch):
    store: dict[str, str] = {}

    class _FakeRedis:
        def get(self, key):
            return store.get(key)

        def setex(self, key, _ttl, value):
            store[key] = value

        def delete(self, key):
            store.pop(key, None)

        def exists(self, key):
            return 1 if key in store else 0

        def expire(self, key, _ttl):
            return True

    monkeypatch.setattr("project_core.infra.stm.redis_store.redis.from_url", lambda *_a, **_k: _FakeRedis())
    return store

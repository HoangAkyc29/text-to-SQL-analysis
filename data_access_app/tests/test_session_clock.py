"""Session clock unit tests (no live SQL)."""
from __future__ import annotations

from datetime import date, datetime

from app.db import session_clock as clock
from app.db.cutoff import rolling_cutoff


def test_session_now_uses_pinned_as_of(monkeypatch):
    monkeypatch.setattr(clock, "_as_of", datetime(2026, 5, 18, 9, 30, 0))
    monkeypatch.setattr(clock, "_source", "transhdr")
    monkeypatch.setattr(clock, "_bootstrapped", True)
    assert clock.session_now() == datetime(2026, 5, 18, 9, 30, 0)
    assert rolling_cutoff() == date(2026, 4, 1)


def test_bootstrap_idempotent(monkeypatch):
    calls = {"n": 0}

    def fake_refresh():
        calls["n"] += 1
        monkeypatch.setattr(clock, "_as_of", datetime(2026, 3, 1))
        monkeypatch.setattr(clock, "_source", "transhdr")
        monkeypatch.setattr(clock, "_bootstrapped", True)
        monkeypatch.setattr(clock, "_detail", "ok")
        return clock.status()

    monkeypatch.setattr(clock, "refresh_from_transhdr", fake_refresh)
    monkeypatch.setattr(clock, "_bootstrapped", False)
    clock.bootstrap_session_clock()
    clock.bootstrap_session_clock()
    assert calls["n"] == 1
    clock.bootstrap_session_clock(force=True)
    assert calls["n"] == 2

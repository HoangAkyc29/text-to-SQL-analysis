"""Single-instance lock tests (no GUI MessageBox)."""
from __future__ import annotations

import pytest

from app import single_instance as si


def test_try_acquire_and_second_fails(monkeypatch, tmp_path):
    monkeypatch.setattr(si, "_MUTEX_NAME", "Local\\DataAccessApp_TestMutex_Unit2")
    monkeypatch.setattr(si, "_LOCK_PATH", tmp_path / "test.lock")

    first = si.try_acquire()
    assert first is not None
    second = si.try_acquire()
    assert second is None
    first.release()

    third = si.try_acquire()
    assert third is not None
    third.release()


def test_port_busy_exits(monkeypatch):
    monkeypatch.setenv("DATA_ACCESS_ALLOW_MULTI", "")
    monkeypatch.setattr(si, "port_is_listening", lambda port, host="127.0.0.1": True)
    monkeypatch.setattr(si, "show_already_running_modal", lambda **kwargs: None)
    with pytest.raises(SystemExit) as ei:
        si.acquire_or_exit(port=59999)
    assert ei.value.code == 0


def test_allow_multi_skips(monkeypatch):
    monkeypatch.setenv("DATA_ACCESS_ALLOW_MULTI", "1")
    si.acquire_or_exit(port=1)

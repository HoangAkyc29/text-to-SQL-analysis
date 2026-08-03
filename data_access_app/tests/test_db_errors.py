"""Unit tests for DB error classification (no live ODBC)."""
from __future__ import annotations

import pytest

from app.db.errors import (
    DbError,
    classify_db_failure,
    is_missing_object_error,
    user_facing_error,
    wrap_db_exception,
)
from app.ui.jobs import JobRunner, JobState


def test_classify_restore():
    msg = classify_db_failure(Exception("Database 'RESTORED_DB2' is being restored"))
    assert "restore" in msg.lower() or "recovery" in msg.lower()


def test_classify_disconnect():
    msg = classify_db_failure(Exception("TCP Provider: Communication link failure"), target="db2")
    assert "db2" in msg
    assert "Mất kết nối" in msg or "kết nối" in msg.lower()


def test_classify_timeout():
    msg = classify_db_failure(Exception("HYT00 Query timeout expired"))
    assert "Hết thời gian" in msg or "timeout" in msg.lower()


def test_wrap_preserves_dberror():
    e = DbError("đã thân thiện")
    assert wrap_db_exception(e) is e


def test_missing_object():
    assert is_missing_object_error(Exception("Invalid object name 'STRANS_202301'"))
    assert not is_missing_object_error(Exception("Communication link failure"))


def test_user_facing_strips_traceback():
    assert user_facing_error("Mất kết nối\nTraceback...") == "Mất kết nối"
    assert "Mất kết nối" in user_facing_error(DbError("Mất kết nối SQL Server (db1). x"))


def test_job_runner_sets_short_error_not_traceback():
    runner = JobRunner(page=None)

    def boom():
        raise ConnectionError("Communication link failure")

    done_states: list[JobState] = []

    def on_done(st: JobState):
        done_states.append(st)

    assert runner.run(boom, on_done=on_done) is True
    # Thread may still be running — wait briefly
    import time

    for _ in range(50):
        if done_states:
            break
        time.sleep(0.05)
    assert done_states
    st = done_states[0]
    assert st.error
    assert "Traceback" not in st.error
    assert "Mất kết nối" in st.error or "kết nối" in st.error.lower()
    assert "Traceback" in st.error_detail

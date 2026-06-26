"""Smoke tests for project-core scaffold."""

from project_core.runtime.scheduler import parse_duration_seconds


def test_parse_duration_60s():
    assert parse_duration_seconds("60s") == 60.0


def test_parse_duration_5m():
    assert parse_duration_seconds("5m") == 300.0


def test_paths_module_importable():
    from project_core import paths  # noqa: F401

    assert paths.DATA_DIR.name == "data"

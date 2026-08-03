"""Export path helpers — Windows backslashes must not break .env rewrite."""
from __future__ import annotations

from pathlib import Path

from app.ui.output_path import remember_output_dir


def test_remember_output_dir_windows_path_no_re_escape(tmp_path, monkeypatch):
    app_root = tmp_path / "app"
    app_root.mkdir()
    env_path = app_root / ".env"
    env_path.write_text("DATA_ACCESS_OUTPUT_DIR=C:\\old\\out\nOTHER=1\n", encoding="utf-8")

    monkeypatch.setattr("app.ui.output_path.APP_ROOT", app_root)

    # Path that previously crashed re.sub: \C in \CODING
    chosen = tmp_path / "CODING STUFF" / "Data Extracting" / "test sample"
    chosen.mkdir(parents=True)

    out = remember_output_dir(chosen)
    assert out == chosen.resolve()
    text = env_path.read_text(encoding="utf-8")
    assert f"DATA_ACCESS_OUTPUT_DIR={chosen.resolve()}" in text
    assert "OTHER=1" in text
    assert text.count("DATA_ACCESS_OUTPUT_DIR=") == 1

"""python-sandbox MCP tools with real parquet files."""

from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_sandbox_load_dataset(sample_parquet):
    from python_sandbox.tools_impl import load_dataset

    result = load_dataset(str(sample_parquet))
    assert result["row_count"] == 2
    assert "month" in result["columns"]


def test_sandbox_preview_dataframe(sample_parquet):
    from python_sandbox.tools_impl import preview_dataframe

    result = preview_dataframe(str(sample_parquet), n=1)
    assert len(result["preview"]) == 1


def test_sandbox_export_excel(sample_parquet, tmp_path):
    from python_sandbox.tools_impl import export_excel

    out = tmp_path / "out.xlsx"
    result = export_excel(str(sample_parquet), str(out))
    assert result["status"] == "ok"
    assert out.exists()


def test_sandbox_plot_chart(sample_parquet, tmp_path):
    from python_sandbox.tools_impl import plot_chart

    out = tmp_path / "chart.png"
    result = plot_chart(str(sample_parquet), str(out), x="month", y="amount", title="t")
    assert result["status"] == "ok"
    assert out.exists()


def test_sandbox_run_analysis_script(sample_parquet, tmp_path):
    from python_sandbox.tools_impl import run_analysis_script

    out_dir = tmp_path / "out"
    script = "df=pd.read_parquet(path); (out / 'summary.txt').write_text(str(len(df)))"
    result = run_analysis_script(str(sample_parquet), script, str(out_dir))
    assert result["status"] == "ok"
    assert (out_dir / "summary.txt").exists()


def test_sandbox_missing_file_returns_error():
    from python_sandbox.tools_impl import load_dataset

    result = load_dataset("/nonexistent/path.parquet")
    assert result["error"] == "file_not_found"

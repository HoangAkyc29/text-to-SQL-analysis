from __future__ import annotations

from pathlib import Path

import pandas as pd

from project_core.domain.analysis.ops import DatasetWorkingSet, execute_op
from project_core.domain.analysis.ops.working_set import DatasetHandle
from project_core.ingest.attachments import ingest_file


def _ws(tmp_path: Path) -> tuple[DatasetWorkingSet, Path]:
    out = tmp_path / "out"
    out.mkdir()
    source = tmp_path / "q0.parquet"
    pd.DataFrame({"id": [1, 2], "value": [10.0, 20.0]}).to_parquet(source)
    ws = DatasetWorkingSet.from_manifest(
        {"queries": [{"path": str(source), "ref": "q0", "format": "parquet", "row_count": 2}]},
        [{"role": "main"}],
        work_dir=out / "_ws",
    )
    return ws, out


def test_csv_excel_reload_validate_compare_and_lineage(tmp_path):
    ws, out = _ws(tmp_path)
    csv_result = execute_op(
        ws, "export_csv", {"dataset": "q0", "filename": "data.csv"}, out_dir=out
    )
    assert csv_result.status == "ok"
    artifact_id = csv_result.result["artifact_id"]
    validation = execute_op(
        ws,
        "validate_export",
        {"artifact_id": artifact_id, "expected_dataset": "q0"},
        out_dir=out,
    )
    assert validation.status == "ok"
    reload_result = execute_op(
        ws,
        "reload_artifact",
        {"artifact_id": artifact_id, "save_as": "csv_copy"},
        out_dir=out,
    )
    assert reload_result.status == "ok"
    comparison = execute_op(
        ws,
        "compare_datasets",
        {"left": "q0", "right": "csv_copy", "keys": ["id"], "numeric_tolerance": 0.0},
        out_dir=out,
    )
    assert comparison.status == "ok"
    assert comparison.result["equal"] is True
    lineage = execute_op(ws, "get_lineage", {"ref": "csv_copy"}, out_dir=out)
    assert lineage.status == "ok"
    assert len(lineage.result["nodes"]) >= 2

    excel_result = execute_op(
        ws,
        "export_excel",
        {"filename": "book.xlsx", "sheets": {"source": "q0", "copy": "csv_copy"}},
        out_dir=out,
    )
    assert excel_result.status == "ok"
    inspection = execute_op(
        ws,
        "inspect_excel",
        {"artifact_id": excel_result.result["artifact_id"]},
        out_dir=out,
    )
    assert inspection.status == "ok"
    assert inspection.result["sheet_names"] == ["source", "copy"]


def test_load_allowlisted_xlsx_sheet(tmp_path):
    book = tmp_path / "input.xlsx"
    with pd.ExcelWriter(book, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="one", index=False)
        pd.DataFrame({"b": [2, 3]}).to_excel(writer, sheet_name="two", index=False)
    ws = DatasetWorkingSet(work_dir=tmp_path / "out" / "_ws")
    ws.register_allowed_source(
        "book",
        DatasetHandle(ref="book", path=str(book), format="xlsx", sheet_name="two"),
    )
    result = execute_op(
        ws,
        "load_tabular",
        {"source_ref": "book", "sheet_name": "two", "save_as": "loaded"},
        out_dir=tmp_path / "out",
    )
    assert result.status == "ok"
    assert result.result["row_count"] == 2


def test_attachment_ingest_preserves_all_xlsx_sheets_and_images(tmp_path):
    source = tmp_path / "source.xlsx"
    with pd.ExcelWriter(source, engine="openpyxl") as writer:
        pd.DataFrame({"a": [1]}).to_excel(writer, sheet_name="first", index=False)
        pd.DataFrame({"b": [2]}).to_excel(writer, sheet_name="second", index=False)
    uploaded = ingest_file(
        session_id="../../safe",
        file_name="../source.xlsx",
        content=source.read_bytes(),
        base_dir=tmp_path / "attachments",
    )
    assert len(uploaded.datasets) == 2
    assert {d.sheet_name for d in uploaded.datasets} == {"first", "second"}
    assert all(Path(d.path).exists() for d in uploaded.datasets)

    from PIL import Image

    image_path = tmp_path / "image.png"
    Image.new("RGB", (20, 20), "red").save(image_path)
    image = ingest_file(
        session_id="s1",
        file_name="image.png",
        content=image_path.read_bytes(),
        base_dir=tmp_path / "attachments",
    )
    assert image.mime == "image/png"
    assert image.schema_profile["width"] == 20


def test_export_rejects_traversal(tmp_path):
    ws, out = _ws(tmp_path)
    result = execute_op(
        ws,
        "export_csv",
        {"dataset": "q0", "filename": "../escape.csv"},
        out_dir=out,
    )
    assert result.status == "error"
    assert "unsafe_filename" in (result.error or "")


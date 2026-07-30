"""TCVN3 conversion tests — driven by tests/sample_tcvn3/sampletcvn3.txt."""

from __future__ import annotations

from pathlib import Path

import pytest

from project_core.text.tcvn3 import UNICODE_CHARS, TCVN3_CHARS, tcvn3_to_unicode

_REPO_ROOT = Path(__file__).resolve().parents[4]
_SAMPLE_FILE = _REPO_ROOT / "tests" / "sample_tcvn3" / "sampletcvn3.txt"


def _load_sample_pairs(path: Path) -> list[tuple[str, str, int]]:
    if not path.is_file():
        pytest.skip(f"sample file missing: {path}")
    pairs: list[tuple[str, str, int]] = []
    for lineno, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not line.strip():
            continue
        parts = line.split("\t")
        if len(parts) < 2:
            pytest.fail(f"{path}:{lineno}: expected tab-separated input\\texpected")
        pairs.append((parts[0], parts[-1], lineno))
    return pairs


_SAMPLE_PAIRS = _load_sample_pairs(_SAMPLE_FILE)


@pytest.mark.parametrize(
    ("raw", "expected", "lineno"),
    _SAMPLE_PAIRS,
    ids=[f"line{ln}" for _, _, ln in _SAMPLE_PAIRS],
)
def test_sample_file_pairs(raw: str, expected: str, lineno: int) -> None:
    got = tcvn3_to_unicode(raw)
    assert got == expected, (
        f"line {lineno} mismatch\n"
        f"  raw: {raw!r}\n"
        f"  exp: {expected!r}\n"
        f"  got: {got!r}"
    )


def test_map_lengths_match() -> None:
    assert len(UNICODE_CHARS) == len(TCVN3_CHARS) == 134


def test_multi_char_sequence() -> None:
    assert tcvn3_to_unicode("Aµ") == "À"


def test_single_char_d() -> None:
    assert tcvn3_to_unicode("§") == "Đ"


def test_remark_string_no_double_replace() -> None:
    """Regression: iterative str.replace re-mapped Unicode â via TCVN3 'â'→õ."""
    raw = "C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0"
    assert tcvn3_to_unicode(raw) == "Cân đối điều chỉnh quỹ thu ngân về 0"


def test_copyright_to_circumflex() -> None:
    assert tcvn3_to_unicode("©") == "â"
    assert tcvn3_to_unicode("ng©n") == "ngân"


def test_is_unicode_text_column() -> None:
    from project_core.text.tcvn3 import is_unicode_text_column

    assert is_unicode_text_column("CUST_NAME_U")
    assert is_unicode_text_column("FULL_NAME_U")
    assert is_unicode_text_column("full_name_u")
    assert not is_unicode_text_column("CUST_NAME")
    assert not is_unicode_text_column("FULL_NAME")


def test_maybe_decode_row_skips_u_suffix() -> None:
    from project_core.text.tcvn3 import maybe_decode_row

    unicode_name = "Nguyễn Văn Á"
    legacy = "NguyÔn V¨n A"  # typical TCVN3-ish; conversion need not be perfect here
    row = maybe_decode_row({"CUST_NAME": legacy, "CUST_NAME_U": unicode_name})
    assert row["CUST_NAME_U"] == unicode_name
    assert row["CUST_NAME"] != legacy or tcvn3_to_unicode(legacy) == legacy


def test_op_tcvn3_converter_skips_u_suffix(tmp_path) -> None:
    import pandas as pd
    from project_core.domain.analysis.ops.handlers import op_tcvn3_converter
    from project_core.domain.analysis.ops.working_set import DatasetWorkingSet

    ws = DatasetWorkingSet(work_dir=tmp_path / "ws")
    # lowercase á overlaps a TCVN3 codepoint; re-decode would remap it (á→ỏ).
    unicode_name = "Nguyễn Thị Lan á"
    assert tcvn3_to_unicode(unicode_name) != unicode_name
    ws.save_frame(
        "cust",
        pd.DataFrame(
            {
                "CUST_NAME": ["NguyÔn"],
                "CUST_NAME_U": [unicode_name],
                "FULL_NAME_U": [unicode_name],
            }
        ),
        role="dim",
        source="test",
    )
    out = op_tcvn3_converter(
        ws,
        {
            "dataset": "cust",
            "columns": ["CUST_NAME", "CUST_NAME_U", "FULL_NAME_U"],
            "save_as": "cust",
        },
        tmp_path / "out",
    )
    assert "CUST_NAME" in out["converted_columns"]
    assert out.get("skipped_unicode_columns") == ["CUST_NAME_U", "FULL_NAME_U"]
    got = ws.get("cust").frame()
    assert list(got["CUST_NAME_U"]) == [unicode_name]
    assert list(got["FULL_NAME_U"]) == [unicode_name]

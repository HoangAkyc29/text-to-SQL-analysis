"""IV analyzer impossible branch."""

from __future__ import annotations

import pandas as pd

from project_core.domain.analysis.iv_analyzer import _is_impossible_analysis
from project_core.domain.contracts.analysis_plan import ExecutionCoverage
from project_core.domain.contracts.brief import AnalysisBrief


def test_is_impossible_for_unmappable_metric(tmp_path):
    raw = tmp_path / "q.parquet"
    pd.DataFrame({"SKU_ID": [1], "AMOUNT": [100]}).to_parquet(raw, index=False)
    brief = AnalysisBrief(intent="custom", metrics=["nonexistent_metric_xyz"])
    assert _is_impossible_analysis(
        brief,
        ExecutionCoverage(diagnosis="none"),
        steps_run=0,
        main_rows=1,
        paths=[str(raw)],
    )

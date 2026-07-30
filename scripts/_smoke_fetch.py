from project_core.domain.data_fetch import flexible_builders as flex
from project_core.domain.data_fetch.toolkit import (
    _looks_like_dataset_ref,
    _resolved_sku_ids_from_ws,
)
from project_core.domain.analysis.ops.working_set import DatasetHandle, DatasetWorkingSet
import pandas as pd
from pathlib import Path

sql = flex.build_query_rows(
    table="CUSTOMER",
    filters=[{"column": "CARD_ID", "op": "in", "value": ["A1"]}],
    time_range={"start": "2026-07-01", "end": "2026-07-06"},
    require_time=False,
)
assert "TRAN_DATE" not in sql, sql
sql2 = flex.build_query_rows(
    table="STRANS",
    time_range={"start": "2026-07-01", "end": "2026-07-06"},
    require_time=True,
)
assert "TRAN_DATE" in sql2
ws = DatasetWorkingSet(work_dir=Path("/tmp/ws_smoke2"))
ws.put(
    DatasetHandle(
        ref="resolve_products",
        df=pd.DataFrame([{"SKU_ID": "290003050900"}]),
    )
)
assert _resolved_sku_ids_from_ws(ws) == ["290003050900"]
print("smoke_ok")

"""Replay toolkit fetch for session 00ce475f."""
from pathlib import Path

import httpx
from project_core.domain.analysis.ops import DatasetWorkingSet
from project_core.domain.contracts.sql_acl import SqlAclContext
from project_core.domain.data_fetch.toolkit import DataFetchToolkit
from project_core.domain.schema.catalog import SchemaCatalog
from project_core.domain.sql.policy_engine import PolicyEngine
from project_core.infra.auth_internal import internal_auth_headers
import pandas as pd


class _Gw:
    def execute_readonly(self, sql, acl, *, target_db="db2"):
        r = httpx.post(
            "http://sql-gateway:18101/tools/execute_readonly",
            json={"sql": sql, "target_db": target_db, **acl.to_gateway_args()},
            headers=internal_auth_headers(),
            timeout=120,
        )
        r.raise_for_status()
        return r.json()


catalog = SchemaCatalog.from_dictionary_dir()
acl = SqlAclContext(
    actor_id="33333333-3333-3333-3333-333333333333",
    allowed_tables=["STRANS", "TRANSHDR", "SKU_DEF", "CUSTOMER", "CSCARD"],
    tool_grants=["tool:*"],
    store_filter_required=True,
    store_ids=[10001, 10004],
)
policy = PolicyEngine(
    catalog,
    allowed_tables=acl.allowed_tables,
    store_ids=acl.store_ids,
    store_filter_required=acl.store_filter_required,
)
ws = DatasetWorkingSet(work_dir=Path("/tmp/replay_ws"))
ws.save_frame(
    "resolve_products",
    pd.DataFrame([{"SKU_ID": "290003050900", "SKU_CODE": "x", "FULL_NAME": "t"}]),
    role="fetch",
)
toolkit = DataFetchToolkit(sql_gateway=_Gw(), policy=policy, acl=acl, working_set=ws)
brief = {
    "time_range": {"start": "2026-07-22", "end": "2026-07-28", "grain": "day"},
    "filters": {"store_ids": ["10005"]},
}
result = toolkit.execute(
    "query_rows",
    {
        "table": "STRANS",
        "time_range": brief["time_range"],
        "sku_ids": "resolve_products",
        "limit": 5000,
    },
    save_as="sale_lines",
    brief=brief,
)
print(result)

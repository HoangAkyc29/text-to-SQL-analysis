import httpx
from project_core.infra.auth_internal import internal_auth_headers

def run(sql: str, **extra):
    payload = {
        "sql": sql,
        "target_db": "db2",
        "actor_id": "33333333-3333-3333-3333-333333333333",
        "allowed_tables": ["STRANS"],
        "tool_grants": ["tool:*"],
        "store_filter_required": False,
        **extra,
    }
    r = httpx.post(
        "http://sql-gateway:18101/tools/execute_readonly",
        json=payload,
        headers=internal_auth_headers(),
        timeout=60,
    )
    data = r.json()
    print("row_count", data.get("row_count"), "sql snippet", sql[:80])

base = (
    "SELECT TOP 5 TRANS_NUM, TRAN_DATE, STK_ID, SKU_ID FROM STRANS "
    "WHERE SKU_ID='290003050900' "
    "AND TRAN_DATE >= '2026-07-22' AND TRAN_DATE <= '2026-07-28'"
)
run(base)
run(base + " AND STK_ID IN ('10001','10004','10005')")
run(base + " AND RTRIM(STK_ID) IN ('10001','10004','10005')")


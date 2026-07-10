---
semantic_key: suspend__dtdisc_rate
title: Tỷ lệ / phần trăm (dtdisc rate) (SUSPEND)
display_names:
- DTDISC_RATE
kind: measure
tables:
- ref: db2:suspend
  column: DTDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệDTDISC_RATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ / phần trăm (dtdisc rate) (SUSPEND)

**Semantic key:** `suspend__dtdisc_rate` · **Cột vật lý:** `DTDISC_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ / phần trăm (dtdisc rate) — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DTDISC_RATE` | numeric | Tỷ lệDTDISC_RATE |

## Ghi chú thêm

- Tỷ lệDTDISC_RATE

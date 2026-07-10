---
semantic_key: suspend__dmdisc_rate
title: Tỷ lệ / phần trăm (dmdisc rate) (SUSPEND)
display_names:
- DMDISC_RATE
kind: measure
tables:
- ref: db2:suspend
  column: DMDISC_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệDMDISC_RATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tỷ lệ / phần trăm (dmdisc rate) (SUSPEND)

**Semantic key:** `suspend__dmdisc_rate` · **Cột vật lý:** `DMDISC_RATE`

## Ý nghĩa nghiệp vụ

Tỷ lệ / phần trăm (dmdisc rate) — bill đang treo / chưa hoàn tất.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:suspend` | `DMDISC_RATE` | numeric | Tỷ lệDMDISC_RATE |

## Ghi chú thêm

- Tỷ lệDMDISC_RATE

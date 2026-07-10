---
semantic_key: st_order__deliver_dt
title: Ngày deliver (ST_ORDER)
display_names:
- DELIVER_DT
kind: date
tables:
- ref: db2:st_order
  column: DELIVER_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày giao hàng
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày deliver (ST_ORDER)

**Semantic key:** `st_order__deliver_dt` · **Cột vật lý:** `DELIVER_DT`

## Ý nghĩa nghiệp vụ

Ngày giao hàng dự kiến / thực tế trên đơn ST_ORDER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `DELIVER_DT` | datetime | Ngày giao hàng |

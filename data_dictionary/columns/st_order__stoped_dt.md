---
semantic_key: st_order__stoped_dt
title: Ngày stoped (ST_ORDER)
display_names:
- STOPED_DT
kind: date
tables:
- ref: db2:st_order
  column: STOPED_DT
  type: datetime
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày stoped (ST_ORDER)

**Semantic key:** `st_order__stoped_dt` · **Cột vật lý:** `STOPED_DT`

## Ý nghĩa nghiệp vụ

Ngày dừng / hủy đơn ST_ORDER.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:st_order` | `STOPED_DT` | datetime | Ngày stoped trên đơn đặt hàng nội bộ |

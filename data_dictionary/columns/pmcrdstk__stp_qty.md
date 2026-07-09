---
semantic_key: pmcrdstk__stp_qty
title: pmcrdstk · stp qty
display_names:
- STP_QTY
kind: measure
tables:
- ref: db2:pmcrdstk
  column: STP_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL dừng/hủy
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STP_QTY
- 'db2:pmcrdstk.STP_QTY: top=0(1000)'
---

# pmcrdstk · stp qty

**Semantic key:** `pmcrdstk__stp_qty` · **Cột vật lý:** `STP_QTY`

## Ý nghĩa nghiệp vụ

Cột STP_QTY trên PMCRDSTK. db2:pmcrdstk: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdstk` | `STP_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdstk.STP_QTY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm

- SL dừng/hủy

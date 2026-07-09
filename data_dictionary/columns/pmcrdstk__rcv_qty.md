---
semantic_key: pmcrdstk__rcv_qty
title: pmcrdstk · rcv qty
display_names:
- RCV_QTY
kind: measure
tables:
- ref: db2:pmcrdstk
  column: RCV_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL nhận
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RCV_QTY
- 'db2:pmcrdstk.RCV_QTY: top=1(349), 2(145), 3(85), 0(77), 4(48)'
---

# pmcrdstk · rcv qty

**Semantic key:** `pmcrdstk__rcv_qty` · **Cột vật lý:** `RCV_QTY`

## Ý nghĩa nghiệp vụ

Cột RCV_QTY trên PMCRDSTK. db2:pmcrdstk: top 0, 2, 46.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdstk` | `RCV_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdstk.RCV_QTY`
- Null rate trong sample: 0%
- Distinct ≈8; top: `0`×13, `2`×1, `46`×1, `54`×1, `41`×1, `47`×1, `29`×1, `857`×1

## Ghi chú thêm

- SL nhận

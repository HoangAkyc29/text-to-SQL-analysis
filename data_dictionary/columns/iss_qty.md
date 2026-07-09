---
semantic_key: iss_qty
title: iss qty
display_names:
- ISS_QTY
kind: measure
tables:
- ref: db2:pmcrdiss
  column: ISS_QTY
  type: numeric
- ref: db2:pmcrdstk
  column: ISS_QTY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- SL xuất
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:pmcrdiss.ISS_QTY: top=1(395), 2(161), 3(88), 4(54), 6(44)'
- 'db2:pmcrdstk.ISS_QTY: top=1(377), 2(152), 3(86), 4(62), 5(38)'
---

# iss qty

**Semantic key:** `iss_qty` · **Cột vật lý:** `ISS_QTY`

## Ý nghĩa nghiệp vụ

Cột ISS_QTY trên PMCRDISS, PMCRDSTK. db2:pmcrdiss: top 3, 1, 2; db2:pmcrdstk: top 0, 50, 2.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdiss` | `ISS_QTY` | numeric | có dữ liệu |
| `db2:pmcrdstk` | `ISS_QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdiss.ISS_QTY`
- Null rate trong sample: 0%
- Distinct ≈9; top: `3`×4, `1`×4, `2`×4, `4`×2, `5`×2, `33`×1, `6`×1, `13`×1

### `db2:pmcrdstk.ISS_QTY`
- Null rate trong sample: 0%
- Distinct ≈4; top: `0`×13, `50`×5, `2`×1, `908`×1

## Ghi chú thêm

- SL xuất

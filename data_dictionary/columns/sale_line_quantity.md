---
semantic_key: sale_line_quantity
title: Số lượng bán trên dòng STRANS
display_names:
- QTY
kind: measure
tables:
- ref: db1:strans
  column: QTY
  type: numeric
- ref: db2:strans
  column: QTY
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Số lượng
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.QTY: top=1.000(444), 2.000(105), 3.000(45), 4.000(27), 0.000(26)'
- 'db2:strans.QTY: top=1.000(512), 2.000(100), 3.000(33), 5.000(17), 4.000(15)'
---

# Số lượng bán trên dòng STRANS

**Semantic key:** `sale_line_quantity` · **Cột vật lý:** `QTY`

## Ý nghĩa nghiệp vụ

QTY trên STRANS — số lượng bán. Gift line có thể QTY=1, AMOUNT=0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `QTY` | numeric | có dữ liệu |
| `db2:strans` | `QTY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.QTY`
- Null rate trong sample: 0%
- Distinct ≈8; top: `3.000`×7, `10.000`×5, `1.000`×3, `30.000`×1, `40.000`×1, `5.000`×1, `25.000`×1, `2.000`×1

### `db2:strans.QTY`
- Null rate trong sample: 0%
- Distinct ≈8; top: `2.000`×10, `5.000`×3, `3.000`×2, `1.000`×1, `7.000`×1, `10.000`×1, `12.000`×1, `6.000`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Số lượng

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
- column_semantic_registry
- business_prose
---

# Số lượng bán trên dòng STRANS

**Semantic key:** `sale_line_quantity` · **Cột vật lý:** `QTY`

## Ý nghĩa nghiệp vụ

Số lượng bán trên dòng STRANS. Dòng quà tặng có thể QTY=1, AMOUNT=0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `QTY` | numeric | Số lượng trên dòng bán hàng POS |
| `db2:strans` | `QTY` | numeric | Số lượng trên dòng bán hàng POS |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

---
semantic_key: loyalty_tx_amount
title: Doanh thu gốc gắn giao dịch tích điểm (CRDTRANS)
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: AMOUNT
  type: numeric
- ref: db2:crdtrans
  column: AMOUNT
  type: numeric
- ref: db2:crdtrans_tmp
  column: AMOUNT
  type: numeric
join_with:
- TRANS_NUM
- SKU_ID
related_semantic_keys: []
facts:
- Thành tiền / số tiền (ngữ cảnh theo bảng)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Doanh thu gốc gắn giao dịch tích điểm (CRDTRANS)

**Semantic key:** `loyalty_tx_amount` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Doanh thu gốc dùng tính điểm trên CRDTRANS (811) / CRDTRANS_ARC (812). Archive có thể âm khi đổi quà. Quy tắc tham khảo: ~50.000 VND / 1 điểm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:crdtrans` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| `db2:crdtrans_tmp` | `AMOUNT` | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)

---
semantic_key: loyalty_tx_operator_note
title: Ghi chú thủ công trên giao dịch thẻ (REMARK)
display_names:
- REMARK
kind: text
tables:
- ref: db1:crdtrans_arc
  column: REMARK
  type: nvarchar
- ref: db2:crdtrans
  column: REMARK
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Ghi chú nghiệp vụ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ghi chú thủ công trên giao dịch thẻ (REMARK)

**Semantic key:** `loyalty_tx_operator_note` · **Cột vật lý:** `REMARK`

## Ý nghĩa nghiệp vụ

Ghi chú do nhân viên nhập khi điều chỉnh thẻ — giải thích trừ/cộng điểm, đổi quà, sửa tích nhầm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |
| `db2:crdtrans` | `REMARK` | nvarchar | Ghi chú nghiệp vụ |

## Ghi chú thêm

- Ghi chú nghiệp vụ

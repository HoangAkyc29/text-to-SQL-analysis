---
semantic_key: loyalty_points_redeemed
title: Điểm bị trừ / đổi quà (CRDTRANS_ARC 812)
display_names:
- MARK
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Điểm bị trừ / đổi quà (CRDTRANS_ARC 812)

**Semantic key:** `loyalty_points_redeemed` · **Cột vật lý:** `MARK`

## Ý nghĩa nghiệp vụ

Điểm trừ trên CRDTRANS_ARC (TRANS_CODE=812) khi đổi quà hoặc điều chỉnh thủ công.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `MARK` | numeric | Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811 |

## Ghi chú thêm

- Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811

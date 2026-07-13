---
semantic_key: loyalty_points_earned
title: Điểm tích lũy phát sinh (CRDTRANS 811)
display_names:
- MARK
kind: measure
tables:
- ref: db2:crdtrans
  column: MARK
  type: numeric
- ref: db2:crdtrans_tmp
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

# Điểm tích lũy phát sinh (CRDTRANS 811)

**Semantic key:** `loyalty_points_earned` · **Cột vật lý:** `MARK`

## Ý nghĩa nghiệp vụ

Điểm cộng trên CRDTRANS (ví dụ `TRANS_CODE=811`) hoặc metric điểm liên quan thẻ. Công thức tính lại điểm theo kỳ (nếu khác cột `MARK`) lấy từ **case study retrieve**, không hardcode trong column dict.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crdtrans` | `MARK` | numeric | Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811 |
| `db2:crdtrans_tmp` | `MARK` | numeric | Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811 |

## Ghi chú thêm

- Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811

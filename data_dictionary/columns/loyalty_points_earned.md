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
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crdtrans.MARK: top=1(185), 2(181), 3(120), 4(107), 5(81)'
- 'db2:crdtrans_tmp.MARK: top=1(199), 2(167), 3(124), 4(96), 5(78)'
---

# Điểm tích lũy phát sinh (CRDTRANS 811)

**Semantic key:** `loyalty_points_earned` · **Cột vật lý:** `MARK`

## Ý nghĩa nghiệp vụ

Điểm cộng trên CRDTRANS (TRANS_CODE=811). Sample: 4–66 điểm; tỷ lệ ~AMOUNT/50000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crdtrans` | `MARK` | numeric | Điểm cộng — ~AMOUNT/50000 |
| `db2:crdtrans_tmp` | `MARK` | numeric | Điểm cộng — ~AMOUNT/50000 |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crdtrans.MARK`
- Null rate trong sample: 0%
- Distinct ≈17; top: `10`×2, `76`×2, `1`×2, `22`×1, `18`×1, `43`×1, `29`×1, `2`×1

### `db2:crdtrans_tmp.MARK`
- Null rate trong sample: 0%
- Distinct ≈10; top: `7`×4, `2`×3, `3`×3, `5`×3, `8`×2, `4`×1, `9`×1, `1`×1

## Ghi chú thêm

- Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811

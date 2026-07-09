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
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.MARK: top=1(152), 2(147), 4(111), 3(109), 5(99)'
---

# Điểm bị trừ / đổi quà (CRDTRANS_ARC 812)

**Semantic key:** `loyalty_points_redeemed` · **Cột vật lý:** `MARK`

## Ý nghĩa nghiệp vụ

Điểm trừ trên CRDTRANS_ARC (TRANS_CODE=812). Sample: -100, -500 điểm kèm AMOUNT âm (đổi thẻ quà 50k/100k). REMARK mô tả: 'tang 02 the 50k=100d', 'giam 100 diem…'.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `MARK` | numeric | Điểm trừ (âm) khi đổi quà |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.MARK`
- Null rate trong sample: 0%
- Distinct ≈13; top: `-100`×5, `-500`×3, `-200`×2, `-2`×1, `-4`×1, `-400`×1, `-300`×1, `-150`×1

## Ghi chú thêm

- Điểm tích lũy; ~AMOUNT/50000 trên CRDTRANS 811

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
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for AMOUNT
- 'db1:crdtrans_arc.AMOUNT: top=80000(3), 90000(3), 81000(2), 451992(2), 58000(2)'
- 'db2:crdtrans.AMOUNT: top=69000(4), 115000(4), 58000(3), 82000(3), 52500(2)'
- 'db2:crdtrans_tmp.AMOUNT: top=80000(3), 76000(3), 71500(3), 59000(3), 239400(3)'
---

# Doanh thu gốc gắn giao dịch tích điểm (CRDTRANS)

**Semantic key:** `loyalty_tx_amount` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Doanh thu gốc dùng tính điểm trên CRDTRANS (811 live) / CRDTRANS_ARC (812 archive). Sample live: 450k–10M dương. Sample archive: **âm** (-5M, -100k) khi đổi quà/trừ điểm. Quy tắc quan sát: AMOUNT/MARK ≈ 50,000 VND/điểm.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `AMOUNT` | numeric | có dữ liệu |
| `db2:crdtrans` | `AMOUNT` | numeric | có dữ liệu |
| `db2:crdtrans_tmp` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈13; top: `-5000000`×5, `-25000000`×3, `-10000000`×2, `-100000`×1, `-200000`×1, `-20000000`×1, `-15000000`×1, `-7500000`×1

### `db2:crdtrans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈17; top: `500000`×2, `3800000`×2, `50000`×2, `1100000`×1, `900000`×1, `2150000`×1, `1450000`×1, `100000`×1

### `db2:crdtrans_tmp.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `108840`×1, `224100`×1, `454624`×1, `59946`×1, `139000`×1, `394634`×1, `170000`×1, `1190600`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)

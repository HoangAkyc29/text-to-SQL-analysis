---
semantic_key: amount_line_item
title: Thành tiền / giá trị dòng hàng STRANS
display_names:
- AMOUNT
kind: measure
tables:
- ref: db1:strans
  column: AMOUNT
  type: numeric
- ref: db2:st_order
  column: AMOUNT
  type: decimal
- ref: db2:strans
  column: AMOUNT
  type: numeric
- ref: db2:strans_tmp
  column: AMOUNT
  type: numeric
- ref: db2:suspend
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
- 'db1:strans.AMOUNT: top=0.00(109), 15686.24(6), 0.08(5), 16187.46(4), 50000.00(4)'
- 'db2:st_order.AMOUNT: top=0.00(22), 87514.00(6), 193452.00(5), 390000.00(5), 26000.00(4)'
- 'db2:strans.AMOUNT: top=0.00(130), 876.91(20), 1391.67(17), 1200.00(15), 695.84(10)'
- 'db2:strans_tmp.AMOUNT: top=0.00(142), 14000.00(7), 38000.00(5), 6853.42(4), 22222.23(4)'
- 'db2:suspend.AMOUNT: top=28000.00(15), 15000.00(13), 25000.00(12), 10000.00(11),
  1.00(10)'
---

# Thành tiền / giá trị dòng hàng STRANS

**Semantic key:** `amount_line_item` · **Cột vật lý:** `AMOUNT`

## Ý nghĩa nghiệp vụ

Giá trị/thành tiền trên dòng STRANS. Sample có 0.00 (gift/khuyến mãi) và các mức 120k–725k. Không dùng thay TRANSHDR.AMOUNT khi lọc min bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `AMOUNT` | numeric | Line amount — có thể 0 (gift) |
| `db2:st_order` | `AMOUNT` | decimal | có dữ liệu |
| `db2:strans` | `AMOUNT` | numeric | Line amount — có thể 0 (gift) |
| `db2:strans_tmp` | `AMOUNT` | numeric | có dữ liệu |
| `db2:suspend` | `AMOUNT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈19; top: `356481.50`×2, `1348050.00`×1, `58500.00`×1, `792000.00`×1, `168750.00`×1, `613425.00`×1, `1000000.02`×1, `625000.02`×1

### `db2:st_order.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `460025.64`×1, `614354.64`×1, `614720.10`×1, `714561.30`×1, `458923.92`×1, `592447.80`×1, `715020.12`×1, `450828.32`×1

### `db2:strans.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `20000.00`×1, `117000.00`×1, `136500.00`×1, `204000.00`×1, `294444.00`×1, `712962.96`×1, `796296.30`×1, `497222.22`×1

### `db2:strans_tmp.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `13278652.74`×1, `3913459.50`×1, `8559176.92`×1, `2392380.96`×1, `829090.92`×1, `574074.10`×1, `300000.00`×1, `324935.40`×1

### `db2:suspend.AMOUNT`
- Null rate trong sample: 0%
- Distinct ≈20; top: `7700.00`×1, `34700.00`×1, `25415.00`×1, `13120.00`×1, `10000.00`×1, `8028.00`×1, `15200.00`×1, `16500.00`×1

## Join

Thường join: `TRANS_NUM`, `SKU_ID`

## Ghi chú thêm

- Thành tiền / số tiền (ngữ cảnh theo bảng)

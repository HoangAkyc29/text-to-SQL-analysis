---
semantic_key: pmtrans__roundiff
title: pmtrans · roundiff
display_names:
- ROUNDIFF
kind: measure
tables:
- ref: db1:pmtrans
  column: ROUNDIFF
  type: numeric
- ref: db2:pmtrans
  column: ROUNDIFF
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Chênh lệch làm tròn thanh toán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for ROUNDIFF
- 'db1:pmtrans.ROUNDIFF: top=0.00(728), 50.00(14), 90.00(14), 80.00(13), 16.00(11)'
- 'db2:pmtrans.ROUNDIFF: top=0.00(898), 20.00(6), 80.00(5), 12.00(4), 92.00(4)'
---

# pmtrans · roundiff

**Semantic key:** `pmtrans__roundiff` · **Cột vật lý:** `ROUNDIFF`

## Ý nghĩa nghiệp vụ

Cột ROUNDIFF trên PMTRANS. db1:pmtrans: top 0.00, 74.00, 18.00; db2:pmtrans: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:pmtrans` | `ROUNDIFF` | numeric | có dữ liệu |
| `db2:pmtrans` | `ROUNDIFF` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.ROUNDIFF`
- Null rate trong sample: 0%
- Distinct ≈4; top: `0.00`×15, `74.00`×2, `18.00`×2, `16.00`×1

### `db2:pmtrans.ROUNDIFF`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Chênh lệch làm tròn thanh toán

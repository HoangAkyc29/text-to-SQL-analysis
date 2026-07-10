---
semantic_key: pmtrans__roundiff
title: Roundiff (PMTRANS)
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
- column_semantic_registry
- business_prose
---

# Roundiff (PMTRANS)

**Semantic key:** `pmtrans__roundiff` · **Cột vật lý:** `ROUNDIFF`

## Ý nghĩa nghiệp vụ

Chỉ số đo lường (roundiff) — dòng thanh toán / quỹ bill.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `ROUNDIFF` | numeric | Chênh lệch làm tròn thanh toán |
| `db2:pmtrans` | `ROUNDIFF` | numeric | Chênh lệch làm tròn thanh toán |

## Ghi chú thêm

- Chênh lệch làm tròn thanh toán

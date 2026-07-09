---
semantic_key: ctrans__bill
title: ctrans · bill
display_names:
- BILL
kind: identifier
tables:
- ref: db2:ctrans
  column: BILL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Tham chiếu bill / chứng từ gốc
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for BILL
- 'db2:ctrans.BILL: top=True(1000)'
---

# ctrans · bill

**Semantic key:** `ctrans__bill` · **Cột vật lý:** `BILL`

## Ý nghĩa nghiệp vụ

Cột BILL trên CTRANS. db2:ctrans: top True.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `BILL` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.BILL`
- Null rate trong sample: 0%
- Distinct ≈1; top: `True`×20

## Ghi chú thêm

- Tham chiếu bill / chứng từ gốc

---
semantic_key: inv_vatamt
title: inv vatamt
display_names:
- INV_VATAMT
kind: measure
tables:
- ref: db1:strans
  column: INV_VATAMT
  type: numeric
- ref: db2:debt
  column: INV_VATAMT
  type: numeric
- ref: db2:strans
  column: INV_VATAMT
  type: numeric
- ref: db2:strans_tmp
  column: INV_VATAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- VAT trên hóa đơn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_VATAMT: top=0.00(1000)'
- 'db2:debt.INV_VATAMT: top=0.00(1000)'
- 'db2:strans.INV_VATAMT: top=0.00(1000)'
- 'db2:strans_tmp.INV_VATAMT: top=0.00(1000)'
---

# inv vatamt

**Semantic key:** `inv_vatamt` · **Cột vật lý:** `INV_VATAMT`

## Ý nghĩa nghiệp vụ

Cột INV_VATAMT trên DEBT, STRANS, STRANS_TMP. db1:strans: top 0.00; db2:debt: top 0.00; db2:strans: top 0.00; db2:strans_tmp: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_VATAMT` | numeric | có dữ liệu |
| `db2:debt` | `INV_VATAMT` | numeric | có dữ liệu |
| `db2:strans` | `INV_VATAMT` | numeric | có dữ liệu |
| `db2:strans_tmp` | `INV_VATAMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:strans.INV_VATAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:debt.INV_VATAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans.INV_VATAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

### `db2:strans_tmp.INV_VATAMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- VAT trên hóa đơn

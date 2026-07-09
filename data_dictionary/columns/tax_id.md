---
semantic_key: tax_id
title: tax id
display_names:
- TAX_ID
kind: identifier
tables:
- ref: db2:inv_iss
  column: TAX_ID
  type: varchar
- ref: db2:partner
  column: TAX_ID
  type: varchar
- ref: db2:supplier
  column: TAX_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã số thuế
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.TAX_ID: top=0401801656(20), 0400102091(13), 0400101972(12), 0400101394(10),
  0101243150(7)'
- 'db2:partner.TAX_ID: top=0101526991002(1), 0304192712(1), 0400388101(1), 1600583588(1),
  03011966090-1(1)'
- 'db2:supplier.TAX_ID: top=0400130099(1), 0302783332(1), 0304693571(1), 0101594448(1),
  0301441897(1)'
---

# tax id

**Semantic key:** `tax_id` · **Cột vật lý:** `TAX_ID`

## Ý nghĩa nghiệp vụ

Cột TAX_ID trên INV_ISS, PARTNER, SUPPLIER. db2:partner: top 0303256057, 3600536736, 0303898713; db2:supplier: top 0303256057, 3600536736, 0303898713.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `TAX_ID` | varchar | có dữ liệu |
| `db2:partner` | `TAX_ID` | varchar | có dữ liệu |
| `db2:supplier` | `TAX_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.TAX_ID`
- Null rate trong sample: 60%
- Distinct ≈8; top: `0303256057`×1, `3600536736`×1, `0303898713`×1, `0303124558`×1, `0400228337`×1, `0400393549`×1, `0400388131`×1, `03011966090-1`×1

### `db2:supplier.TAX_ID`
- Null rate trong sample: 60%
- Distinct ≈8; top: `0303256057`×1, `3600536736`×1, `0303898713`×1, `0303124558`×1, `0400228337`×1, `0400393549`×1, `0400388131`×1, `03011966090-1`×1

## Ghi chú thêm

- Mã số thuế

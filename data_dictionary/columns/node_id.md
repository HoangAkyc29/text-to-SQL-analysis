---
semantic_key: node_id
title: node id
display_names:
- NODE_ID
kind: identifier
tables:
- ref: db2:crd_info
  column: NODE_ID
  type: char
- ref: db2:customer
  column: NODE_ID
  type: char
- ref: db2:pmcrdstk
  column: NODE_ID
  type: char
- ref: db2:rdiscinf
  column: NODE_ID
  type: char
- ref: db2:supplier
  column: NODE_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã node / chi nhánh hệ thống
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:crd_info.NODE_ID: top=000(603), 901(266), 902(131)'
- 'db2:customer.NODE_ID: top=000(250), 901(205), 902(78)'
- 'db2:pmcrdstk.NODE_ID: top=000(1000)'
- 'db2:rdiscinf.NODE_ID: top=000(522), 902(11), 901(2)'
- 'db2:supplier.NODE_ID: top=000(348)'
---

# node id

**Semantic key:** `node_id` · **Cột vật lý:** `NODE_ID`

## Ý nghĩa nghiệp vụ

Cột NODE_ID trên CRD_INFO, CUSTOMER, PMCRDSTK. db2:crd_info: top 000; db2:pmcrdstk: top 000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:crd_info` | `NODE_ID` | char | có dữ liệu |
| `db2:customer` | `NODE_ID` | char | có dữ liệu |
| `db2:pmcrdstk` | `NODE_ID` | char | có dữ liệu |
| `db2:rdiscinf` | `NODE_ID` | char | có dữ liệu |
| `db2:supplier` | `NODE_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crd_info.NODE_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `000`×20

### `db2:pmcrdstk.NODE_ID`
- Null rate trong sample: 0%
- Distinct ≈1; top: `000`×20

## Ghi chú thêm

- Mã node / chi nhánh hệ thống

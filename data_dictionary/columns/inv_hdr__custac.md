---
semantic_key: inv_hdr__custac
title: inv hdr · custac
display_names:
- CUSTAC
kind: text
tables:
- ref: db2:inv_hdr
  column: CUSTAC
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột CUSTAC
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CUSTAC
- 'db2:inv_hdr.CUSTAC: top=C(984), D(16)'
---

# inv hdr · custac

**Semantic key:** `inv_hdr__custac` · **Cột vật lý:** `CUSTAC`

## Ý nghĩa nghiệp vụ

Cột CUSTAC trên INV_HDR. db2:inv_hdr: top C.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_hdr` | `CUSTAC` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_hdr.CUSTAC`
- Null rate trong sample: 0%
- Distinct ≈1; top: `C`×20

## Ghi chú thêm


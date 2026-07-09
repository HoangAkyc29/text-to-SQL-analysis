---
semantic_key: inv_hdr__einv
title: inv hdr · einv
display_names:
- EINV
kind: flag
tables:
- ref: db2:inv_hdr
  column: EINV
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Hóa đơn điện tử
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for EINV
- 'db2:inv_hdr.EINV: top=False(1000)'
---

# inv hdr · einv

**Semantic key:** `inv_hdr__einv` · **Cột vật lý:** `EINV`

## Ý nghĩa nghiệp vụ

Cột EINV trên INV_HDR. db2:inv_hdr: top False.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_hdr` | `EINV` | bit | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_hdr.EINV`
- Null rate trong sample: 0%
- Distinct ≈1; top: `False`×20

## Ghi chú thêm

- Hóa đơn điện tử

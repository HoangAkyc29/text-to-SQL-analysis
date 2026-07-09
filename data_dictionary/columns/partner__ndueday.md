---
semantic_key: partner__ndueday
title: partner · ndueday
display_names:
- NDUEDAY
kind: measure
tables:
- ref: db2:partner
  column: NDUEDAY
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Cột NDUEDAY
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for NDUEDAY
- 'db2:partner.NDUEDAY: top=0(1000)'
---

# partner · ndueday

**Semantic key:** `partner__ndueday` · **Cột vật lý:** `NDUEDAY`

## Ý nghĩa nghiệp vụ

Cột NDUEDAY trên PARTNER. db2:partner: top 0.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `NDUEDAY` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.NDUEDAY`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0`×20

## Ghi chú thêm


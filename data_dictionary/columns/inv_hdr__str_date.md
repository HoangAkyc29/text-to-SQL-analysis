---
semantic_key: inv_hdr__str_date
title: inv hdr · str date
display_names:
- STR_DATE
kind: date
tables:
- ref: db2:inv_hdr
  column: STR_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàySTR_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STR_DATE
- 'db2:inv_hdr.STR_DATE: top=2024-08-23 00:00:00(5), 2024-09-18 00:00:00(5), 2024-01-09
  00:00:00(4), 2025-11-28 00:00:00(4), 2023-10-10 00:00:00(4)'
---

# inv hdr · str date

**Semantic key:** `inv_hdr__str_date` · **Cột vật lý:** `STR_DATE`

## Ý nghĩa nghiệp vụ

Cột STR_DATE trên INV_HDR. db2:inv_hdr: top 2025-12-31T00:00:00, 2026-03-31T00:00:00, 2025-08-29T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_hdr` | `STR_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_hdr.STR_DATE`
- Null rate trong sample: 0%
- Distinct ≈17; top: `2025-12-31T00:00:00`×3, `2026-03-31T00:00:00`×2, `2025-08-29T00:00:00`×1, `2025-08-31T00:00:00`×1, `2025-12-26T00:00:00`×1, `2026-01-22T00:00:00`×1, `2026-01-31T00:00:00`×1, `2026-02-09T00:00:00`×1

## Ghi chú thêm

- NgàySTR_DATE

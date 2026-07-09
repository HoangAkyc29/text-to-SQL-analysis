---
semantic_key: partner__inter_rate
title: partner · inter rate
display_names:
- INTER_RATE
kind: measure
tables:
- ref: db2:partner
  column: INTER_RATE
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tỷ lệINTER_RATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for INTER_RATE
- 'db2:partner.INTER_RATE: top=0.00(1000)'
---

# partner · inter rate

**Semantic key:** `partner__inter_rate` · **Cột vật lý:** `INTER_RATE`

## Ý nghĩa nghiệp vụ

Cột INTER_RATE trên PARTNER. db2:partner: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `INTER_RATE` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.INTER_RATE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Tỷ lệINTER_RATE

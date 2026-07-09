---
semantic_key: cscard__fresh_date
title: cscard · fresh date
display_names:
- FRESH_DATE
kind: date
tables:
- ref: db2:cscard
  column: FRESH_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyFRESH_DATE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for FRESH_DATE
- 'db2:cscard.FRESH_DATE: top=2025-10-09 00:00:00(26), 2017-11-02 00:00:00(14), 2014-06-05
  00:00:00(8), 2013-10-14 00:00:00(6), 2013-10-09 00:00:00(6)'
---

# cscard · fresh date

**Semantic key:** `cscard__fresh_date` · **Cột vật lý:** `FRESH_DATE`

## Ý nghĩa nghiệp vụ

Cột FRESH_DATE trên CSCARD. db2:cscard: top 2006-10-17T00:00:00, 2006-10-23T00:00:00, 2006-10-21T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `FRESH_DATE` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.FRESH_DATE`
- Null rate trong sample: 10%
- Distinct ≈8; top: `2006-10-17T00:00:00`×3, `2006-10-23T00:00:00`×3, `2006-10-21T00:00:00`×3, `2006-10-22T00:00:00`×3, `2006-10-18T00:00:00`×2, `2006-10-20T00:00:00`×2, `2012-12-29T00:00:00`×1, `2006-10-19T00:00:00`×1

## Ghi chú thêm

- NgàyFRESH_DATE

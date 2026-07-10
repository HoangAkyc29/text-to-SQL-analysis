---
semantic_key: iss_date
title: iss date
display_names:
- ISS_DATE
kind: date
tables:
- ref: db2:assolst
  column: ISS_DATE
  type: datetime
- ref: db2:cscard
  column: ISS_DATE
  type: datetime
- ref: db2:pmcrdinf
  column: ISS_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyISS_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# iss date

**Semantic key:** `iss_date` · **Cột vật lý:** `ISS_DATE`

## Ý nghĩa nghiệp vụ

NgàyISS_DATE. Dùng trong Loyalty / thẻ (CSCARD).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:assolst` | `ISS_DATE` | datetime | NgàyISS_DATE |
| `db2:cscard` | `ISS_DATE` | datetime | Ngày phát hành thẻ |
| `db2:pmcrdinf` | `ISS_DATE` | datetime | NgàyISS_DATE |

---
semantic_key: partner__rep_person
title: partner · rep person
display_names:
- REP_PERSON
kind: text
tables:
- ref: db2:partner
  column: REP_PERSON
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột REP_PERSON
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for REP_PERSON
- 'db2:partner.REP_PERSON: top=Ly Ph­¬ng(1), ANH pHóC1(1), Nguyen Hung Duong(1), Xu©n
  Thñy(1), ChÞ M¬(1)'
---

# partner · rep person

**Semantic key:** `partner__rep_person` · **Cột vật lý:** `REP_PERSON`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `REP_PERSON` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột REP_PERSON

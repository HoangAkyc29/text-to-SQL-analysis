---
semantic_key: sex
title: sex
display_names:
- SEX
kind: text
tables:
- ref: db2:cscard
  column: SEX
  type: char
- ref: db2:customer
  column: SEX
  type: char
join_with: []
related_semantic_keys: []
facts:
- Giới tính
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.SEX: top=F(812), M(153), C(4)'
- 'db2:customer.SEX: top=F(757), M(153), C(7), U(1)'
---

# sex

**Semantic key:** `sex` · **Cột vật lý:** `SEX`

## Ý nghĩa nghiệp vụ

Cột SEX trên CSCARD, CUSTOMER. db2:cscard: top F, M; db2:customer: top M, F.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `SEX` | char | có dữ liệu |
| `db2:customer` | `SEX` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.SEX`
- Null rate trong sample: 10%
- Distinct ≈2; top: `F`×17, `M`×1

### `db2:customer.SEX`
- Null rate trong sample: 90%
- Distinct ≈2; top: `M`×1, `F`×1

## Ghi chú thêm

- Giới tính

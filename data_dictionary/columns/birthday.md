---
semantic_key: birthday
title: birthday
display_names:
- BIRTHDAY
kind: date
tables:
- ref: db2:cscard
  column: BIRTHDAY
  type: datetime
- ref: db2:customer
  column: BIRTHDAY
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- Ngày sinh
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.BIRTHDAY: top=1968-01-01 00:00:00(4), 1965-01-01 00:00:00(4), 1973-01-01
  00:00:00(3), 1990-01-01 00:00:00(3), 1999-01-01 00:00:00(3)'
- 'db2:customer.BIRTHDAY: top=1990-01-01 00:00:00(3), 1982-10-14 00:00:00(3), 1963-01-01
  00:00:00(3), 1984-06-22 00:00:00(2), 1960-01-01 00:00:00(2)'
---

# birthday

**Semantic key:** `birthday` · **Cột vật lý:** `BIRTHDAY`

## Ý nghĩa nghiệp vụ

Cột BIRTHDAY trên CSCARD, CUSTOMER. db2:cscard: top 1976-10-11T00:00:00, 1964-04-11T00:00:00, 1949-08-06T00:00:00; db2:customer: top 1981-11-10T00:00:00, 1971-08-08T00:00:00, 1957-01-11T00:00:00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `BIRTHDAY` | datetime | có dữ liệu |
| `db2:customer` | `BIRTHDAY` | datetime | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.BIRTHDAY`
- Null rate trong sample: 5%
- Distinct ≈19; top: `1976-10-11T00:00:00`×1, `1964-04-11T00:00:00`×1, `1949-08-06T00:00:00`×1, `1969-10-02T00:00:00`×1, `1961-02-21T00:00:00`×1, `1960-05-09T00:00:00`×1, `1976-11-05T00:00:00`×1, `1976-10-13T00:00:00`×1

### `db2:customer.BIRTHDAY`
- Null rate trong sample: 0%
- Distinct ≈20; top: `1981-11-10T00:00:00`×1, `1971-08-08T00:00:00`×1, `1957-01-11T00:00:00`×1, `1964-04-11T00:00:00`×1, `1972-12-22T00:00:00`×1, `1961-12-07T00:00:00`×1, `1980-08-30T00:00:00`×1, `1986-08-30T00:00:00`×1

## Ghi chú thêm

- Ngày sinh

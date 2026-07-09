---
semantic_key: phone
title: phone
display_names:
- Phone
- PHONE
kind: text
tables:
- ref: db2:cscard
  column: PHONE
  type: varchar
- ref: db2:customer
  column: PHONE
  type: varchar
- ref: db2:custsumm
  column: Phone
  type: char
- ref: db2:inv_iss
  column: PHONE
  type: varchar
- ref: db2:partner
  column: PHONE
  type: varchar
- ref: db2:supplier
  column: PHONE
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Điện thoại
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.PHONE: top=0935888999(2), 0915716102(2), 0915464577(2), 0905002225(2),
  0934806608(1)'
- 'db2:customer.PHONE: top=0905144833(2), 0905673133(2), 0908049402(1), 0898372162(1),
  0905548458(1)'
- 'db2:custsumm.Phone: top=0935345357(2), 0914352280(2), 0917981951(2), 0905933567(1),
  0934939619(1)'
- 'db2:inv_iss.PHONE: top=0905223866(20), 0702636406(6), 0913417452(5), 0905475747(4),
  0905298398(3)'
- 'db2:partner.PHONE: top=0511722310(2), 0836031681(1), 0779431852(1), 05113.739262-3739457(1),
  048571152-045375469(1)'
- 'db2:supplier.PHONE: top=08.38341208(1), 0935.058.936(1), 048571152-045375469(1),
  05113.739262-3739457(1), 0511722310(1)'
---

# phone

**Semantic key:** `phone` · **Cột vật lý:** `Phone`, `PHONE`

## Ý nghĩa nghiệp vụ

Cột PHONE trên CSCARD, CUSTOMER, CUSTSUMM. db2:cscard: top 0903203411, 0983004441, 0919503031; db2:customer: top 0914111553, 3519475, 0983723356; db2:custsumm: top 3834869, 0779420825, 0905873338; db2:partner: top 087551372-7551796, 891643, 0511722310; db2:supplier: top 087551372-7551796, 891643, 0511722310.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `PHONE` | varchar | có dữ liệu |
| `db2:customer` | `PHONE` | varchar | có dữ liệu |
| `db2:custsumm` | `Phone` | char | có dữ liệu |
| `db2:inv_iss` | `PHONE` | varchar | có dữ liệu |
| `db2:partner` | `PHONE` | varchar | có dữ liệu |
| `db2:supplier` | `PHONE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.PHONE`
- Null rate trong sample: 20%
- Distinct ≈16; top: `0903203411`×1, `0983004441`×1, `0919503031`×1, `0983887728`×1, `0905812671`×1, `0914040050`×1, `0989078976`×1, `750363`×1

### `db2:customer.PHONE`
- Null rate trong sample: 55%
- Distinct ≈9; top: `0914111553`×1, `3519475`×1, `0983723356`×1, `0983004441`×1, `NV siªu thÞ`×1, `0905348048`×1, `0983887728`×1, `0913415205`×1

### `db2:custsumm.Phone`
- Null rate trong sample: 0%
- Distinct ≈20; top: `3834869`×1, `0779420825`×1, `0905873338`×1, `0915535969`×1, `0931919090`×1, `0909250150`×1, `0905232710`×1, `0979460718`×1

### `db2:partner.PHONE`
- Null rate trong sample: 85%
- Distinct ≈3; top: `087551372-7551796`×1, `891643`×1, `0511722310`×1

### `db2:supplier.PHONE`
- Null rate trong sample: 85%
- Distinct ≈3; top: `087551372-7551796`×1, `891643`×1, `0511722310`×1

## Ghi chú thêm

- Điện thoại

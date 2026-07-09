---
semantic_key: email
title: email
display_names:
- EMAIL
kind: text
tables:
- ref: db2:cscard
  column: EMAIL
  type: varchar
- ref: db2:customer
  column: EMAIL
  type: varchar
- ref: db2:inv_iss
  column: EMAIL
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Email
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.EMAIL: top=mis@vnuk.edu.vn(2), tuantv19@yahoo.com(1), lanphuongnt@vinatexdn.com.vn(1),
  kimtuyenbve@gmail.com(1), drthanhnhan281@gmail.com(1)'
- 'db2:customer.EMAIL: top=dieuthaopt@gmail.com(2), hiendtt@nascoexpress.com(1), hoadonpccs3@gmail.com(1),
  quynhhuongmine914@gmail.com(1), phuonghtm1@danang.gov.vn(1)'
- 'db2:inv_iss.EMAIL: top=anh.duong@ahts.com.vn(12), tckt@danangport.com(10), n.khanhhuyen@danapha.com(6),
  lienevncpc@gmail.com(5), htto@dng.misa.com.vn(5)'
---

# email

**Semantic key:** `email` · **Cột vật lý:** `EMAIL`

## Ý nghĩa nghiệp vụ

Cột EMAIL trên CSCARD, CUSTOMER, INV_ISS. db2:customer: top tnc.danang@gmail.com, Lecamhoa-qnyahoo.com.vn.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `EMAIL` | varchar | có dữ liệu |
| `db2:customer` | `EMAIL` | varchar | có dữ liệu |
| `db2:inv_iss` | `EMAIL` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:customer.EMAIL`
- Null rate trong sample: 90%
- Distinct ≈2; top: `tnc.danang@gmail.com`×1, `Lecamhoa-qnyahoo.com.vn`×1

## Ghi chú thêm

- Email

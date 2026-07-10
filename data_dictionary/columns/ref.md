---
semantic_key: ref
title: ref
display_names:
- REF
kind: text
tables:
- ref: db1:crdtrans_arc
  column: REF
  type: char
- ref: db1:strans
  column: REF
  type: char
- ref: db2:crdtrans
  column: REF
  type: char
- ref: db2:crdtrans_tmp
  column: REF
  type: char
- ref: db2:st_order
  column: REF
  type: char
- ref: db2:strans_tmp
  column: REF
  type: char
- ref: db2:transhdr
  column: REF
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã/tham chiếu nội bộ
sources:
- table_md
- column_semantic_registry
- business_prose
---

# ref

**Semantic key:** `ref` · **Cột vật lý:** `REF`

## Ý nghĩa nghiệp vụ

Mã/tham chiếu nội bộ. Dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `REF` | char | Mã/tham chiếu nội bộ |
| `db1:strans` | `REF` | char | Mã/tham chiếu nội bộ |
| `db2:crdtrans` | `REF` | char | Mã/tham chiếu nội bộ |
| `db2:crdtrans_tmp` | `REF` | char | Mã/tham chiếu nội bộ |
| `db2:st_order` | `REF` | char | Mã/tham chiếu nội bộ |
| `db2:strans_tmp` | `REF` | char | Mã/tham chiếu nội bộ |
| `db2:transhdr` | `REF` | char | Mã/tham chiếu nội bộ |

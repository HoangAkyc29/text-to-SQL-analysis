---
semantic_key: updated
title: updated
display_names:
- UPDATED
kind: date
tables:
- ref: db1:pmtrans
  column: UPDATED
  type: bit
- ref: db1:strans
  column: UPDATED
  type: bit
- ref: db1:transhdr_arc
  column: UPDATED
  type: bit
- ref: db2:pmtrans
  column: UPDATED
  type: bit
- ref: db2:st_order
  column: UPDATED
  type: bit
- ref: db2:strans
  column: UPDATED
  type: bit
- ref: db2:strans_tmp
  column: UPDATED
  type: bit
- ref: db2:suspend
  column: UPDATED
  type: bit
- ref: db2:transhdr
  column: UPDATED
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Đã cập nhật (bit)
sources:
- table_md
- column_semantic_registry
- business_prose
---

# updated

**Semantic key:** `updated` · **Cột vật lý:** `UPDATED`

## Ý nghĩa nghiệp vụ

Đã cập nhật (bit). Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:pmtrans` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db1:strans` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db1:transhdr_arc` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:pmtrans` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:st_order` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:strans` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:strans_tmp` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:suspend` | `UPDATED` | bit | Đã cập nhật (bit) |
| `db2:transhdr` | `UPDATED` | bit | Đã cập nhật (bit) |

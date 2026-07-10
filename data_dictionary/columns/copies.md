---
semantic_key: copies
title: Số liên in / số bản sao chứng từ (COPIES)
display_names:
- COPIES
kind: measure
tables:
- ref: db1:strans
  column: COPIES
  type: numeric
- ref: db1:transhdr_arc
  column: COPIES
  type: numeric
- ref: db2:inv_iss
  column: COPIES
  type: numeric
- ref: db2:st_order
  column: COPIES
  type: numeric
- ref: db2:strans
  column: COPIES
  type: numeric
- ref: db2:strans_tmp
  column: COPIES
  type: numeric
- ref: db2:transhdr
  column: COPIES
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số liên in / số bản sao chứng từ (COPIES)

**Semantic key:** `copies` · **Cột vật lý:** `COPIES`

## Ý nghĩa nghiệp vụ

Số liên in / số bản sao chứng từ — dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Kho / mua hàng (INV_ISS, ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên dòng bán hàng POS |
| `db1:transhdr_arc` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên header bill đã archive |
| `db2:inv_iss` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên phiếu xuất kho |
| `db2:st_order` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên đơn đặt hàng nội bộ |
| `db2:strans` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên dòng bán hàng POS |
| `db2:strans_tmp` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên dòng bán tạm / suspend |
| `db2:transhdr` | `COPIES` | numeric | Số liên in / số bản sao chứng từ trên header bill bán lẻ |

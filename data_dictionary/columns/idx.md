---
semantic_key: idx
title: idx
display_names:
- IDX
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: IDX
  type: numeric
- ref: db1:pmtrans
  column: IDX
  type: int
- ref: db1:strans
  column: IDX
  type: numeric
- ref: db1:transhdr_arc
  column: IDX
  type: numeric
- ref: db2:asso_inf
  column: IDX
  type: numeric
- ref: db2:crd_info
  column: IDX
  type: numeric
- ref: db2:crdtrans
  column: IDX
  type: numeric
- ref: db2:crdtrans_tmp
  column: IDX
  type: numeric
- ref: db2:cscard
  column: IDX
  type: int
- ref: db2:ctrans
  column: IDX
  type: int
- ref: db2:pmtrans
  column: IDX
  type: int
- ref: db2:rdiscinf
  column: IDX
  type: int
- ref: db2:st_order
  column: IDX
  type: numeric
- ref: db2:strans
  column: IDX
  type: numeric
- ref: db2:strans_tmp
  column: IDX
  type: numeric
- ref: db2:suspend
  column: IDX
  type: numeric
- ref: db2:transhdr
  column: IDX
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- ID rule khuyến mãi
sources:
- table_md
- column_semantic_registry
- business_prose
---

# idx

**Semantic key:** `idx` · **Cột vật lý:** `IDX`

## Ý nghĩa nghiệp vụ

ID rule khuyến mãi. Dùng trong POS bán lẻ (PMTRANS, STRANS, …); Loyalty / thẻ (CRDTRANS, CRDTRANS_ARC, …); Kho / mua hàng (ST_ORDER).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db1:pmtrans` | `IDX` | int | Số thứ tự dòng trong chứng từ |
| `db1:strans` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db1:transhdr_arc` | `IDX` | numeric | Chỉ số dòng header (thường 0) |
| `db2:asso_inf` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:crd_info` | `IDX` | numeric | ID nội bộ bản ghi tích lũy |
| `db2:crdtrans` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:crdtrans_tmp` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:cscard` | `IDX` | int | ID nội bộ bản ghi thẻ |
| `db2:ctrans` | `IDX` | int | Số thứ tự dòng trong chứng từ |
| `db2:pmtrans` | `IDX` | int | Số thứ tự dòng trong chứng từ |
| `db2:rdiscinf` | `IDX` | int | ID rule khuyến mãi |
| `db2:st_order` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:strans` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:strans_tmp` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:suspend` | `IDX` | numeric | Số thứ tự dòng trong chứng từ |
| `db2:transhdr` | `IDX` | numeric | Chỉ số dòng header (thường 0) |

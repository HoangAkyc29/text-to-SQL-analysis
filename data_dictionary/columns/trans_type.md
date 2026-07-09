---
semantic_key: trans_type
title: trans type
display_names:
- TRANS_TYPE
kind: text
tables:
- ref: db1:crdtrans_arc
  column: TRANS_TYPE
  type: char
- ref: db2:crdtrans
  column: TRANS_TYPE
  type: char
- ref: db2:crdtrans_tmp
  column: TRANS_TYPE
  type: char
- ref: db2:ctrans
  column: TRANS_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Phân loại giao dịch thẻ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:ctrans.TRANS_TYPE: top=01(1000)'
---

# trans type

**Semantic key:** `trans_type` · **Cột vật lý:** `TRANS_TYPE`

## Ý nghĩa nghiệp vụ

Cột TRANS_TYPE trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db2:ctrans: top 01.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TRANS_TYPE` | char | Không có giá trị trong sample |
| `db2:crdtrans` | `TRANS_TYPE` | char | Không có giá trị trong sample |
| `db2:crdtrans_tmp` | `TRANS_TYPE` | char | Không có giá trị trong sample |
| `db2:ctrans` | `TRANS_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.TRANS_TYPE`
- Null rate trong sample: 0%
- Distinct ≈1; top: `01`×20

## Ghi chú thêm

- Phân loại giao dịch thẻ

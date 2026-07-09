---
semantic_key: supplier__pmt_seq
title: supplier · pmt seq
display_names:
- PMT_SEQ
kind: text
tables:
- ref: db2:supplier
  column: PMT_SEQ
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột PMT_SEQ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PMT_SEQ
- 'db2:supplier.PMT_SEQ: top=00000000000(471)'
---

# supplier · pmt seq

**Semantic key:** `supplier__pmt_seq` · **Cột vật lý:** `PMT_SEQ`

## Ý nghĩa nghiệp vụ

Cột PMT_SEQ trên SUPPLIER. db2:supplier: top 00000000000.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `PMT_SEQ` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.PMT_SEQ`
- Null rate trong sample: 85%
- Distinct ≈1; top: `00000000000`×3

## Ghi chú thêm


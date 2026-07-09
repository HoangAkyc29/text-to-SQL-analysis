---
semantic_key: custhist__surp_amt
title: custhist · surp amt
display_names:
- SURP_AMT
kind: measure
tables:
- ref: db2:custhist
  column: SURP_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnSURP_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SURP_AMT
- 'db2:custhist.SURP_AMT: top=0.00(886), 20000.00(3), 15000.00(3), 7800.00(2), 120000.00(2)'
---

# custhist · surp amt

**Semantic key:** `custhist__surp_amt` · **Cột vật lý:** `SURP_AMT`

## Ý nghĩa nghiệp vụ

Cột SURP_AMT trên CUSTHIST. db2:custhist: top 0.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:custhist` | `SURP_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:custhist.SURP_AMT`
- Null rate trong sample: 0%
- Distinct ≈1; top: `0.00`×20

## Ghi chú thêm

- Số tiềnSURP_AMT

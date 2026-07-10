---
semantic_key: crd_info__oth_amt
title: Số tiền / giá trị (CRD_INFO)
display_names:
- OTH_AMT
kind: measure
tables:
- ref: db2:crd_info
  column: OTH_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh khác: OTH_AMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Số tiền / giá trị (CRD_INFO)

**Semantic key:** `crd_info__oth_amt` · **Cột vật lý:** `OTH_AMT`

## Ý nghĩa nghiệp vụ

Doanh thu / giá trị phát sinh other (ngoài tích chuẩn) trong kỳ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `OTH_AMT` | numeric | Phát sinh khác: OTH_AMT |

## Ghi chú thêm

- Phát sinh khác: OTH_AMT

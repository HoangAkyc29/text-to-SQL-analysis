---
semantic_key: crd_info__beg_oamt
title: Beg Oamt (CRD_INFO)
display_names:
- BEG_OAMT
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_OAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_OAMT'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Beg Oamt (CRD_INFO)

**Semantic key:** `crd_info__beg_oamt` · **Cột vật lý:** `BEG_OAMT`

## Ý nghĩa nghiệp vụ

Doanh thu mua khác đầu kỳ (other amount) — ngoài bucket chính.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `BEG_OAMT` | numeric | Số dư đầu kỳ: BEG_OAMT |

## Ghi chú thêm

- Số dư đầu kỳ: BEG_OAMT

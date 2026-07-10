---
semantic_key: crd_info__beg_otrs
title: Beg Otrs (CRD_INFO)
display_names:
- BEG_OTRS
kind: measure
tables:
- ref: db2:crd_info
  column: BEG_OTRS
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Số dư đầu kỳ: BEG_OTRS'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Beg Otrs (CRD_INFO)

**Semantic key:** `crd_info__beg_otrs` · **Cột vật lý:** `BEG_OTRS`

## Ý nghĩa nghiệp vụ

Số giao dịch other đầu kỳ trên CRD_INFO.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `BEG_OTRS` | numeric | Số dư đầu kỳ: BEG_OTRS |

## Ghi chú thêm

- Số dư đầu kỳ: BEG_OTRS

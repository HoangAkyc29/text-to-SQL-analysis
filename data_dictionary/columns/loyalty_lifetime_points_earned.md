---
semantic_key: loyalty_lifetime_points_earned
title: Tổng điểm tích lifetime (CRD_INFO.BUY_MARK)
display_names:
- BUY_MARK
kind: measure
tables:
- ref: db2:crd_info
  column: BUY_MARK
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- 'Phát sinh mua/tích: BUY_MARK'
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tổng điểm tích lifetime (CRD_INFO.BUY_MARK)

**Semantic key:** `loyalty_lifetime_points_earned` · **Cột vật lý:** `BUY_MARK`

## Ý nghĩa nghiệp vụ

Tổng điểm đã tích lifetime (CRD_INFO.BUY_MARK).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:crd_info` | `BUY_MARK` | numeric | Phát sinh mua/tích: BUY_MARK |

## Ghi chú thêm

- Phát sinh mua/tích: BUY_MARK

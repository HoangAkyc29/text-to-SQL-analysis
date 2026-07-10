---
semantic_key: cscard__radius
title: Radius (CSCARD)
display_names:
- RADIUS
kind: measure
tables:
- ref: db2:cscard
  column: RADIUS
  type: int
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Radius (CSCARD)

**Semantic key:** `cscard__radius` · **Cột vật lý:** `RADIUS`

## Ý nghĩa nghiệp vụ

Bán kính / phạm vi cửa hàng áp dụng thẻ (geo radius).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:cscard` | `RADIUS` | int | Chỉ số đo lường (radius) trên master thẻ khách hàng thân thiết |

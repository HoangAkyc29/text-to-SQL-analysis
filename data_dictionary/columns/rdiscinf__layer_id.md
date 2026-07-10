---
semantic_key: rdiscinf__layer_id
title: Mã định danh (layer id) (RDISCINF)
display_names:
- LAYER_ID
kind: identifier
tables:
- ref: db2:rdiscinf
  column: LAYER_ID
  type: int
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (layer id) (RDISCINF)

**Semantic key:** `rdiscinf__layer_id` · **Cột vật lý:** `LAYER_ID`

## Ý nghĩa nghiệp vụ

Mức ưu tiên / lớp xếp chồng rule KM — rule priority khi nhiều KM cùng match.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `LAYER_ID` | int | Mã định danh (layer id) trên rule khuyến mãi / chiết khấu |

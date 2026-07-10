---
semantic_key: rdiscinf__disc_code
title: Mã phân loại disc (RDISCINF)
display_names:
- DISC_CODE
kind: code
tables:
- ref: db2:rdiscinf
  column: DISC_CODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã chiết khấu
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã phân loại disc (RDISCINF)

**Semantic key:** `rdiscinf__disc_code` · **Cột vật lý:** `DISC_CODE`

## Ý nghĩa nghiệp vụ

Mã chương trình chiết khấu / khuyến mãi — khóa tra rule trong RDISCINF.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `DISC_CODE` | char | Mã chiết khấu |

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã chiết khấu

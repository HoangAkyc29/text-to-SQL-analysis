---
semantic_key: ctrans__bill
title: Bill (CTRANS)
display_names:
- BILL
kind: identifier
tables:
- ref: db2:ctrans
  column: BILL
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Tham chiếu bill / chứng từ gốc
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Bill (CTRANS)

**Semantic key:** `ctrans__bill` · **Cột vật lý:** `BILL`

## Ý nghĩa nghiệp vụ

Cờ tham chiếu bill POS gốc — link CTRANS ↔ bán lẻ.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:ctrans` | `BILL` | bit | Tham chiếu bill / chứng từ gốc |

## Ghi chú thêm

- Tham chiếu bill / chứng từ gốc

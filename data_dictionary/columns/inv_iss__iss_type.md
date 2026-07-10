---
semantic_key: inv_iss__iss_type
title: Cờ thuộc tính (s type) (INV_ISS)
display_names:
- ISS_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: ISS_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cờ thuộc tính (s type) (INV_ISS)

**Semantic key:** `inv_iss__iss_type` · **Cột vật lý:** `ISS_TYPE`

## Ý nghĩa nghiệp vụ

Cờ thuộc tính (s type) — phiếu xuất kho.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_iss` | `ISS_TYPE` | char | Cờ thuộc tính (s type) trên phiếu xuất kho |

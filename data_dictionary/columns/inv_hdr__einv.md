---
semantic_key: inv_hdr__einv
title: Einv (INV_HDR)
display_names:
- EINV
kind: flag
tables:
- ref: db2:inv_hdr
  column: EINV
  type: bit
join_with: []
related_semantic_keys: []
facts:
- Hóa đơn điện tử
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Einv (INV_HDR)

**Semantic key:** `inv_hdr__einv` · **Cột vật lý:** `EINV`

## Ý nghĩa nghiệp vụ

Cờ hóa đơn điện tử (e-invoice) trên header nhập.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:inv_hdr` | `EINV` | bit | Hóa đơn điện tử |

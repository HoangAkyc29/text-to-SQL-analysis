---
semantic_key: sku
title: sku
display_names:
- SKU
kind: flag
tables:
- ref: db1:strans
  column: SKU
  type: bit
- ref: db2:assolst
  column: SKU
  type: bit
- ref: db2:sku_def
  column: SKU
  type: bit
- ref: db2:strans
  column: SKU
  type: bit
- ref: db2:strans_tmp
  column: SKU
  type: bit
- ref: db2:suspend
  column: SKU
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# sku

**Semantic key:** `sku` · **Cột vật lý:** `SKU`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (sku) — dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `SKU` | bit | Cờ / trạng thái (sku) trên dòng bán hàng POS |
| `db2:assolst` | `SKU` | bit | Cờ / trạng thái (sku) trên master combo / bundle |
| `db2:sku_def` | `SKU` | bit | Cờ / trạng thái (sku) trên master sản phẩm (SKU) |
| `db2:strans` | `SKU` | bit | Cờ / trạng thái (sku) trên dòng bán hàng POS |
| `db2:strans_tmp` | `SKU` | bit | Cờ / trạng thái (sku) trên dòng bán tạm / suspend |
| `db2:suspend` | `SKU` | bit | Cờ / trạng thái (sku) trên bill đang treo / chưa hoàn tất |

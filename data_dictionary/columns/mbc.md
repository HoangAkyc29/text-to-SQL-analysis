---
semantic_key: mbc
title: mbc
display_names:
- MBC
kind: flag
tables:
- ref: db1:strans
  column: MBC
  type: bit
- ref: db2:assolst
  column: MBC
  type: bit
- ref: db2:sku_def
  column: MBC
  type: bit
- ref: db2:strans
  column: MBC
  type: bit
- ref: db2:strans_tmp
  column: MBC
  type: bit
- ref: db2:suspend
  column: MBC
  type: bit
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# mbc

**Semantic key:** `mbc` · **Cột vật lý:** `MBC`

## Ý nghĩa nghiệp vụ

Cờ / trạng thái (mbc) — dùng trong POS bán lẻ (STRANS, STRANS_TMP, …); Master / danh mục (SKU_DEF).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:strans` | `MBC` | bit | Cờ / trạng thái (mbc) trên dòng bán hàng POS |
| `db2:assolst` | `MBC` | bit | Cờ / trạng thái (mbc) trên master combo / bundle |
| `db2:sku_def` | `MBC` | bit | Cờ / trạng thái (mbc) trên master sản phẩm (SKU) |
| `db2:strans` | `MBC` | bit | Cờ / trạng thái (mbc) trên dòng bán hàng POS |
| `db2:strans_tmp` | `MBC` | bit | Cờ / trạng thái (mbc) trên dòng bán tạm / suspend |
| `db2:suspend` | `MBC` | bit | Cờ / trạng thái (mbc) trên bill đang treo / chưa hoàn tất |

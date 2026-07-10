---
semantic_key: sku_id_ref
title: Mã sản phẩm nội bộ (join master SKU) (SKU_ID)
display_names:
- sku_id
- SKU_ID
kind: identifier
tables:
- ref: db2:asso_inf
  column: SKU_ID
  type: char
- ref: db2:custhist
  column: SKU_ID
  type: char
- ref: db2:hisrtpr
  column: SKU_ID
  type: char
- ref: db2:hissppr
  column: SKU_ID
  type: char
- ref: db2:plu
  column: SKU_ID
  type: char
- ref: db2:sku_activity
  column: sku_id
  type: varchar
- ref: db2:st_order
  column: SKU_ID
  type: char
- ref: db2:stk_dtl
  column: SKU_ID
  type: char
- ref: db2:strans_tmp
  column: SKU_ID
  type: char
- ref: db2:suspend
  column: SKU_ID
  type: char
- ref: db2:webrpt_inventory_daily
  column: sku_id
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã SKU
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã sản phẩm nội bộ (join master SKU) (SKU_ID)

**Semantic key:** `sku_id_ref` · **Cột vật lý:** `sku_id`, `SKU_ID`

## Ý nghĩa nghiệp vụ

Mã SKU trên báo cáo doanh số/tồn theo ngày — join SKU_DEF. (bảng WEBRPT_INVENTORY_DAILY).

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:asso_inf` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:custhist` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:hisrtpr` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:hissppr` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:plu` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:sku_activity` | `sku_id` | varchar | Mã SKU |
| `db2:st_order` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:stk_dtl` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:strans_tmp` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:suspend` | `SKU_ID` | char | Mã sản phẩm nội bộ |
| `db2:webrpt_inventory_daily` | `sku_id` | varchar | Mã SKU |

## Join

Thường join: `TRANS_NUM`

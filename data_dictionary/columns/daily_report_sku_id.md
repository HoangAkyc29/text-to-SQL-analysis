---
semantic_key: daily_report_sku_id
title: daily report sku id
display_names:
- sku_id
kind: identifier
tables:
- ref: db2:webrpt_sales_sku_daily
  column: sku_id
  type: varchar
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã SKU
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:webrpt_sales_sku_daily.sku_id: top=290312701100(3), 290310149700(3), 290310170400(3),
  290002621400(3), 290612667700(3)'
---

# daily report sku id

**Semantic key:** `daily_report_sku_id` · **Cột vật lý:** `sku_id`

## Ý nghĩa nghiệp vụ

Mã sản phẩm nội bộ — join STRANS ↔ SKU_DEF/BARCODE. db2:webrpt_sales_sku_daily: top 290000000300, 290000011100, 290000012300.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_sales_sku_daily` | `sku_id` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_sales_sku_daily.sku_id`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290000000300`×1, `290000011100`×1, `290000012300`×1, `290000012700`×1, `290000054800`×1, `290000059600`×1, `290000060800`×1, `290000061300`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã SKU

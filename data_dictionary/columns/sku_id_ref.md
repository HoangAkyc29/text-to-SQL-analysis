---
semantic_key: sku_id_ref
title: sku id ref
display_names:
- SKU_ID
- sku_id
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
- samples_top20
- column_semantic_registry
evidence:
- 'db2:asso_inf.SKU_ID: top=290300325000(6), 290300494000(5), 290300181900(5), 290001980800(5),
  290000561700(5)'
- 'db2:custhist.SKU_ID: top=290300559000(2), 290734170000(2), 291090550000(2), 290312790400(2),
  290200037500(2)'
- 'db2:hisrtpr.SKU_ID: top=290300505000(6), 290001856100(5), 290000118600(5), 290300611900(4),
  290001472300(4)'
- 'db2:hissppr.SKU_ID: top=290300483400(3), 290300471900(3), 290300324200(3), 290100022500(2),
  290300471700(2)'
- 'db2:plu.SKU_ID: top=290300049600(1), 290300225300(1), 290300650000(1), 290300084700(1),
  290002721100(1)'
- 'db2:sku_activity.sku_id: top=290600017500(2), 290002794100(2), 290100062800(2),
  290312798900(2), 290002089000(2)'
- 'db2:st_order.SKU_ID: top=290002979000(10), 290002978900(8), 290002978800(6), 290000864300(6),
  290002950000(6)'
- 'db2:stk_dtl.SKU_ID: top=290213113300(2), 290211984800(2), 290300147200(2), 290000174700(1),
  290300003200(1)'
- 'db2:strans_tmp.SKU_ID: top=290300472100(9), 290300471500(9), 290300471100(8), 290320061200(8),
  290310180900(7)'
- 'db2:suspend.SKU_ID: top=290310180900(8), 290300456300(7), 290001381800(7), 290600076400(6),
  290300472100(6)'
- 'db2:webrpt_inventory_daily.sku_id: top=290002844100(2), 290001969300(2), 290002357800(2),
  290001532400(2), 290312673600(2)'
---

# sku id ref

**Semantic key:** `sku_id_ref` · **Cột vật lý:** `SKU_ID`, `sku_id`

## Ý nghĩa nghiệp vụ

Mã sản phẩm nội bộ — join STRANS ↔ SKU_DEF/BARCODE. db2:asso_inf: top 290300227300, 290300229400, 290300054600; db2:custhist: top 290610000300, 290610000400, 290612576700; db2:hisrtpr: top 290300704400, 290300773900, 290200083200; db2:hissppr: top 290100190600, 290211846200, 290000011100; db2:plu: top 290300000400, 290300001200, 290300001400; db2:sku_activity: top 290000000100, 290000000300, 290000000700; db2:st_order: top 290310252200, 290310435700, 290311900200; db2:stk_dtl: top 290000000100, 290000000200, 290000000300; db2:strans_tmp: top 290312632800, 290300288100, 290000307500; db2:suspend: top 290311900200, 290310154300, 290300471800; db2:webrpt_inventory_daily: top 290000000100, 290000000200, 290000000400.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:asso_inf` | `SKU_ID` | char | có dữ liệu |
| `db2:custhist` | `SKU_ID` | char | có dữ liệu |
| `db2:hisrtpr` | `SKU_ID` | char | có dữ liệu |
| `db2:hissppr` | `SKU_ID` | char | có dữ liệu |
| `db2:plu` | `SKU_ID` | char | có dữ liệu |
| `db2:sku_activity` | `sku_id` | varchar | có dữ liệu |
| `db2:st_order` | `SKU_ID` | char | có dữ liệu |
| `db2:stk_dtl` | `SKU_ID` | char | có dữ liệu |
| `db2:strans_tmp` | `SKU_ID` | char | có dữ liệu |
| `db2:suspend` | `SKU_ID` | char | có dữ liệu |
| `db2:webrpt_inventory_daily` | `sku_id` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290300227300`×1, `290300229400`×1, `290300054600`×1, `290300155700`×1, `290612819300`×1, `290600218500`×1, `290600008400`×1, `290600012400`×1

### `db2:custhist.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈9; top: `290610000300`×5, `290610000400`×5, `290612576700`×3, `290612576600`×2, `290200291200`×1, `290200291900`×1, `290600088200`×1, `290600232400`×1

### `db2:hisrtpr.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈19; top: `290300704400`×2, `290300773900`×1, `290200083200`×1, `290210809100`×1, `290211343300`×1, `290200514200`×1, `290000000100`×1, `290000000200`×1

### `db2:hissppr.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈14; top: `290100190600`×2, `290211846200`×2, `290000011100`×2, `290000011200`×2, `290110785900`×2, `290000011300`×2, `290000011000`×1, `290512521600`×1

### `db2:plu.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290300000400`×1, `290300001200`×1, `290300001400`×1, `290300005000`×1, `290300005100`×1, `290300005400`×1, `290300006500`×1, `290300007800`×1

### `db2:sku_activity.sku_id`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290000000100`×1, `290000000300`×1, `290000000700`×1, `290000000900`×1, `290000009100`×1, `290000009300`×1, `290000009600`×1, `290000011100`×1

### `db2:st_order.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290310252200`×1, `290310435700`×1, `290311900200`×1, `290312426000`×1, `290310247800`×1, `290312616200`×1, `290312059100`×1, `290311444200`×1

### `db2:stk_dtl.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290000000100`×1, `290000000200`×1, `290000000300`×1, `290000000400`×1, `290000000500`×1, `290000000600`×1, `290000000700`×1, `290000000800`×1

### `db2:strans_tmp.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290312632800`×1, `290300288100`×1, `290000307500`×1, `290300497300`×1, `290001428900`×1, `290312626000`×1, `290001428800`×1, `290300598100`×1

### `db2:suspend.SKU_ID`
- Null rate trong sample: 0%
- Distinct ≈19; top: `290311900200`×2, `290310154300`×1, `290300471800`×1, `290300474600`×1, `290312580500`×1, `290300486000`×1, `290300471500`×1, `290300003400`×1

### `db2:webrpt_inventory_daily.sku_id`
- Null rate trong sample: 0%
- Distinct ≈20; top: `290000000100`×1, `290000000200`×1, `290000000400`×1, `290000000600`×1, `290000000700`×1, `290000000800`×1, `290000007300`×1, `290000007800`×1

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm

- Mã SKU

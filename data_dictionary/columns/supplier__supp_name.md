---
semantic_key: supplier__supp_name
title: supplier · supp name
display_names:
- SUPP_NAME
kind: text
tables:
- ref: db2:supplier
  column: SUPP_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên nhà cung cấp
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SUPP_NAME
- 'db2:supplier.SUPP_NAME: top=Cty TNHH Minh Quang(3), Cty TNHH Hoµng NhËt Ph­¬ng(2),
  Gia Dông HCM(2), C«ng Ty TNHH Lª ThÞ(2), CN Cty MinKai(1)'
---

# supplier · supp name

**Semantic key:** `supplier__supp_name` · **Cột vật lý:** `SUPP_NAME`

## Ý nghĩa nghiệp vụ

Cột SUPP_NAME trên SUPPLIER. db2:supplier: top C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t, C«ng ty TNHH An Ti, C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `SUPP_NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.SUPP_NAME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t`×1, `C«ng ty TNHH An Ti`×1, `C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc`×1, `C«ng ty TNHH n«ng l©m s¶n T©n Th¸i`×1, `C«ng ty TNHH Ch©u ¢u ViÖt Nam`×1, `C«ng ty d­îc §µ N½ng`×1, `C¬ së H­¬ng Nam`×1, `C«ng ty TNHH chÕ biÕn LTTP V¹n H­¬ng`×1

## Ghi chú thêm

- Tên nhà cung cấp

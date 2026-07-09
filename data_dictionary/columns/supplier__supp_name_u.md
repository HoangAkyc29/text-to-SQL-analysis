---
semantic_key: supplier__supp_name_u
title: supplier · supp name u
display_names:
- SUPP_NAME_U
kind: text
tables:
- ref: db2:supplier
  column: SUPP_NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột SUPP_NAME_U
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for SUPP_NAME_U
- 'db2:supplier.SUPP_NAME_U: top=Cty TNHH Minh Quang(3), Cty TNHH Hoàng Nhật Phương(2),
  Gia Dụng HCM(2), Công Ty TNHH Lê Thị(2), CN Cty MinKai(1)'
---

# supplier · supp name u

**Semantic key:** `supplier__supp_name_u` · **Cột vật lý:** `SUPP_NAME_U`

## Ý nghĩa nghiệp vụ

Cột SUPP_NAME_U trên SUPPLIER. db2:supplier: top Công ty TNHH TM-XNK Việt Thái Phát, Công ty TNHH An Ti, Công ty TNHH KD & CBTP Toàn Gia Hiệp Phước.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:supplier` | `SUPP_NAME_U` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:supplier.SUPP_NAME_U`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Công ty TNHH TM-XNK Việt Thái Phát`×1, `Công ty TNHH An Ti`×1, `Công ty TNHH KD & CBTP Toàn Gia Hiệp Phước`×1, `Công ty TNHH nông lâm sản Tân Thái`×1, `Công ty TNHH Châu Âu Việt Nam`×1, `Công ty dược Đà Nẵng`×1, `Cơ sở Hương Nam`×1, `Công ty TNHH chế biến LTTP Vạn Hương`×1

## Ghi chú thêm


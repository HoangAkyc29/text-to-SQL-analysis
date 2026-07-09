---
semantic_key: tax_name
title: tax name
display_names:
- TAX_NAME
kind: text
tables:
- ref: db2:inv_iss
  column: TAX_NAME
  type: nvarchar
- ref: db2:partner
  column: TAX_NAME
  type: nvarchar
- ref: db2:supplier
  column: TAX_NAME
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Tên đơn vị trên HĐ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.TAX_NAME: top=C«ng Ty Cæ PhÇn DÞch Vô Nhµ Ga Quèc TÕ §µ N½ng(14), C«ng
  Ty Cæ PhÇn C¶ng §µ N½ng(12), C«ng Ty Cæ PhÇn D­îc Danapha(8), Tæng C«ng Ty §iÖn
  Lùc MiÒn Trung(6), Ng©n Hµng Nhµ N­íc Chi Nh¸nh Khu Vùc 9(5)'
- 'db2:partner.TAX_NAME: top=NCC Anh §oµi(1), C«ng ty Cæ PhÇn C¶ng §µ N½ng(1), Cty
  TNHH Hieu Hang(1), C«ng ty TNHH MTV FDV(1), CT TNHH Hoµng TrÇn THT(1)'
- 'db2:supplier.TAX_NAME: top=CT TNHH Hoµng TrÇn THT(1), LA FRESH(1), C«ng ty CP ThÞnh
  Thiªn Kú(1)'
---

# tax name

**Semantic key:** `tax_name` · **Cột vật lý:** `TAX_NAME`

## Ý nghĩa nghiệp vụ

Tên đơn vị trên HĐ

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `TAX_NAME` | nvarchar | có dữ liệu |
| `db2:partner` | `TAX_NAME` | nvarchar | có dữ liệu |
| `db2:supplier` | `TAX_NAME` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm


---
semantic_key: tax_addr
title: tax addr
display_names:
- TAX_ADDR
kind: text
tables:
- ref: db2:inv_iss
  column: TAX_ADDR
  type: nvarchar
- ref: db2:partner
  column: TAX_ADDR
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Địa chỉ trên HĐ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:inv_iss.TAX_ADDR: top=C¶ng Hµng Kh«ng Quèc TÕ §µ N½ng, Ph­êng Hßa ThuËn T©y,
  QuËn H¶i Ch©u, §µ N½ng(8), Sè 253, ®­êng Dòng SÜ Thanh Khª, ph­êng Thanh Khª, thµnh
  phè §µ N½ng(7), 26 B¹ch §»ng, Ph­êng H¶i Ch©u, Thµnh Phè §µ N½ng, ViÖt Nam(6), 26
  B¹ch §»ng, P. H¶i Ch©u, TP §µ N½ng, ViÖt Nam(5), 72A §iÖn Biªn Phñ, Ph­êng Thanh
  Khª, Thµnh Phè §µ N½ng, ViÖt Nam(4)'
- 'db2:partner.TAX_ADDR: top=26 B¹ch §»ng, Ph­êng H¶i Ch©u, Thµnh phè §µ n½ng(1),
  Dong Hoi - Quang Binh(1)'
---

# tax addr

**Semantic key:** `tax_addr` · **Cột vật lý:** `TAX_ADDR`

## Ý nghĩa nghiệp vụ

Địa chỉ trên HĐ

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `TAX_ADDR` | nvarchar | có dữ liệu |
| `db2:partner` | `TAX_ADDR` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm


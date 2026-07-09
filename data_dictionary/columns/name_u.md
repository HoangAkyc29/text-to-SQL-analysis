---
semantic_key: name_u
title: name u
display_names:
- NAME_U
kind: text
tables:
- ref: db2:cscard
  column: NAME_U
  type: nvarchar
- ref: db2:partner
  column: NAME_U
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Cột NAME_U
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.NAME_U: top=Huỳnh Thị Kim Loan(3), Phạm Thị Thu(2), Nguyễn Thị Trang(2),
  Trần Thị Diệu Hiền(2), Nguyễn Thị Thanh Châu(2)'
- 'db2:partner.NAME_U: top=Cty TNHH MTV Trịnh Hiền(2), Cty TNHH Hải Đảo Lý Sơn(2),
  Joly Mart(2), Bảo Hưng Fruits(2), Cty TNHH Thành Nhân(2)'
---

# name u

**Semantic key:** `name_u` · **Cột vật lý:** `NAME_U`

## Ý nghĩa nghiệp vụ

Cột NAME_U trên CSCARD, PARTNER. db2:cscard: top Nguyen Hong Sơn, nguyeen van a, Nguyễn Văn Đại F2; db2:partner: top Công ty TNHH TM-XNK Việt Thái Phát, Công ty TNHH An Ti, Công ty TNHH KD & CBTP Toàn Gia Hiệp Phước.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `NAME_U` | nvarchar | có dữ liệu |
| `db2:partner` | `NAME_U` | nvarchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:cscard.NAME_U`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Nguyen Hong Sơn`×1, `nguyeen van a`×1, `Nguyễn Văn Đại F2`×1, `Trần thị Lệ Phước E253`×1, `Nguyễn Thị Thanh Vân`×1, `Lê Thị Bích Xuân`×1, `Nguyễn Thị Mỹ Thanh`×1, `Trần t Thanh Tâm`×1

### `db2:partner.NAME_U`
- Null rate trong sample: 0%
- Distinct ≈20; top: `Công ty TNHH TM-XNK Việt Thái Phát`×1, `Công ty TNHH An Ti`×1, `Công ty TNHH KD & CBTP Toàn Gia Hiệp Phước`×1, `Công ty TNHH nông lâm sản Tân Thái`×1, `Công ty TNHH Châu Âu Việt Nam`×1, `Công ty dược Đà Nẵng`×1, `Cơ sở Hương Nam`×1, `Công ty TNHH chế biến LTTP Vạn Hương`×1

## Ghi chú thêm


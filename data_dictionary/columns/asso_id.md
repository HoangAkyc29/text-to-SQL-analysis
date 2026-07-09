---
semantic_key: asso_id
title: asso id
display_names:
- ASSO_ID
kind: identifier
tables:
- ref: db1:strans
  column: ASSO_ID
  type: char
- ref: db2:asso_inf
  column: ASSO_ID
  type: char
- ref: db2:assolst
  column: ASSO_ID
  type: char
- ref: db2:strans
  column: ASSO_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã combo/bundle
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.ASSO_ID: top=270000400356(1)'
- 'db2:asso_inf.ASSO_ID: top=270000403753(2), 270000402021(2), 270000400787(2), 270000405851(2),
  270000405347(2)'
- 'db2:assolst.ASSO_ID: top=270000403319(1), 270000406320(1), 270000401865(1), 270000401157(1),
  270000403658(1)'
- 'db2:strans.ASSO_ID: top=270000407086(1), 270000407223(1)'
---

# asso id

**Semantic key:** `asso_id` · **Cột vật lý:** `ASSO_ID`

## Ý nghĩa nghiệp vụ

Cột ASSO_ID trên ASSOLST, ASSO_INF, STRANS. db2:asso_inf: top 270000400007, 270000400008, 270000400009; db2:assolst: top 270000400007, 270000400008, 270000400009.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `ASSO_ID` | char | có dữ liệu |
| `db2:asso_inf` | `ASSO_ID` | char | có dữ liệu |
| `db2:assolst` | `ASSO_ID` | char | có dữ liệu |
| `db2:strans` | `ASSO_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:asso_inf.ASSO_ID`
- Null rate trong sample: 0%
- Distinct ≈10; top: `270000400007`×2, `270000400008`×2, `270000400009`×2, `270000400010`×2, `270000400011`×2, `270000400012`×2, `270000400013`×2, `270000400014`×2

### `db2:assolst.ASSO_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `270000400007`×1, `270000400008`×1, `270000400009`×1, `270000400010`×1, `270000400011`×1, `270000400012`×1, `270000400013`×1, `270000400014`×1

## Ghi chú thêm

- Mã combo/bundle

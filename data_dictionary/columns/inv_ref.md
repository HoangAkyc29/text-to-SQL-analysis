---
semantic_key: inv_ref
title: inv ref
display_names:
- INV_REF
kind: text
tables:
- ref: db1:strans
  column: INV_REF
  type: varchar
- ref: db2:inv_iss
  column: INV_REF
  type: varchar
- ref: db2:strans
  column: INV_REF
  type: varchar
- ref: db2:strans_tmp
  column: INV_REF
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Tham chiếu hóa đơn
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:strans.INV_REF: top=000002025042800038514(8), 000002025042200038402(6), 000002025042000038359(6),
  000002025041800038336(6), 000002025040400038046(6)'
- 'db2:inv_iss.INV_REF: top=000AV2212209000507(1), 000002022062200006133(1), 000002024030400030409(1),
  000002024121800035737(1), 000BR2212601001528(1)'
- 'db2:strans.INV_REF: top=000002026062700042491(137), 000002026062700042488(119),
  000002026062700042485(94), 000002026062700042492(51), 000002026062700042489(36)'
- 'db2:strans_tmp.INV_REF: top=000002024052200031667(8), 000002024052900031782(7),
  000002024052600031731(7), 000002024050400031380(6), 000002024051200031502(6)'
---

# inv ref

**Semantic key:** `inv_ref` · **Cột vật lý:** `INV_REF`

## Ý nghĩa nghiệp vụ

Cột INV_REF trên INV_ISS, STRANS, STRANS_TMP. db2:inv_iss: top 000002022061600000001, 000002022061600000002, 000002022061600000003.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:strans` | `INV_REF` | varchar | có dữ liệu |
| `db2:inv_iss` | `INV_REF` | varchar | có dữ liệu |
| `db2:strans` | `INV_REF` | varchar | có dữ liệu |
| `db2:strans_tmp` | `INV_REF` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_iss.INV_REF`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000002022061600000001`×1, `000002022061600000002`×1, `000002022061600000003`×1, `000002022061600000004`×1, `000002022061600000005`×1, `000002022061600000006`×1, `000002022061600000007`×1, `000002022061600000008`×1

## Ghi chú thêm

- Tham chiếu hóa đơn

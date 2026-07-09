---
semantic_key: account_id
title: account id
display_names:
- ACCOUNT_ID
kind: identifier
tables:
- ref: db2:account
  column: ACCOUNT_ID
  type: char
- ref: db2:ctrans
  column: ACCOUNT_ID
  type: char
- ref: db2:debt
  column: ACCOUNT_ID
  type: char
- ref: db2:supplier
  column: ACCOUNT_ID
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã tài khoản công nợ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:account.ACCOUNT_ID: top=60174(1), 00164(1), 50633(1), 51128(1), 51576(1)'
- 'db2:ctrans.ACCOUNT_ID: top=50971(62), 00062(46), 50617(45), 51508(36), 51451(34)'
- 'db2:debt.ACCOUNT_ID: top=00062(46), 50617(34), 50371(26), 50724(26), 50426(24)'
- 'db2:supplier.ACCOUNT_ID: top=50204(1), 50760(1), 00714(1), 60144(1), 50614(1)'
---

# account id

**Semantic key:** `account_id` · **Cột vật lý:** `ACCOUNT_ID`

## Ý nghĩa nghiệp vụ

Cột ACCOUNT_ID trên ACCOUNT, CTRANS, DEBT. db2:account: top 00004, 00006, 00010; db2:ctrans: top 50855, 51547, 51373; db2:debt: top 00097, 00469, 00043; db2:supplier: top 00004, 00006, 00010.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:account` | `ACCOUNT_ID` | char | có dữ liệu |
| `db2:ctrans` | `ACCOUNT_ID` | char | có dữ liệu |
| `db2:debt` | `ACCOUNT_ID` | char | có dữ liệu |
| `db2:supplier` | `ACCOUNT_ID` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:account.ACCOUNT_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

### `db2:ctrans.ACCOUNT_ID`
- Null rate trong sample: 0%
- Distinct ≈12; top: `50855`×6, `51547`×3, `51373`×2, `51067`×1, `50565`×1, `50672`×1, `51449`×1, `50426`×1

### `db2:debt.ACCOUNT_ID`
- Null rate trong sample: 0%
- Distinct ≈9; top: `00097`×5, `00469`×4, `00043`×3, `00310`×2, `00656`×2, `50193`×1, `00481`×1, `00248`×1

### `db2:supplier.ACCOUNT_ID`
- Null rate trong sample: 0%
- Distinct ≈20; top: `00004`×1, `00006`×1, `00010`×1, `00011`×1, `00016`×1, `00017`×1, `00023`×1, `00026`×1

## Ghi chú thêm

- Mã tài khoản công nợ

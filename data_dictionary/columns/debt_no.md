---
semantic_key: debt_no
title: debt no
display_names:
- DEBT_NO
kind: identifier
tables:
- ref: db2:ctrans
  column: DEBT_NO
  type: char
- ref: db2:debt
  column: DEBT_NO
  type: char
join_with: []
related_semantic_keys: []
facts:
- Số chứng từ công nợ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:ctrans.DEBT_NO: top=000002112606000024(1), 000001132606001277(1), 000001132606001960(1),
  000001132607000100(1), 000001132606001407(1)'
- 'db2:debt.DEBT_NO: top=000001132505000519(1), 000001132008000489(1), 000001131609001003(1),
  000001131310000098(1), 000001132602000200(1)'
---

# debt no

**Semantic key:** `debt_no` · **Cột vật lý:** `DEBT_NO`

## Ý nghĩa nghiệp vụ

Cột DEBT_NO trên CTRANS, DEBT. db2:ctrans: top 000001132606000001, 000001132606000002, 000001132606000003; db2:debt: top 000001131212000002, 000001131212000003, 000001131212000004.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `DEBT_NO` | char | có dữ liệu |
| `db2:debt` | `DEBT_NO` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.DEBT_NO`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000001132606000001`×1, `000001132606000002`×1, `000001132606000003`×1, `000001132606000004`×1, `000001132606000005`×1, `000001132606000010`×1, `000001132606000011`×1, `000001132606000012`×1

### `db2:debt.DEBT_NO`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000001131212000002`×1, `000001131212000003`×1, `000001131212000004`×1, `000001131212000005`×1, `000001131212000006`×1, `000001131212000007`×1, `000001131212000008`×1, `000001131212000009`×1

## Ghi chú thêm

- Số chứng từ công nợ

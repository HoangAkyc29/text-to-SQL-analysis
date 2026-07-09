---
semantic_key: ctrans__tax_amt
title: ctrans · tax amt
display_names:
- TAX_AMT
kind: measure
tables:
- ref: db2:ctrans
  column: TAX_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Số tiềnTAX_AMT
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for TAX_AMT
- 'db2:ctrans.TAX_AMT: top=0.00(383), 34400.00(4), 103200.00(3), 25600.00(3), 13104.00(3)'
---

# ctrans · tax amt

**Semantic key:** `ctrans__tax_amt` · **Cột vật lý:** `TAX_AMT`

## Ý nghĩa nghiệp vụ

Cột TAX_AMT trên CTRANS. db2:ctrans: top 0.00, 10192.00, 60155.52.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:ctrans` | `TAX_AMT` | numeric | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:ctrans.TAX_AMT`
- Null rate trong sample: 0%
- Distinct ≈13; top: `0.00`×7, `10192.00`×2, `60155.52`×1, `281999.99`×1, `364054.81`×1, `644000.00`×1, `42189.60`×1, `6864.00`×1

## Ghi chú thêm

- Số tiềnTAX_AMT

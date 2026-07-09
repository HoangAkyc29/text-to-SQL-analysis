---
semantic_key: partner__code
title: partner · code
display_names:
- CODE
kind: text
tables:
- ref: db2:partner
  column: CODE
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Cột CODE
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for CODE
- 'db2:partner.CODE: top=A.HIEU(1), DUCQUY(1), 51230(1), 51492(1), 51019(1)'
---

# partner · code

**Semantic key:** `partner__code` · **Cột vật lý:** `CODE`

## Ý nghĩa nghiệp vụ

Cột CODE trên PARTNER. db2:partner: top 00036.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:partner` | `CODE` | varchar | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:partner.CODE`
- Null rate trong sample: 95%
- Distinct ≈1; top: `00036`×1

## Ghi chú thêm


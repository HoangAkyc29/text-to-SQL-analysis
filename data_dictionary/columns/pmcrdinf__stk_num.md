---
semantic_key: pmcrdinf__stk_num
title: pmcrdinf · stk num
display_names:
- STK_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: STK_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột STK_NUM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STK_NUM
- 'db2:pmcrdinf.STK_NUM: top=000008211704000025(6), 000008211704000024(6), 000008211709000023(5),
  000008211511000020(5), 000008211611000021(4)'
---

# pmcrdinf · stk num

**Semantic key:** `pmcrdinf__stk_num` · **Cột vật lý:** `STK_NUM`

## Ý nghĩa nghiệp vụ

Cột STK_NUM trên PMCRDINF. db2:pmcrdinf: top 000008211212000026.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `STK_NUM` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:pmcrdinf.STK_NUM`
- Null rate trong sample: 0%
- Distinct ≈1; top: `000008211212000026`×20

## Ghi chú thêm


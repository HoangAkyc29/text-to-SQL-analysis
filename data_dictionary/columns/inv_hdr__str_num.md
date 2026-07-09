---
semantic_key: inv_hdr__str_num
title: inv hdr · str num
display_names:
- STR_NUM
kind: identifier
tables:
- ref: db2:inv_hdr
  column: STR_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột STR_NUM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for STR_NUM
- 'db2:inv_hdr.STR_NUM: top=000001132507001441(1), 000001132206000806(1), 000001132511001438(1),
  000001132508000828(1), 000001132305000099(1)'
---

# inv hdr · str num

**Semantic key:** `inv_hdr__str_num` · **Cột vật lý:** `STR_NUM`

## Ý nghĩa nghiệp vụ

Cột STR_NUM trên INV_HDR. db2:inv_hdr: top 000001132508002379, 000001132508002300, 000001132512001105.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_hdr` | `STR_NUM` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:inv_hdr.STR_NUM`
- Null rate trong sample: 0%
- Distinct ≈20; top: `000001132508002379`×1, `000001132508002300`×1, `000001132512001105`×1, `000001132512002285`×1, `000001132512002346`×1, `000001132601000871`×1, `000001132601002371`×1, `000001132602000092`×1

## Ghi chú thêm


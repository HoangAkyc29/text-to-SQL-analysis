---
semantic_key: inv_iss__pmt_type
title: inv iss · pmt type
display_names:
- PMT_TYPE
kind: text
tables:
- ref: db2:inv_iss
  column: PMT_TYPE
  type: char
join_with: []
related_semantic_keys: []
facts:
- Loại thanh toán
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for PMT_TYPE
- 'db2:inv_iss.PMT_TYPE: top=CK(235), TM(125)'
---

# inv iss · pmt type

**Semantic key:** `inv_iss__pmt_type` · **Cột vật lý:** `PMT_TYPE`

## Ý nghĩa nghiệp vụ

Loại thanh toán

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:inv_iss` | `PMT_TYPE` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm


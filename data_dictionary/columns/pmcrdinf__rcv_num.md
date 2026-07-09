---
semantic_key: pmcrdinf__rcv_num
title: pmcrdinf · rcv num
display_names:
- RCV_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: RCV_NUM
  type: char
join_with: []
related_semantic_keys: []
facts:
- Cột RCV_NUM
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for RCV_NUM
- 'db2:pmcrdinf.RCV_NUM: top=000BE2212204007760(2), 000P12212102000006(2), 901AY2212201004428(1),
  901AX2212312001757(1), 000AU2212112001948(1)'
---

# pmcrdinf · rcv num

**Semantic key:** `pmcrdinf__rcv_num` · **Cột vật lý:** `RCV_NUM`

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:pmcrdinf` | `RCV_NUM` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Ghi chú thêm

- Cột RCV_NUM

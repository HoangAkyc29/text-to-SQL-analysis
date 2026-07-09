---
semantic_key: barcode
title: barcode
display_names:
- BARCODE
kind: identifier
tables:
- ref: db2:cscard
  column: BARCODE
  type: char
- ref: db2:pmcrdinf
  column: BARCODE
  type: char
join_with:
- TRANS_NUM
related_semantic_keys: []
facts:
- Mã vạch
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db2:cscard.BARCODE: top=239010000672(1), 230000009176(1), 230000006719(1), 239010001754(1),
  230000009700(1)'
---

# barcode

**Semantic key:** `barcode` · **Cột vật lý:** `BARCODE`

## Ý nghĩa nghiệp vụ

Mã vạch

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:cscard` | `BARCODE` | char | có dữ liệu |
| `db2:pmcrdinf` | `BARCODE` | char | Không có giá trị trong sample |

## Quan sát từ sample (TOP 20 db2/db1)

_Chưa có sample trong `samples_top20.json` — cần chạy `explore_db_samples.py` hoặc khai phá DB._

## Join

Thường join: `TRANS_NUM`

## Ghi chú thêm


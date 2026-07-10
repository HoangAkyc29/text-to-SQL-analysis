---
semantic_key: pmcrdinf__rcv_date
title: Ngày rcv (PMCRDINF)
display_names:
- RCV_DATE
kind: date
tables:
- ref: db2:pmcrdinf
  column: RCV_DATE
  type: datetime
join_with: []
related_semantic_keys: []
facts:
- NgàyRCV_DATE
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Ngày rcv (PMCRDINF)

**Semantic key:** `pmcrdinf__rcv_date` · **Cột vật lý:** `RCV_DATE`

## Ý nghĩa nghiệp vụ

Ngày nhận / kích hoạt voucher PM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `RCV_DATE` | datetime | NgàyRCV_DATE |

## Ghi chú thêm

- NgàyRCV_DATE

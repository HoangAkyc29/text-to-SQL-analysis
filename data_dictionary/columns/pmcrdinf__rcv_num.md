---
semantic_key: pmcrdinf__rcv_num
title: Mã định danh (rcv num) (PMCRDINF)
display_names:
- RCV_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: RCV_NUM
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (rcv num) (PMCRDINF)

**Semantic key:** `pmcrdinf__rcv_num` · **Cột vật lý:** `RCV_NUM`

## Ý nghĩa nghiệp vụ

Số phiếu nhận / kích hoạt voucher PM.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `RCV_NUM` | char | Mã định danh (rcv num) trên master thẻ PM / voucher |

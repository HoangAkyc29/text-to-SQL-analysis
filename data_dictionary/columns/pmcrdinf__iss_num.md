---
semantic_key: pmcrdinf__iss_num
title: Mã định danh (iss num) (PMCRDINF)
display_names:
- ISS_NUM
kind: identifier
tables:
- ref: db2:pmcrdinf
  column: ISS_NUM
  type: char
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã định danh (iss num) (PMCRDINF)

**Semantic key:** `pmcrdinf__iss_num` · **Cột vật lý:** `ISS_NUM`

## Ý nghĩa nghiệp vụ

Số phiếu phát hành thẻ PM / voucher — trace lifecycle phát hành.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:pmcrdinf` | `ISS_NUM` | char | Mã định danh (iss num) trên master thẻ PM / voucher |

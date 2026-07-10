---
semantic_key: rdiscinf__cntsumamt
title: Cntsumamt (RDISCINF)
display_names:
- CNTSUMAMT
kind: measure
tables:
- ref: db2:rdiscinf
  column: CNTSUMAMT
  type: numeric
join_with: []
related_semantic_keys: []
facts: []
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Cntsumamt (RDISCINF)

**Semantic key:** `rdiscinf__cntsumamt` · **Cột vật lý:** `CNTSUMAMT`

## Ý nghĩa nghiệp vụ

Tổng tiền KM đã cộng dồn (counter) — theo dõi ngân sách rule.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db2:rdiscinf` | `CNTSUMAMT` | numeric | Chỉ số đo lường (cntsumamt) trên rule khuyến mãi / chiết khấu |

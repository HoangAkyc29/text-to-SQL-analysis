---
semantic_key: webrpt_rfm_snapshot__monetary
title: webrpt rfm snapshot · monetary
display_names:
- monetary
kind: measure
tables:
- ref: db2:webrpt_rfm_snapshot
  column: monetary
  type: decimal
join_with: []
related_semantic_keys: []
facts:
- Tổng chi tiêu
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- role-specific semantic key for monetary
- 'db2:webrpt_rfm_snapshot.monetary: top=139400.00(2), 542300.00(2), 134000.00(2),
  776000.00(2), 861100.00(2)'
---

# webrpt rfm snapshot · monetary

**Semantic key:** `webrpt_rfm_snapshot__monetary` · **Cột vật lý:** `monetary`

## Ý nghĩa nghiệp vụ

Cột MONETARY trên WEBRPT_RFM_SNAPSHOT. db2:webrpt_rfm_snapshot: top 63812.00, 486000.00, 216680.00.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db2:webrpt_rfm_snapshot` | `monetary` | decimal | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:webrpt_rfm_snapshot.monetary`
- Null rate trong sample: 0%
- Distinct ≈20; top: `63812.00`×1, `486000.00`×1, `216680.00`×1, `78200.00`×1, `351900.00`×1, `472200.00`×1, `1819400.00`×1, `1325600.00`×1

## Ghi chú thêm

- Tổng chi tiêu

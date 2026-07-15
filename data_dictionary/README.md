# Data dictionary — agent schema reference

Tài liệu schema cho SQL planner (Agent II) và risk reviewer (Agent III). Nguồn: JSON export + `docs/DB_EXPLORATION_REPORT.md` + mẫu exploration.

## Hai database (peer, không primary/secondary)

| DB | SQL | Vai trò |
|----|-----|---------|
| **db1** | `RESTORED_DB` | **Lịch sử** — giao dịch archive trước ngưỡng rolling |
| **db2** | `RESTORED_DB2` | **Live** — danh mục, chứng từ gần đây, staging, báo cáo |

### Ngưỡng thời gian (rolling cutoff)

Tính theo **ngày chạy query**:

- `cutoff` = **ngày 1 của tháng trước** (so với hôm nay).
- `archive_newest_ym` = **tháng trước cutoff** — hậu tố shard db1 mới nhất (expand runtime trong `shard_resolver`, không freeze trong YAML).
- Ví dụ hôm nay **15/07/2026** → `cutoff = 2026-06-01`, `archive_newest_ym = 202605`.

| DB | Phạm vi giao dịch | Tên bảng fact |
|----|-------------------|---------------|
| **db2** | `TRAN_DATE >= cutoff` (~2 tháng gần) | **Bare names** — `STRANS`, `PMTRANS`, `TRANSHDR` (không `_YYYYMM`) |
| **db1** | `TRAN_DATE < cutoff` | `STRANS_YYYYMM` / `PMTRANS_YYYYMM` tới `archive_newest_ym` |

**db2** còn chứa toàn bộ **master** (SKU, khách, NCC, giá, …) và **báo cáo** (`WebRpt_*`) — không phụ thuộc cutoff.

Brief trải cả hai khoảng: query db2 (gần) + db1 shards (xa), `UNION ALL` — merge ở analyst, không join cross-DB.

## Cấu trúc thư mục

| Path | Mục đích |
|------|----------|
| `tables/db1/*.md` | 4 bảng archive lịch sử |
| `tables/db2/*.md` | 36 bảng live / master / báo cáo |
| `domain_definitions.md` | TRANS_CODE, PMT_CODE, cutoff, join keys |
| `sensitive_columns.md` | Cột chặn theo role |
| `db1/README.md` + `db1/shards.yaml` | Shard theo tháng |
| `db2/README.md` | Index nhóm bảng db2 |

## Regenerate

```bash
python scripts/generate_data_dictionary.py
```

## Agent usage

- Chọn **đúng thư mục** (`db1` vs `db2`) theo khoảng `TRAN_DATE` trong brief.
- db1: map logical → physical shard qua `db1/shards.yaml`.
- Mô tả cột trong markdown — RAG excerpt, không load full file vào prompt.
- Text varchar có thể TCVN3 — decode trước hiển thị (`tcvn3_to_unicode`).

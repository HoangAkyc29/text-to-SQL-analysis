# db1 — schema overview

db1 có **4 logical table**, **59 physical table** (57 shard theo tháng + 2 archive).

Agent **không** cần đọc 59 file — đọc 4 file trong `tables/` + file này + `shards.yaml`.

## Logical tables

| Logical | Physical pattern | Shards | Mô tả |
|---------|------------------|--------|-------|
| `STRANS` | `STRANS_{YYYYMM}` | 202312..202604 (29) | [TODO: mô tả nghiệp vụ bảng STRANS — chi tiết dòng giao dịch] |
| `PMTRANS` | `PMTRANS_{YYYYMM}` | 202401..202604 (28) | [TODO: mô tả nghiệp vụ bảng PMTRANS — thanh toán] |
| `CRDTRANS_ARC` | `CRDTRANS_ARC` | 1 (archive) | [TODO: mô tả nghiệp vụ bảng CRDTRANS_ARC — archive thẻ/điểm] |
| `TRANSHDR_ARC` | `TRANSHDR_ARC` | 1 (archive) | [TODO: mô tả nghiệp vụ bảng TRANSHDR_ARC — archive header giao dịch] |

## Cách chọn physical table

1. Xác định logical table (VD `STRANS`).
2. Lọc theo `TRAN_DATE` trong brief/filter.
3. Map tháng → suffix `YYYYMM` → VD `STRANS_202503`.
4. Khoảng nhiều tháng: `UNION ALL` các shard tương ứng (không join cross-shard trên server nếu không cần).

## Quan hệ (placeholder — user điền)

- `STRANS` ↔ `TRANSHDR_ARC`: [TODO: join key, cardinality]
- `STRANS` ↔ `PMTRANS`: [TODO]
- `CRDTRANS_ARC` ↔ `STRANS` / thẻ: [TODO]

## File liên quan

- `tables/STRANS.md`, `tables/PMTRANS.md`, `tables/CRDTRANS_ARC.md`, `tables/TRANSHDR_ARC.md` — cột + type
- `shards.yaml` — danh sách physical table đầy đủ
- `../domain_definitions.md` — thuật ngữ nghiệp vụ (TRANS_CODE, …)

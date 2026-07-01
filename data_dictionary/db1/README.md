# db1 — lịch sử (RESTORED_DB)

db1 là **archive giao dịch quá khứ**. Dữ liệu giao dịch ở đây có `TRAN_DATE` **trước** ngưỡng rolling — tức trước ngày 1 của tháng trước (so với hôm nay).

Ví dụ hôm nay **22/06/2026**:
- `cutoff = 2026-05-01`
- db1: giao dịch **trước** 01/05/2026 (tháng 4 và cũ hơn)
- db2: giao dịch **từ** 01/05/2026 đến nay

## Logical tables (4)

| Logical | Physical | Shards | Mô tả |
|---------|----------|--------|-------|
| `STRANS` | `STRANS_{YYYYMM}` | 29 | Chi tiết dòng bán lịch sử |
| `PMTRANS` | `PMTRANS_{YYYYMM}` | 28 | Thanh toán bill lịch sử |
| `CRDTRANS_ARC` | `CRDTRANS_ARC` | 1 | Giao dịch thẻ/điểm archive |
| `TRANSHDR_ARC` | `TRANSHDR_ARC` | 1 | Header bill archive |

Schema: `../tables/db1/<TênBảng>.md` + `shards.yaml` + `../domain_definitions.md`

## Chọn physical table

1. Xác nhận khoảng thời gian **nằm hoàn toàn trước cutoff** — nếu không, dùng db2.
2. Lọc `TRAN_DATE` theo brief.
3. Suffix `YYYYMM` → vd. `STRANS_202503`.
4. Nhiều tháng: `UNION ALL` các shard.

## Quan hệ

- `TRANSHDR_ARC` 1 — N `STRANS` / `PMTRANS` (shard): `TRANS_NUM` + `TRANS_CODE` + `TRAN_DATE`
- `CRDTRANS_ARC` ↔ `CARD_ID` (master thẻ trên db2 `CSCARD`)

## Không có trên db1

Danh mục (SKU, khách, NCC, giá, …) — luôn query **db2**.

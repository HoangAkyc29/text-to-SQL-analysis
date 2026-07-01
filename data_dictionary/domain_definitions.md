# Domain glossary

Thuật ngữ và mã nghiệp vụ dùng chung (suy luận từ dữ liệu mẫu — xác nhận với nghiệp vụ).

## Phân tách db1 / db2 theo thời gian

**Ngưỡng rolling** (tính khi chạy query):

```
cutoff = ngày 1 của tháng trước (so với GETDATE())
```

| | db1 (lịch sử) | db2 (live) |
|---|---------------|------------|
| Giao dịch | `TRAN_DATE < cutoff` | `TRAN_DATE >= cutoff` |
| Ví dụ 22/06/2026 | trước 01/05/2026 | từ 01/05/2026 đến nay |
| Ý nghĩa | Archive shard theo tháng | ~2 tháng gần nhất + master |

- **Master** (SKU, khách, NCC, giá, thẻ, …): chỉ **db2**.
- Brief trải cutoff: `UNION ALL` db2 + db1 shards — merge ở analyst.

## TRANS_CODE — loại chứng từ

| Mã | Ý nghĩa |
|----|---------|
| `113` | Bán lẻ — header (TRANSHDR) và dòng hàng (STRANS) |
| `221` | Thanh toán bill bán (PMTRANS, TRANSHDR_ARC) |
| `008` | Thu/chi quỹ tiền mặt (PMTRANS; AMOUNT có thể âm khi chi) |
| `222` | Thanh toán / điều chỉnh khác trên PMTRANS (cần xác nhận) |
| `010` | Kiểm đếm quỹ tiền mặt theo mệnh giá (CASH_ST) |
| `334` | Đơn đặt hàng / chuyển kho (ST_ORDER) |
| `811` | Giao dịch thẻ loyalty live (CRDTRANS, db2) |
| `812` | Giao dịch thẻ loyalty archive (CRDTRANS_ARC, db1) |
| `821` | Xuất/nhập kho thẻ PM gift/voucher |
| `320`, `340`, `310`, `318`, `316` | Loại chứng từ khác trên STRANS (điều chỉnh, KM, …) — cần map đầy đủ |

## PMT_CODE — hình thức thanh toán

| Mã | Ý nghĩa |
|----|---------|
| `CASH` | Tiền mặt |
| `CARD` | Thẻ |
| `BANK` | Chuyển khoản |
| `OWNCP` | Thanh toán nội bộ công ty (cần xác nhận) |

## Định danh

- `TRANS_NUM`: số bill; join TRANSHDR ↔ STRANS ↔ PMTRANS
- `STK_ID`: cửa hàng/kho (`10001`, `10004`, `10005`, …)
- `CARD_ID`: thẻ loyalty; prefix `A`, `E`, `F`, `H` (hạng/loại thẻ — cần xác nhận)
- `@P…`: thẻ PM (gift/voucher)

## Điểm thưởng

- `MARK`: điểm tích lũy
- Quy tắc quan sát: `AMOUNT / MARK ≈ 50,000` trên giao dịch `811` (1 điểm ≈ 50k VND doanh thu)
- `TRANS_CODE=221` thường dùng khi tính điểm từ thanh toán bán

## VIP / lọc thẻ

- VIP có thể lọc theo prefix `CARD_ID` (vd. `E…`) hoặc `DISC_LVL` / tier trên `CSCARD` — user định nghĩa rule cụ thể

## Store filter

- Role `store_manager`: bắt buộc lọc `STK_ID` theo cửa hàng được phép

## db1 shard

- `STRANS_{YYYYMM}`, `PMTRANS_{YYYYMM}`: chọn physical table theo tháng của `TRAN_DATE` (chỉ khi `TRAN_DATE < cutoff`)

## Mã hàng / barcode / PLU

User thường không hiểu format mã trong DB:

| Input user | Tra cứu | Ghi chú |
|------------|---------|---------|
| 6–8 chữ số, có thể thiếu số 0 đầu | `SKU_DEF.SKU_CODE`, `BARCODE.BARCODE` | LPAD 8 ký tự; thử `LIKE '%suffix'` |
| 10–13 chữ số | `BARCODE`, `SKU_DEF.UPC_CODE` | EAN/GTIN |
| Mã dài trên bill | **Không** filter trực tiếp như SKU master | Có thể là line id — join `TRANS_NUM` + dòng `STRANS` |

Join path: user barcode → `BARCODE` → `SKU_ID` → `STRANS.SKU_ID`.

Khi query chính trả 0 dòng nhưng probe master có kết quả → **identifier mismatch**, không phải “không bán”.

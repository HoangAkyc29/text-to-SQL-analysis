# Domain glossary

Thuật ngữ và mã nghiệp vụ dùng chung (suy luận từ dữ liệu mẫu — xác nhận với nghiệp vụ).

## Phân tách db1 / db2 theo thời gian

**Ngưỡng rolling** (tính khi chạy query):

```
cutoff = ngày 1 của tháng trước (so với GETDATE() / as_of)
archive_newest_ym = tháng trước cutoff (YYYYMM) — hậu tố shard mới nhất được phép trên db1
```

| | db1 (lịch sử) | db2 (live + gần) |
|---|---------------|------------------|
| Giao dịch | `TRAN_DATE < cutoff` | `TRAN_DATE >= cutoff` |
| Tên bảng fact | `STRANS_YYYYMM` / `PMTRANS_YYYYMM` (suffix động tới `archive_newest_ym`) | **Bare name only** — `STRANS`, `PMTRANS`, `TRANSHDR`, `CRDTRANS` — **không** `_YYYYMM` |
| Ví dụ 15/07/2026 | cutoff=`2026-06-01`; shard mới nhất `…_202605` | từ 01/06/2026; bảng `STRANS` (không `STRANS_202607`) |
| Ý nghĩa | Archive shard theo tháng | ~2 tháng gần nhất + master |

- **Master** (SKU, khách, NCC, giá, thẻ, …): chỉ **db2**, bare names.
- Brief trải cutoff: `UNION ALL` db2 + db1 shards — merge ở analyst.
- `CRDTRANS_ARC` / `TRANSHDR_ARC` trên db1 cũng **không** có hậu tố tháng.

## TRANS_CODE — loại chứng từ

| Mã | Ý nghĩa |
|----|---------|
| `113` | Bán lẻ (một loại chứng từ trên TRANSHDR / STRANS) |
| `221` | Thanh toán bill — xuất hiện trên **PMTRANS** và cũng rất phổ biến trên **STRANS / TRANSHDR** live |
| `008` | Thu/chi quỹ tiền mặt (PMTRANS; AMOUNT có thể âm khi chi) |
| `222` | Thanh toán / điều chỉnh khác trên PMTRANS (cần xác nhận) |
| `010` | Kiểm đếm quỹ tiền mặt theo mệnh giá (CASH_ST) |
| `334` | Đơn đặt hàng / chuyển kho (ST_ORDER) |
| `811` | Giao dịch thẻ loyalty live (CRDTRANS, db2) |
| `812` | Giao dịch thẻ loyalty archive (CRDTRANS_ARC, db1) |
| `821` | Xuất/nhập kho thẻ PM gift/voucher |
| `320`, `340`, `310`, `318`, `316` | Loại chứng từ khác trên STRANS (điều chỉnh, KM, …) — cần map đầy đủ |

**Lưu ý:** `STRANS` / `TRANSHDR` mang **nhiều** `TRANS_CODE` (`113`, `221`, `310`, …). Không suy ra mọi dòng hàng đều là `113`. **Không** thêm `WHERE TRANS_CODE = …` cho phân tích SKU / số lượng / giá trị bill trừ khi brief (hoặc domain rule / case study) chỉ rõ loại chứng từ. Chọn filter theo brief + retrieval, không theo mặc định cứng trong glossary.

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

- `STRANS_{YYYYMM}`, `PMTRANS_{YYYYMM}`: chỉ khi `TRAN_DATE < cutoff`; hậu tố mới nhất = `archive_newest_ym` (tháng trước cutoff), expand động lúc runtime — không hard-freeze danh sách tháng trong YAML.
- Trên **db2** cùng logical fact: dùng `STRANS` / `PMTRANS` **không** hậu tố.
- `TRANSHDR_ARC` / `CRDTRANS_ARC`: bare name trên db1.

## Mã hàng / barcode / PLU

User thường không hiểu format mã trong DB:

| Input user | Tra cứu | Ghi chú |
|------------|---------|---------|
| 6–8 chữ số, có thể thiếu số 0 đầu | `SKU_DEF.SKU_CODE`, `BARCODE.BARCODE` | LPAD 8 ký tự; thử `LIKE '%suffix'` |
| 10–13 chữ số | `BARCODE`, `SKU_DEF.UPC_CODE` | EAN/GTIN |
| Mã dài trên bill | **Không** filter trực tiếp như SKU master | Có thể là line id — join `TRANS_NUM` + dòng `STRANS` |

Join path: user barcode → `BARCODE` → `SKU_ID` → `STRANS.SKU_ID`.

Khi query chính trả 0 dòng nhưng probe master có kết quả → **identifier mismatch**, không phải “không bán”.

### Tên hiển thị (`SKU_DEF.FULL_NAME`) vs loại hàng

- Prefix / từ trong `FULL_NAME` (vd. ký hiệu khuyến mãi trên nhãn) **không** phải ontology “loại hàng” ổn định.
- Khi user đã đưa `SKU_CODE` / mã SP: lấy hàng theo mã; **không** suy type từ chuỗi tên.
- “Quà tặng” / gift / khuyến mãi: ưu tiên cột / rule trong dictionary (AMOUNT dòng, GDISC/GCOMM, …) hoặc hỏi clarify khi **không** có mã và schema không có cột type — không map từ prefix tên.

## Tên hiển thị vs loại hàng (quà / KM)

- `SKU_DEF.FULL_NAME` là **tên hiển thị**, không phải ontology loại hàng.
- Prefix / substring trên tên (vd. mã ngắn kiểu KM, chữ “quà”, …) **không** đủ để khẳng định product type.
- Khi user đã chỉ `SKU_CODE` / product code: resolve theo mã là đủ; soft phrase (“dạng quà tặng”) chỉ là ngữ cảnh — xác nhận type qua cột dictionary / clarify khi **không** có mã hoặc resolve đa nghĩa.
- Dòng quà/KM trên fact: xem mô tả cột `AMOUNT` (có thể 0), `GDISC_*` / `GCOMM_*`, và glossary TRANS_CODE khi brief yêu cầu loại chứng từ — không suy từ `FULL_NAME` alone.

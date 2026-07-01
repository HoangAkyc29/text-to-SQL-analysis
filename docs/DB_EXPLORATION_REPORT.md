# Database Exploration Report — Ý nghĩa bảng & giá trị

Tài liệu đúc kết từ khám phá read-only (`SELECT TOP 20` / bảng) trên `RESTORED_DB` (db1) và `RESTORED_DB2` (db2).  
Mục tiêu: mô tả **bảng dùng để làm gì** và **các giá trị/cột quan trọng nghĩa là gì** — phục vụ `data_dictionary` và agent.

> Các mã nghiệp vụ (`TRANS_CODE`, …) là **suy luận từ dữ liệu mẫu** — cần bạn xác nhận/bổ sung khi có tài liệu chính thức.

---

## 1. Hai database

| DB | Tên SQL | Vai trò |
|----|---------|---------|
| **db1** | `RESTORED_DB` | **Lịch sử** — archive giao dịch có `TRAN_DATE` **trước** ngưỡng rolling; shard `STRANS_YYYYMM`, `PMTRANS_YYYYMM` + `*_ARC` |
| **db2** | `RESTORED_DB2` | **Live** — danh mục (SKU, khách, NCC, giá, …), chứng từ **~2 tháng gần nhất**, staging POS, báo cáo `WebRpt_*` |

### Ngưỡng rolling giữa db1 và db2

Tính theo ngày chạy query:

- **`cutoff`** = ngày **1** của **tháng trước** (so với hôm nay).
- Ví dụ hôm nay **22/06/2026** → `cutoff = 2026-05-01`.

| Phạm vi | Điều kiện | Ý nghĩa |
|---------|-----------|---------|
| **db2** (gần) | `TRAN_DATE >= cutoff` | Khoảng **~2 tháng**: trọn tháng trước + phần đã qua của tháng hiện tại (vd. từ 01/05 đến 22/06) |
| **db1** (xa) | `TRAN_DATE < cutoff` | **Lịch sử** từ tháng trước đó nữa trở về quá khứ (vd. trước 01/05/2026) |

**db2** luôn chứa **master** và **báo cáo** — không phụ thuộc cutoff. **db1** không có danh mục; join `CARD_ID` → `CSCARD` trên db2 khi cần.

**Liên kết logic:** `STRANS`, `PMTRANS`, `TRANSHDR`, `CRDTRANS` trên db2 cùng schema với db1 (shard / `*_ARC`). Query xa cutoff → db1 + đúng shard; gần cutoff hoặc master → db2. Brief trải cả hai: `UNION ALL`, merge ở analyst.

---

## 2. Mã & giá trị dùng chung (nhiều bảng)

### 2.1 `TRANS_CODE` — loại chứng từ

| Mã | Thường gặp ở | Ý nghĩa (suy luận) |
|----|--------------|-------------------|
| `113` | TRANSHDR, STRANS | Bán lẻ — phiếu/header và dòng hàng |
| `221` | PMTRANS | Thanh toán gắn bill bán |
| `008` | PMTRANS | Thu/chi quỹ (số tiền lớn, không phải dòng SKU) |
| `811` | CRDTRANS | Giao dịch thẻ loyalty (tích/điều chỉnh điểm) |
| `812` | CRDTRANS_ARC | Tương tự `811` (archive) |
| `821` | PMCRDISS, PMCRDSTK | Xuất/nhập kho thẻ PM (gift/voucher) |
| `222`, `320`, `340`, `010`, `310` | PMTRANS / STRANS | Loại chứng từ khác (điều chuyển, điều chỉnh, …) — **cần map đầy đủ** |

### 2.2 `PMT_CODE` — hình thức thanh toán (PMTRANS)

| Giá trị | Ý nghĩa |
|---------|---------|
| `CASH` | Tiền mặt |
| `CARD` | Thẻ |
| `BANK` | Chuyển khoản / ngân hàng |
| `OWNCP` | Loại thanh toán nội bộ/công ty (cần xác nhận) |

*(Trong DB thường có trailing space sau mã.)*

### 2.3 Định danh

| Cột | Ý nghĩa | Giá trị mẫu |
|-----|---------|-------------|
| `TRANS_NUM` | Số chứng từ / bill (nối header ↔ dòng ↔ thanh toán) | `000001132605000001` |
| `STK_ID` | Mã cửa hàng / kho | `10001`, `10004`, `10005`, `20001`, `20002` |
| `BU_ID` | Đơn vị kinh doanh / chi nhánh logic | `00000`, `90100`, `90200` |
| `CARD_ID` | Mã thẻ loyalty | Prefix `A`, `E`, `F`, `H` — có thể phân loại hạng thẻ |
| `CUST_ID` | Mã khách hàng | `230000000001`, … |
| `SKU_ID` | Mã sản phẩm (nội bộ) | `290002726400`, … |
| `WS_ID` / `POS_ID` / `SHIFT` | Máy trạm / quầy / ca làm việc | — |
| `CYS` | Loại tiền | `VND` |

### 2.4 Loyalty / điểm (CRDTRANS)

| Cột | Ý nghĩa |
|-----|---------|
| `AMOUNT` | Giá trị tiền liên quan giao dịch điểm |
| `MARK` | Điểm tích/lũy |
| `MARK_VAL`, `MARK_MUL` | Hệ số / giá trị quy đổi điểm |
| `ACML_CODE` | Mã chương trình tích lũy |
| `TRANS_TYPE`, `TYPE`, `RS_CODE` | Phân loại / lý do giao dịch điểm |

**Quy tắc quan sát:** `AMOUNT / MARK ≈ 50,000` (1 điểm ≈ 50k VND doanh thu) trên mẫu `811`.

### 2.5 Khác

| Cột / nhóm | Ý nghĩa |
|------------|---------|
| `POST`, `STATUS`, `ACTION` | Trạng thái duyệt / đã post / thao tác |
| `*_DISC_*` (CDISC, TDISC, MDISC, GDISC) | Các lớp chiết khấu: coupon, transaction, manual, gift |
| `VAT_AMT`, `TAX_CODE` | Thuế |
| `UNIT_SYMB`, `BASE_UNIT`, `UNITCONV` | Đơn vị bán và quy đổi (GOI, HOP, KG, …) |

---

## 3. db1 — `RESTORED_DB`

### 3.1 `STRANS` (logical) — `STRANS_YYYYMM` × 29 bảng

**Mục đích:** Chi tiết từng dòng trên chứng từ bán (SKU, SL, giá, CK, VAT, quà…).  
**Chọn bảng:** `STRANS_{YYYYMM}` theo `TRAN_DATE` (vd. tháng 03/2025 → `STRANS_202503`).  
**Quy mô:** ~7M dòng tổng (metadata JSON).

| Nhóm cột | Ý nghĩa |
|----------|---------|
| `TRANS_NUM`, `TRANS_CODE`, `TRAN_DATE`, `IDX` | Khóa dòng; `IDX` = số thứ tự dòng trong bill |
| `SKU_ID`, `QTY`, `AMOUNT`, `PRICE` | Hàng bán: mã SP, số lượng, thành tiền |
| `STK_ID`, `STK_TYPE`, `OSTK_ID` | Kho xuất / loại kho |
| `INV_*` | Thông tin hóa đơn GTGT gắn dòng |
| `CDISC_*`, `TDISC_*`, `MDISC_*`, `GDISC_*`, `GIFT_*` | Chiết khấu & quà tặng theo từng lớp |
| `CARD_ID`, `CS_ID`, `STAFF_ID` | Thẻ KH / ca / nhân viên |
| `ASSO_ID`, `KIT_*`, `PACK_*` | Combo / kit / đóng gói |

**Giá trị mẫu:** `TRANS_CODE` chủ yếu `113`, `221`; `AMOUNT=0` xuất hiện trên dòng quà/KM.

---

### 3.2 `PMTRANS` (logical) — `PMTRANS_YYYYMM` × 28 bảng

**Mục đích:** Dòng thanh toán của bill (`TRANS_NUM` + `TRANS_CODE=221` thường đi với bán lẻ).  
**Chọn bảng:** `PMTRANS_{YYYYMM}` theo `TRAN_DATE`.

| Cột | Ý nghĩa |
|-----|---------|
| `PMT_CODE` | Tiền mặt / thẻ / bank (xem §2.2) |
| `AMOUNT` | Số tiền thanh toán |
| `FOREX_RATE`, `FOREX_AMT` | Tỷ giá / số tiền ngoại tệ (nếu có) |
| `ROUNDIFF` | Lệch làm tròn |
| `CARD_ID`, `CUST_ID` | Thẻ / khách (có thể rỗng với CASH) |

---

### 3.3 `TRANSHDR_ARC`

**Mục đích:** Archive **header** giao dịch — một dòng tổng per bill (~3.7M dòng).  
**Liên kết:** `TRANS_NUM` + `TRANS_CODE` với STRANS / PMTRANS.

| Cột | Ý nghĩa |
|-----|---------|
| `AMOUNT` | Tổng tiền bill |
| `CUST_ID`, `CARD_ID`, `SUPP_ID` | Khách / thẻ / NCC liên quan |
| `EXP_*`, `IMP_*`, `REF_*` | Chiều xuất/nhập, tham chiếu chứng từ |
| `PMT_MODE`, `PMT_TYPE` | Hình thức thanh toán tổng |
| `DUE_DATE`, `EF_DATE` | Hạn / ngày hiệu lực |

---

### 3.4 `CRDTRANS_ARC`

**Mục đích:** Archive giao dịch **thẻ / điểm** (~1.6M dòng).

| Cột | Ý nghĩa |
|-----|---------|
| `TRANS_CODE` | Mẫu: `812` |
| `CARD_ID` | Thẻ bị ảnh hưởng |
| `AMOUNT`, `MARK`, `DISCOUNT` | Tiền / điểm / giảm giá |
| `STK_ID` | Cửa hàng phát sinh (mẫu: `10001`) |
| `REMARK` | Ghi chú nghiệp vụ (vd. cân đối quỹ thu ngân) |

---

## 4. db2 — `RESTORED_DB2`

### 4.1 Giao dịch (live)

#### `TRANSHDR` (~87k dòng)

Header bill **hiện tại** — cùng vai trò `TRANSHDR_ARC`. Mẫu: `TRANS_CODE=113`, ngày 2026-05.

#### `STRANS` (~420k dòng)

Chi tiết dòng bán live — schema = STRANS shard db1. Dùng cho giao dịch gần, không cần chọn shard.

#### `PMTRANS` (~124k dòng)

Thanh toán live — schema = PMTRANS shard db1.

#### `CRDTRANS` (~38k dòng)

Giao dịch thẻ live — `TRANS_CODE=811` trên mẫu; cùng schema `CRDTRANS_ARC`.

#### `CTRANS` (~51k dòng)

Chứng từ **tài chính / công nợ** (không phải POS thuần): `ACCOUNT_ID`, `DEBT_NO`, `TAX_*`, `INV_*`.

#### `CASH_ST` (~15k dòng)

Tổng hợp **quỹ tiền mặt** theo ngày/ca: `PMT_CODE`, `VALUE`, `QTY`, `SHIFT`.

#### `SUSPEND` (~906k dòng)

Bill **treo** tại quầy (chưa hoàn tất) — schema gần STRANS; không dùng cho báo cáo chính thức đã post.

#### `STRANS_TMP` / `CRDTRANS_TMP`

Staging trước khi post — volume lớn; dữ liệu tạm.

---

### 4.2 Khách hàng & thẻ

#### `CUSTOMER` (~47k)

Master khách: `CUST_NAME`, địa chỉ, MST (`TAX_ID`), `CARD_ID` gắn, `DEBT_MODE`, hạn `DUE_DATE`. `TYPE` mẫu: `03`.

#### `CSCARD` (~45k)

Master thẻ loyalty: `CARD_ID`, `BARCODE`, `NAME`, `DISC_LVL`, `ISS_DATE` / `DUE_DATE`, địa chỉ liên hệ.

#### `CRD_INFO` (~52k)

Số dư tích lũy theo kỳ: `BEG_*` (đầu kỳ), `BUY_*` (phát sinh mua), `ACML_CODE`, `LAST_DATE`.

#### `CUSTHIST` (~230k)

Lịch sử mua theo SKU: `SKU_ID`, `QTY`, `AMOUNT` per `TRANS_NUM` — phân tích hành vi.

#### `CustSumm` (~13k)

Tóm tắt KH + thẻ (tên, SĐT, tổng `Amount`) — denormalized, tiện tra cứu nhanh.

---

### 4.3 Sản phẩm

#### `SKU_DEF` (~116k)

Master SKU: `SKU_CODE`, `BARCODE`, tên, nhóm, đơn vị, giá, thuế, thuộc tính in nhãn.

#### `PLU` (~4k)

Giá bán theo quầy (`RTPRICE`, `LASTRTPR`) và hiệu lực `FR_DATE`–`TO_DATE`.

#### `BARCODE` (~44k)

Barcode phụ / đơn vị quy đổi (`UNITCONV`, `ISDEFAULT`) cho từng `SKU_ID`.

#### `ASSOLST` / `ASSO_INF`

Combo/bundle: header (`ASSO_ID`, `ASSO_TYPE`) + thành phần (`SKU_ID`, `QTY`, `PRICE`, `RATIO`).

#### `sku_activity` (~54k)

Ngày bán/nhập đầu–cuối theo `stk_id` × `sku_id`.

---

### 4.4 NCC & đối tác

#### `SUPPLIER` (~1.8k) / `PARTNER` (~1.8k)

Master nhà cung cấp / đối tác: mã, tên, MST, tài khoản, hạn thanh toán, hạn mức `CR_LIMIT`.

---

### 4.5 Giá & khuyến mãi

#### `HISRTPR` (~22k)

Lịch sử **giá bán lẻ** theo ngày × SKU × cửa hàng (`RTPRICE`, `LASTRTPR`).

#### `HISSPPR` (~92k)

Lịch sử **giá mua** NCC (`SPPRICE`, `SUPP_ID`).

#### `RDISCINF` (~19k)

Rule khuyến mãi: điều kiện `SOLD_QTY`/`BUY_AMT`, đối tượng thẻ/KH, `CHG_TYPE`/`CHG_VALUE`, thời gian `FR_DATE`–`TO_DATE`.

---

### 4.6 Kho & hóa đơn

#### `STK_DTL` (~112k)

Sổ tồn kho theo kỳ: nhập/xuất/bán/điều chuyển (`FR*` đầu kỳ, `TO*` cuối kỳ) per `STK_ID` × `SKU_ID`.

#### `ST_ORDER` (~2.2k)

Đơn đặt hàng / chuyển kho: timeline giao (`DELIVER_DT`), SL đặt `ORD_QTY`, đã giao `DLV_QTY`, giá `ORD_PRICE`.

#### `INV_HDR` / `INV_ISS`

Hóa đơn GTGT điện tử: `INV_NO`, `EINV`, `TAX_ID`, người mua/bán, `AMOUNT`, `VAT_AMT`. `INV_ISS` gắn `TRANS_NUM` bán lẻ.

---

### 4.7 Thẻ PM (gift / voucher)

| Bảng | Mục đích |
|------|----------|
| `PMCRDINF` (~426k) | Thông tin thẻ PM: mệnh giá `VALUE_AMT`, trạng thái `ACTIVATE`, `SALEABLE` |
| `PMCRDSTK` (~32k) | Tồn thẻ tại cửa hàng (`FR_SERI`–`TO_SERI`, `STK_QTY`) |
| `PMCRDISS` (~31k) | Phiếu xuất thẻ cho KH (`TRANS_CODE=821`, `FR_CARDID`→`TO_CARDID`) |
| `PMCRDRCV` (~2k) | Thu hồi / nhận lại thẻ |

Prefix thẻ PM mẫu: `@P`.

---

### 4.8 Tài chính

#### `ACCOUNT` (~1.8k)

Tài khoản công nợ: `CR_LIMIT`, `CR_AMT`, `Y_CREDIT`/`Y_DEBIT`, gắn `CUST_ID` / `SUPP_ID`.

#### `DEBT` (~225k)

Chứng từ công nợ: `DEBT_NO`, `DEBT_AMT`, `PAID_AMT`, `DUE_DATE`, liên kết hóa đơn `INV_*`.

---

### 4.9 Báo cáo sẵn (`WebRpt_*`) — ưu tiên cho agent

#### `WebRpt_sales_sku_daily`

Doanh thu SKU × cửa hàng × ngày: `qty`, `revenue`, `cogs`, `gross_profit`, tách từng loại chiết khấu (`mdisc_total`, `tdisc_total`, …).

#### `WebRpt_inventory_daily` (~2.2M dòng)

Tồn kho ngày: `qty_onhand`, `value_onhand`, `doi_days`, `days_no_sale`, `stock_status` (vd. `WARN - Discontinued`, `INFO - Never Sold`).

#### `WebRpt_rfm_snapshot`

RFM loyalty: `recency_days`, `frequency`, `monetary`, `rfm_segment` (`At Risk`, `Loyal`, `Others`), `rfm_score`.

---

## 5. Gợi ý tra cứu theo câu hỏi

| Câu hỏi | Bảng gợi ý |
|---------|------------|
| Doanh thu / lãi theo SKU, ngày | `WebRpt_sales_sku_daily` |
| Tồn kho, DOI, hàng chậm | `WebRpt_inventory_daily` |
| Phân khúc KH loyalty | `WebRpt_rfm_snapshot`, `CSCARD` |
| Chi tiết bill gần đây | db2: `TRANSHDR` + `STRANS` + `PMTRANS` |
| Lịch sử xa | db1: shard `STRANS_*` / `PMTRANS_*` theo tháng |
| Điểm / thẻ | `CRDTRANS`, `CRD_INFO`, `CSCARD` |
| KM đang chạy | `RDISCINF` |
| Công nợ | `DEBT`, `ACCOUNT`, `CTRANS` |

---

*Tái tạo số liệu mẫu (không ghi đè file này): `python scripts/explore_db_deep.py` — script chỉ cập nhật `docs/db_exploration_samples/`; report ngữ nghĩa chỉnh tay hoặc theo PR riêng.*

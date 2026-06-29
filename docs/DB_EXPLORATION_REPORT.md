# Database Exploration Report

Tài liệu tổng hợp khám phá **read-only** trên SQL Server local.

## Phạm vi & giới hạn

- Server: `DESKTOP-AUQEDC5`
- **db1** `RESTORED_DB` — 59 bảng (từ JSON export)
- **db2** `RESTORED_DB2` — 38 bảng (từ JSON export)
- Mỗi bảng: `SELECT TOP 20` only
- User: `analysisagentreadonly` (readonly)
- Lỗi kết nối/query: db1=0, db2=0

## Tóm tắt điều hành

1. **db1** = archive giao dịch băm tháng (`STRANS_*`, `PMTRANS_*`) + 2 bảng archive (`*_ARC`).
2. **db2** = master (KH, SKU, NCC), giao dịch live, staging (`SUSPEND`, `*_TMP`), báo cáo `WebRpt_*`.
3. Schema **STRANS/PMTRANS/TRANSHDR/CRDTRANS** giống hệt giữa db1 shard/arc và db2 live.
4. **`TRANS_CODE` 221** = thanh toán bán; **113** = bán lẻ (header+dòng); **008** = quỹ; **811/812/821** = thẻ/PM.
5. **`PMT_CODE`**: CASH, CARD, BANK, OWNCP.
6. **Điểm:** `AMOUNT/MARK ≈ 50,000` trên CRDTRANS.
7. **Thẻ:** prefix `A`, `E`, `@P` (voucher PM); cửa hàng `STK_ID` chủ yếu `10001`, `10004`, `10005`.
8. **TCVN3:** 40 bảng db1 + 19 bảng db2 có text cần decode — xem `project_core/text/tcvn3.py`.
9. **Agent:** ưu tiên `WebRpt_*` cho aggregate; raw STRANS chỉ khi cần chi tiết.

Tái tạo report: `python scripts/explore_db_deep.py`

## TCVN3 → Unicode

Nhiều cột text (đặc biệt `varchar`/`char`) lưu tiếng Việt theo **TCVN3** (ABC/VNI legacy),
khi đọc qua ODBC có thể hiện mojibake. Report dùng bộ map chuẩn trong:
`packages/project-core/src/project_core/text/tcvn3.py` (`tcvn3_to_unicode`).

Sẽ cần expose thành tool/post-process cho SQL gateway / sandbox để output agent luôn Unicode.

## RESTORED_DB (db1)

### Tổng hợp chéo bảng (từ mẫu)

**TRANS_CODE** (tần suất trong mẫu):

- `221`: 302 dòng mẫu
- `008`: 255 dòng mẫu
- `113`: 225 dòng mẫu
- `320`: 154 dòng mẫu
- `340`: 119 dòng mẫu
- `222`: 46 dòng mẫu
- `812`: 20 dòng mẫu
- `317`: 20 dòng mẫu
- `010`: 17 dòng mẫu
- `310`: 10 dòng mẫu
- `316`: 5 dòng mẫu
- `211`: 5 dòng mẫu
- `009`: 1 dòng mẫu
- `318`: 1 dòng mẫu

**PMT_CODE**:

- `CASH`: 517
- `BANK`: 24
- `CARD`: 15
- `OWNCP`: 4

**CARD_ID prefix** (ký tự đầu):

- `A`: 28
- `E`: 24
- `@`: 4

**STK_ID** (cửa hàng/kho, top mẫu):

- `10001`: 542
- ``: 293
- `10004`: 230
- `10005`: 84
- `20002`: 17
- `20001`: 14

**Shard month:** mẫu khớp suffix `_YYYYMM` (không phát hiện lệch).


**Bảng có text TCVN3 cần decode** (40):

- `CRDTRANS_ARC`
- `PMTRANS_202401`
- `PMTRANS_202403`
- `PMTRANS_202404`
- `PMTRANS_202406`
- `PMTRANS_202407`
- `PMTRANS_202408`
- `PMTRANS_202411`
- `PMTRANS_202412`
- `PMTRANS_202501`
- `PMTRANS_202502`
- `PMTRANS_202503`
- `PMTRANS_202504`
- `PMTRANS_202505`
- `PMTRANS_202506`
- `PMTRANS_202507`
- `PMTRANS_202508`
- `PMTRANS_202509`
- `PMTRANS_202510`
- `PMTRANS_202511`
- `PMTRANS_202512`
- `PMTRANS_202601`
- `PMTRANS_202602`
- `PMTRANS_202603`
- `STRANS_202402`
- `STRANS_202403`
- `STRANS_202404`
- `STRANS_202405`
- `STRANS_202406`
- `STRANS_202407`
- `STRANS_202408`
- `STRANS_202409`
- `STRANS_202503`
- `STRANS_202504`
- `STRANS_202505`
- `STRANS_202507`
- `STRANS_202511`
- `STRANS_202512`
- `STRANS_202601`
- `STRANS_202603`

### Chi tiết theo nhóm

#### db1_archive

##### `TRANSHDR_ARC`

- Rows (metadata JSON): 3,711,486
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-11-08T00:00:00 → 2025-11-08T00:00:00
  - `EF_DATE`: 2025-11-08T00:00:00 → 2025-11-08T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `17:03`, `17:07`, `17:08`, `17:37`, `17:42`, `17:43`, `17:55`, `17:56`, `18:03`, `18:10`
  - `BU_ID`: `90100`
  - `IMP_ID`: `230000032082`, `230000032506`, `239010004170`, `239010004296`, `239010004972`, `239010006451`, `239010006686`, `239010007586`, `239010007615`, `239010008028`
  - `IMP_TYPE`: `03`
  - `EXP_ID`: `10004`
  - `EXP_TYPE`: `01`
  - `PMT_MODE`: `01`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 12966.97 – 767992.28

#### db1_shard

##### `PMTRANS_202401`

- Rows (metadata JSON): 72,923
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-01-01T00:00:00 → 2024-01-28T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`
  - `TRAN_TIME`: `08:34`, `13:59`, `14:19`, `14:38`, `15:07`, `15:59`, `17:03`, `20:50`, `20:55`, `21:00`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `False`, `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -152720.0 – 12458112.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202402`

- Rows (metadata JSON): 61,121
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-02-26T00:00:00 → 2024-02-26T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `16:49`, `16:52`, `16:56`, `16:59`, `17:03`, `17:11`, `17:16`, `17:18`, `17:21`, `17:22`
  - `BU_ID`: `90100`
  - `PMT_CODE`: `BANK`, `CARD`, `CASH`, `OWNCP`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -128056.0 – 500000.0

##### `PMTRANS_202403`

- Rows (metadata JSON): 63,241
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-03-01T00:00:00 → 2024-03-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`
  - `TRAN_TIME`: `14:09`, `14:22`, `14:27`, `14:31`, `15:08`, `16:23`, `16:32`, `16:41`, `16:42`, `16:43`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -440000.0 – 17679072.2
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202404`

- Rows (metadata JSON): 63,891
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-04-07T00:00:00 → 2024-04-24T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`
  - `TRAN_TIME`: `09:39`, `09:40`, `09:41`, `09:42`, `09:43`, `09:44`, `09:51`, `14:16`, `14:57`, `15:04`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1700258.0 – 5915760.8
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202405`

- Rows (metadata JSON): 68,460
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-05-29T00:00:00 → 2024-05-29T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `09:12`, `09:17`, `09:19`, `09:20`, `09:25`, `09:32`, `09:36`, `09:38`, `09:39`, `09:40`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 27000.0 – 282000.0

##### `PMTRANS_202406`

- Rows (metadata JSON): 67,162
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-06-02T00:00:00 → 2024-06-29T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `10:36`, `10:38`, `10:42`, `10:43`, `10:46`, `10:47`, `10:48`, `10:50`, `10:52`, `10:55`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1653844.6 – 3196426.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202407`

- Rows (metadata JSON): 71,330
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-07-05T00:00:00 → 2024-07-11T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `009`, `221`
  - `TRAN_TIME`: `09:17`, `09:19`, `09:50`, `09:53`, `10:02`, `10:03`, `10:05`, `10:06`, `10:11`, `11:40`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -258000.0 – 4967888.6
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202408`

- Rows (metadata JSON): 70,848
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-08-07T00:00:00 → 2024-08-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `15:24`, `15:47`, `16:04`, `16:08`, `16:17`, `16:20`, `16:22`, `16:24`, `16:26`, `21:18`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1486040.01 – 1000000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202409`

- Rows (metadata JSON): 70,590
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-09-27T00:00:00 → 2024-09-27T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `14:34`, `14:51`, `15:02`, `15:21`, `15:27`, `15:32`, `15:37`, `15:39`, `15:44`, `15:49`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 10000.0 – 372000.0

##### `PMTRANS_202410`

- Rows (metadata JSON): 70,703
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-10-02T00:00:00 → 2024-10-02T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `10:50`, `11:07`, `11:44`, `11:49`, `15:14`, `15:19`, `15:23`, `15:25`, `15:32`, `15:52`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -134000.0 – 388000.0

##### `PMTRANS_202411`

- Rows (metadata JSON): 67,462
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-11-04T00:00:00 → 2024-11-27T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`
  - `TRAN_TIME`: `09:07`, `09:18`, `09:19`, `09:22`, `09:24`, `14:16`, `14:22`, `14:28`, `15:13`, `19:49`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1030065.0 – 9743623.2
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202412`

- Rows (metadata JSON): 67,814
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-12-03T00:00:00 → 2024-12-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `16:18`, `16:21`, `16:26`, `16:37`, `17:00`, `17:06`, `17:11`, `17:24`, `17:28`, `17:52`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -349000.0 – 53696300.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202501`

- Rows (metadata JSON): 74,983
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-01-03T00:00:00 → 2025-01-28T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`
  - `TRAN_TIME`: `10:09`, `10:11`, `10:14`, `10:15`, `10:16`, `12:26`, `12:54`, `13:58`, `14:00`, `14:35`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -2794400.0 – 575364800.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202502`

- Rows (metadata JSON): 55,210
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-02-03T00:00:00 → 2025-02-18T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `222`
  - `TRAN_TIME`: `21:21`, `21:22`, `21:23`, `21:24`, `21:25`, `21:26`, `21:27`, `21:28`, `21:29`, `21:30`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -3892528.0 – -30000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202503`

- Rows (metadata JSON): 66,530
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-03-01T00:00:00 → 2025-03-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `14:20`, `15:58`, `17:01`, `17:03`, `18:01`, `18:11`, `19:49`, `19:53`, `19:56`, `20:16`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -123000.0 – 16239108.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202504`

- Rows (metadata JSON): 65,655
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-04-01T00:00:00 → 2025-04-20T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `13:47`, `13:48`, `14:01`, `14:05`, `14:08`, `14:14`, `14:15`, `17:45`, `19:51`, `19:53`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -99000.0 – 44697872.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202505`

- Rows (metadata JSON): 68,696
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-05-01T00:00:00 → 2025-05-25T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `10:17`, `10:19`, `10:22`, `14:12`, `14:15`, `14:16`, `14:17`, `14:20`, `14:21`, `14:23`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -149700.0 – 26739014.6
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202506`

- Rows (metadata JSON): 69,169
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-06-01T00:00:00 → 2025-06-25T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `221`, `222`
  - `TRAN_TIME`: `08:52`, `08:54`, `10:20`, `14:10`, `14:12`, `14:13`, `14:16`, `14:17`, `14:18`, `14:43`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `False`, `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -2550000.0 – 40483702.8
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202507`

- Rows (metadata JSON): 74,789
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-07-09T00:00:00 → 2025-07-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`
  - `TRAN_TIME`: `11:20`, `11:24`, `14:16`, `14:19`, `14:21`, `14:26`, `14:31`, `14:38`, `17:11`, `20:51`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -100732200.0 – 3938000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202508`

- Rows (metadata JSON): 77,980
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-08-01T00:00:00 → 2025-08-10T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`
  - `TRAN_TIME`: `14:18`, `14:28`, `14:29`, `14:32`, `14:35`, `14:47`, `14:53`, `15:35`, `21:34`, `21:36`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 19000.0 – 3497000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202509`

- Rows (metadata JSON): 76,613
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-09-01T00:00:00 → 2025-09-10T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`
  - `TRAN_TIME`: `10:20`, `11:13`, `14:04`, `14:17`, `14:19`, `14:20`, `14:21`, `14:23`, `14:31`, `14:34`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 62000.0 – 2714000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202510`

- Rows (metadata JSON): 78,225
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-10-01T00:00:00 → 2025-10-14T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`
  - `TRAN_TIME`: `13:58`, `14:01`, `14:10`, `14:13`, `14:27`, `14:32`, `14:34`, `14:37`, `15:04`, `15:05`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 207000.0 – 2215000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202511`

- Rows (metadata JSON): 74,851
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-11-01T00:00:00 → 2025-11-27T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`, `221`
  - `TRAN_TIME`: `09:05`, `09:07`, `09:11`, `09:22`, `14:11`, `14:15`, `14:19`, `14:27`, `14:47`, `14:48`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `False`, `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -13782000.0 – 19169256.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202512`

- Rows (metadata JSON): 72,561
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-12-01T00:00:00 → 2025-12-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`
  - `TRAN_TIME`: `10:00`, `13:51`, `14:11`, `14:14`, `14:15`, `14:24`, `14:27`, `14:28`, `14:29`, `14:30`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1721504.0 – 71000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202601`

- Rows (metadata JSON): 71,839
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-01-04T00:00:00 → 2026-01-04T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`, `221`
  - `TRAN_TIME`: `10:38`, `10:41`, `10:43`, `10:48`, `10:53`, `10:55`, `10:56`, `10:58`, `11:00`, `11:07`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CARD`, `CASH`, `OWNCP`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1721000.0 – 1578260.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202602`

- Rows (metadata JSON): 65,946
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-02-02T00:00:00 → 2026-02-16T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`
  - `TRAN_TIME`: `12:29`, `13:03`, `13:05`, `13:11`, `13:26`, `13:35`, `13:54`, `14:01`, `14:03`, `14:45`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -8577000.0 – 265058550.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202603`

- Rows (metadata JSON): 70,968
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-03-01T00:00:00 → 2026-03-11T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `010`, `221`
  - `TRAN_TIME`: `09:24`, `09:26`, `09:27`, `09:30`, `09:36`, `09:37`, `09:40`, `13:31`, `14:13`, `19:47`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `BANK`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -9692000.0 – 1584154.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `PMTRANS_202604`

- Rows (metadata JSON): 69,972
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-04-09T00:00:00 → 2026-04-09T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `08:39`, `08:46`, `08:47`, `08:48`, `08:49`, `08:50`, `08:51`, `08:52`, `08:58`, `08:59`
  - `BU_ID`: `90100`
  - `PMT_CODE`: `BANK`, `CARD`, `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -93200.0 – 1687000.0

##### `STRANS_202312`

- Rows (metadata JSON): 23,583
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2023-12-31T00:00:00 → 2023-12-31T00:00:00
  - `DUE_DATE`: 2023-12-31T00:00:00 → 2023-12-31T00:00:00
  - `EF_DATE`: 2023-12-31T00:00:00 → 2023-12-31T00:00:00
  - `REF_DATE`: 1900-01-01T00:00:00 → 1900-01-01T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `317`
  - `TRAN_TIME`: `21:27`
  - `BU_ID`: `00000`
  - `RS_CODE`: `01`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50337`, `50338`, `50356`, `50419`, `50623`, `50648`, `50720`, `50746`, `50799`, `50840`
  - `OSTK_TYPE`: `05`
  - `UNIT_SYMB`: `CAI`, `GOI`, `KG`, `KHA`, `LO`, `LY`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 169.802
  - `AMOUNT`: 0.0 – 5361818.16

##### `STRANS_202401`

- Rows (metadata JSON): 239,940
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-01-23T00:00:00 → 2024-01-31T00:00:00
  - `EF_DATE`: 2024-01-23T00:00:00 → 2024-01-31T00:00:00
  - `UPDATED`: False → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`, `340`
  - `TRAN_TIME`: `00:00`, `18:36`
  - `BU_ID`: `00000`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`, `02`
  - `OSTK_ID`: `230000025573`
  - `OSTK_TYPE`: `03`
  - `UNIT_SYMB`: `BAO`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `LOC`, `LON`, `THU`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 1.0
  - `AMOUNT`: 0.0 – 3212810.28

##### `STRANS_202402`

- Rows (metadata JSON): 197,239
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-02-01T00:00:00 → 2024-02-07T00:00:00
  - `DUE_DATE`: 2024-02-01T00:00:00 → 2024-02-07T00:00:00
  - `EF_DATE`: 2024-02-01T00:00:00 → 2024-02-07T00:00:00
  - `INV_Date`: 2024-02-07T00:00:00 → 2024-02-07T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `11:32`, `11:34`, `11:35`, `14:41`, `17:53`, `17:54`, `18:00`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `1`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 2.0 – 60.0
  - `AMOUNT`: 0.0 – 1662500.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `h® 1306-1.2.24` → **hđ 1306-1.2.24**
  - `REMARK`: `h® 1306-1.2.24` → **hđ 1306-1.2.24**
  - `REMARK`: `h® 1306-1.2.24` → **hđ 1306-1.2.24**

##### `STRANS_202403`

- Rows (metadata JSON): 201,831
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-03-31T00:00:00 → 2024-03-31T00:00:00
  - `EF_DATE`: 2024-03-31T00:00:00 → 2024-03-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `GOI`, `HOP`, `KG`, `KHA`
  - `BASE_UNIT`: `GOI`, `HOP`, `KG`, `KHA`
  - `TAX_CODE`: `NT`, `T1`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.126 – 17.406
  - `AMOUNT`: 0.0 – 500000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **

##### `STRANS_202404`

- Rows (metadata JSON): 212,900
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-04-01T00:00:00 → 2024-04-01T00:00:00
  - `EF_DATE`: 2024-03-31T00:00:00 → 2024-03-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `BAO`, `GOI`, `HOP`, `KG`, `KHA`
  - `BASE_UNIT`: `BAO`, `GOI`, `HOP`, `KG`, `KHA`
  - `TAX_CODE`: `NT`, `T1`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.128 – 96.0
  - `AMOUNT`: 0.0 – 1214102.4
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **

##### `STRANS_202405`

- Rows (metadata JSON): 230,243
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-05-01T00:00:00 → 2024-05-01T00:00:00
  - `EF_DATE`: 2024-04-30T00:00:00 → 2024-04-30T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CHA`, `GOI`, `HOP`, `HU`, `KHA`, `LOC`, `LON`
  - `BASE_UNIT`: `CHA`, `GOI`, `HOP`, `HU`, `KHA`, `LOC`, `LON`
  - `TAX_CODE`: `NT`, `T1`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 343.0
  - `AMOUNT`: 0.0 – 5145000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **

##### `STRANS_202406`

- Rows (metadata JSON): 229,887
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-06-01T00:00:00 → 2024-06-01T00:00:00
  - `EF_DATE`: 2024-05-31T00:00:00 → 2024-05-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `BO`, `CAI`, `HOP`
  - `BASE_UNIT`: `BO`, `CAI`, `HOP`
  - `TAX_CODE`: `NT`, `T1`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 16.0
  - `AMOUNT`: 0.0 – 944000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **

##### `STRANS_202407`

- Rows (metadata JSON): 242,006
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-07-01T00:00:00 → 2024-07-01T00:00:00
  - `EF_DATE`: 2024-06-30T00:00:00 → 2024-06-30T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `HU`, `KG`, `KHA`, `LO`
  - `BASE_UNIT`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `HU`, `KG`, `KHA`, `LO`
  - `TAX_CODE`: `NT`, `T1`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 61.0
  - `AMOUNT`: 0.0 – 2745000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **

##### `STRANS_202408`

- Rows (metadata JSON): 242,938
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-08-01T00:00:00 → 2024-08-01T00:00:00
  - `EF_DATE`: 2024-07-31T00:00:00 → 2024-07-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CAI`, `CAN`, `CAY`, `CHA`, `GOI`, `HOP`
  - `BASE_UNIT`: `CAI`, `CAN`, `CAY`, `CHA`, `GOI`, `HOP`
  - `TAX_CODE`: `NT`, `T1`, `T2`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 55.0
  - `AMOUNT`: 0.0 – 4252468.25
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy                                                                 ` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này                                                                 **

##### `STRANS_202409`

- Rows (metadata JSON): 253,162
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-09-30T00:00:00 → 2024-09-30T00:00:00
  - `EF_DATE`: 2024-09-30T00:00:00 → 2024-09-30T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `320`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90200`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CAI`, `CHA`, `DOI`, `GOI`, `HOP`, `HU`, `KG`
  - `BASE_UNIT`: `CAI`, `CHA`, `DOI`, `GOI`, `HOP`, `HU`, `KG`
  - `TAX_CODE`: `NT`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.502 – 72.0
  - `AMOUNT`: 0.0 – 1440000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m vÒ 0                                                                                        ` → **Cấn đối tự động hàng tồn ừm về 0                                                                                        **

##### `STRANS_202410`

- Rows (metadata JSON): 249,894
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-10-31T00:00:00 → 2024-10-31T00:00:00
  - `EF_DATE`: 2024-10-31T00:00:00 → 2024-10-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `340`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `00000`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `BAO`, `CAI`, `CHA`, `GOI`, `HOP`, `KHA`, `LON`
  - `BASE_UNIT`: `BAO`, `CAI`, `CHA`, `GOI`, `HOP`, `KHA`, `LON`
  - `TAX_CODE`: `NT`, `T1`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 0.0
  - `AMOUNT`: 747.36 – 82500.0

##### `STRANS_202411`

- Rows (metadata JSON): 227,921
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-11-30T00:00:00 → 2024-11-30T00:00:00
  - `EF_DATE`: 2024-11-30T00:00:00 → 2024-11-30T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `340`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `00000`, `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CAI`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`
  - `BASE_UNIT`: `CAI`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`
  - `TAX_CODE`: `NT`, `T1`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 0.0
  - `AMOUNT`: 134.98 – 9327.09

##### `STRANS_202412`

- Rows (metadata JSON): 245,595
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-12-31T00:00:00 → 2024-12-31T00:00:00
  - `EF_DATE`: 2024-12-31T00:00:00 → 2024-12-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `340`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `00000`, `90100`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `KG`, `LOC`
  - `BASE_UNIT`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `KG`, `LOC`
  - `TAX_CODE`: `NT`, `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 0.0
  - `AMOUNT`: 0.06 – 616197.44

##### `STRANS_202501`

- Rows (metadata JSON): 286,850
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-01-31T00:00:00 → 2025-01-31T00:00:00
  - `EF_DATE`: 2025-01-31T00:00:00 → 2025-01-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `340`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `90200`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `CHA`, `GOI`, `HOP`, `LOC`, `LON`
  - `BASE_UNIT`: `CHA`, `GOI`, `HOP`, `LOC`, `LON`
  - `TAX_CODE`: `T2`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 0.0
  - `AMOUNT`: 34.56 – 133362.72

##### `STRANS_202502`

- Rows (metadata JSON): 191,462
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-02-03T00:00:00 → 2025-02-03T00:00:00
  - `DUE_DATE`: 2025-02-03T00:00:00 → 2025-02-03T00:00:00
  - `EF_DATE`: 2025-02-03T00:00:00 → 2025-02-28T00:00:00
  - `INV_Date`: 2025-02-03T00:00:00 → 2025-02-03T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `10:30`, `14:52`, `14:58`, `16:30`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `4`
  - `RS_CODE`: `01`, `02`
  - `STK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 15.0
  - `AMOUNT`: 54000.0 – 2745000.0

##### `STRANS_202503`

- Rows (metadata JSON): 232,398
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-03-01T00:00:00 → 2025-03-31T00:00:00
  - `EF_DATE`: 2025-03-24T00:00:00 → 2025-04-21T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `316`, `318`, `320`
  - `TRAN_TIME`: `00:13`, `12:08`, `17:02`, `17:03`
  - `BU_ID`: `00000`
  - `RS_CODE`: `03`, `08`
  - `STK_TYPE`: `01`
  - `ASSO_ID`: `270000400087`, `270000405272`, `270000405304`
  - `UNIT_SYMB`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `TUY`
  - `BASE_UNIT`: `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `TUY`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.46 – 48.0
  - `AMOUNT`: 0.0 – 4495396.32
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này**
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này**
  - `REMARK`: `CÊn ®èi tù ®éng hµng tån ©m kú tr­íc chuyÓn sang kú nµy` → **Cấn đối tự động hàng tồn ừm kỳ trước chuyển sang kỳ này**

##### `STRANS_202504`

- Rows (metadata JSON): 229,637
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-04-01T00:00:00 → 2025-04-01T00:00:00
  - `DUE_DATE`: 2025-04-01T00:00:00 → 2025-04-01T00:00:00
  - `EF_DATE`: 2025-04-01T00:00:00 → 2025-04-01T00:00:00
  - `INV_Date`: 2025-04-01T00:00:00 → 2025-04-01T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `10:56`, `14:19`, `14:59`, `15:00`, `15:12`, `15:19`, `15:35`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `1`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 2.0 – 250.0
  - `AMOUNT`: 0.0 – 2257000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `KM P§P 01/4` → **KM PĐP 01/4**
  - `REMARK`: `KM P§P 01/4` → **KM PĐP 01/4**
  - `REMARK`: `h® 752-1.4.25` → **hđ 752-1.4.25**

##### `STRANS_202505`

- Rows (metadata JSON): 237,537
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-05-01T00:00:00 → 2025-05-02T00:00:00
  - `DUE_DATE`: 2025-05-01T00:00:00 → 2025-05-02T00:00:00
  - `EF_DATE`: 2025-04-30T00:00:00 → 2025-05-08T00:00:00
  - `INV_Date`: 2025-05-01T00:00:00 → 2025-05-02T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `10:18`, `10:19`, `10:38`, `11:25`, `11:46`, `15:33`, `15:36`, `15:40`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `03`, `05`, `100`, `101`, `99`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 165.0
  - `AMOUNT`: 0.0 – 1035360.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `L§L H§1310 02/5` → **LĐL HĐ1310 02/5**
  - `REMARK`: `L§L H§1310 02/5` → **LĐL HĐ1310 02/5**
  - `REMARK`: `L§L H§1310 02/5` → **LĐL HĐ1310 02/5**

##### `STRANS_202506`

- Rows (metadata JSON): 250,594
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-06-02T00:00:00 → 2025-06-03T00:00:00
  - `DUE_DATE`: 2025-06-02T00:00:00 → 2025-06-03T00:00:00
  - `EF_DATE`: 2025-06-02T00:00:00 → 2025-06-03T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:00`, `09:01`, `09:35`, `09:37`, `11:35`, `11:36`
  - `BU_ID`: `00000`
  - `RS_CODE`: `01`, `02`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50240`, `50426`, `50734`, `51215`, `51325`
  - `OSTK_TYPE`: `05`
  - `UNIT_SYMB`: `GOI`, `HOP`, `KG`, `KHA`
- Số liệu (min–max trong mẫu):
  - `QTY`: 2.0 – 20.0
  - `AMOUNT`: 54000.0 – 3870000.0

##### `STRANS_202507`

- Rows (metadata JSON): 269,294
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-07-01T00:00:00 → 2025-07-02T00:00:00
  - `DUE_DATE`: 2025-07-01T00:00:00 → 2025-07-02T00:00:00
  - `EF_DATE`: 2025-07-01T00:00:00 → 2025-08-19T00:00:00
  - `INV_Date`: 2025-07-01T00:00:00 → 2025-07-01T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:01`, `09:03`, `12:10`, `12:43`, `15:02`, `15:40`, `15:46`, `15:51`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `1`
  - `RS_CODE`: `01`, `02`, `03`
  - `STK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.5 – 24.0
  - `AMOUNT`: 0.0 – 5320000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `h® 429-1.7.25` → **hđ 429-1.7.25**

##### `STRANS_202508`

- Rows (metadata JSON): 286,567
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-08-31T00:00:00 → 2025-08-31T00:00:00
  - `EF_DATE`: 2025-08-31T00:00:00 → 2025-08-31T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `340`
  - `TRAN_TIME`: `00:00`
  - `BU_ID`: `00000`
  - `RS_CODE`: `08`
  - `STK_TYPE`: `01`
  - `UNIT_SYMB`: `BAO`, `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `HU`, `KG`, `TUY`
  - `BASE_UNIT`: `BAO`, `CAI`, `CAY`, `CHA`, `GOI`, `HOP`, `HU`, `KG`, `TUY`
  - `TAX_CODE`: `T1`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.0 – 0.0
  - `AMOUNT`: 64.6 – 53009.63

##### `STRANS_202509`

- Rows (metadata JSON): 281,502
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-09-02T00:00:00 → 2025-09-23T00:00:00
  - `EF_DATE`: 2025-09-02T00:00:00 → 2025-09-23T00:00:00
  - `INV_Date`: 2025-09-23T00:00:00 → 2025-09-23T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `09:12`, `09:13`, `09:48`, `18:12`, `18:13`, `18:15`, `19:13`, `20:41`
  - `BU_ID`: `90200`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `230000010596`, `230000024547`, `239020002289`
  - `OSTK_TYPE`: `03`
  - `UNIT_SYMB`: `CHA`, `GOI`, `HOP`, `HU`, `KG`, `LOC`
  - `BASE_UNIT`: `CHA`, `GOI`, `HOP`, `HU`, `KG`, `LOC`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.086 – 10.0
  - `AMOUNT`: 0.0 – 70928.2

##### `STRANS_202510`

- Rows (metadata JSON): 306,027
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-10-01T00:00:00 → 2025-10-31T00:00:00
  - `EF_DATE`: 2025-10-01T00:00:00 → 2025-10-31T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `09:04`, `09:56`, `12:06`, `14:42`, `15:06`, `15:11`, `16:54`, `16:57`
  - `BU_ID`: `00000`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `230000021677`, `230000025727`, `230000032305`
  - `OSTK_TYPE`: `03`
  - `UNIT_SYMB`: `GOI`, `HOP`, `KG`, `KHA`, `LOC`, `LON`
  - `BASE_UNIT`: `GOI`, `HOP`, `KG`, `KHA`, `LOC`, `LON`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.384 – 24.0
  - `AMOUNT`: 0.0 – 782743.92

##### `STRANS_202511`

- Rows (metadata JSON): 288,627
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-11-01T00:00:00 → 2025-11-01T00:00:00
  - `DUE_DATE`: 2025-11-01T00:00:00 → 2025-11-01T00:00:00
  - `EF_DATE`: 2025-11-01T00:00:00 → 2025-11-09T00:00:00
  - `INV_Date`: 2025-11-01T00:00:00 → 2025-11-01T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:14`, `10:15`, `10:29`, `10:38`, `11:03`
  - `BU_ID`: `00000`
  - `INV_CODE`: `1`
  - `INV_NO`: `06`
  - `RS_CODE`: `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50746`, `50747`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 44.0
  - `AMOUNT`: 0.0 – 1022222.24
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `L§L H§1822 01/11` → **LĐL HĐ1822 01/11**
  - `REMARK`: `L§L H§1822 01/11` → **LĐL HĐ1822 01/11**
  - `REMARK`: `L§L H§1822 01/11` → **LĐL HĐ1822 01/11**

##### `STRANS_202512`

- Rows (metadata JSON): 271,521
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-12-01T00:00:00 → 2025-12-11T00:00:00
  - `DUE_DATE`: 2025-12-01T00:00:00 → 2025-12-11T00:00:00
  - `EF_DATE`: 2025-12-01T00:00:00 → 2025-12-29T00:00:00
  - `INV_Date`: 2025-12-01T00:00:00 → 2025-12-11T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:39`, `10:34`, `12:12`, `15:07`, `15:09`, `15:11`
  - `BU_ID`: `00000`
  - `INV_CODE`: `1`
  - `INV_NO`: `1`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `00088`, `50426`, `50552`, `50747`, `51276`, `51438`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 80.0
  - `AMOUNT`: 0.0 – 2850000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `h® 5206-10.12.25` → **hđ 5206-10.12.25**
  - `REMARK`: `h® 5206-10.12.25` → **hđ 5206-10.12.25**
  - `REMARK`: `h® 5206-10.12.25` → **hđ 5206-10.12.25**

##### `STRANS_202601`

- Rows (metadata JSON): 265,063
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-01-02T00:00:00 → 2026-01-31T00:00:00
  - `DUE_DATE`: 2026-01-14T00:00:00 → 2026-01-31T00:00:00
  - `EF_DATE`: 2026-01-02T00:00:00 → 2026-02-06T00:00:00
  - `INV_Date`: 2026-01-30T00:00:00 → 2026-01-30T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`, `211`, `310`
  - `TRAN_TIME`: `08:05`, `08:15`, `08:30`, `09:22`, `11:55`, `11:56`, `20:48`
  - `BU_ID`: `00000`
  - `INV_CODE`: `1`
  - `INV_NO`: `2156`
  - `RS_CODE`: `03`
  - `STK_TYPE`: `01`, `02`
  - `OSTK_ID`: `10001`, `10004`, `10005`, `20002`, `40127`, `50435`, `50617`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 20.0
  - `AMOUNT`: 30001.51 – 487497.9
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `H§1057 27/1` → **HĐ1057 27/1**

##### `STRANS_202602`

- Rows (metadata JSON): 252,548
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-02-02T00:00:00 → 2026-02-02T00:00:00
  - `DUE_DATE`: 2026-02-02T00:00:00 → 2026-02-02T00:00:00
  - `EF_DATE`: 2026-02-02T00:00:00 → 2026-02-02T00:00:00
  - `INV_Date`: 2026-02-02T00:00:00 → 2026-02-02T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `08:54`, `10:23`, `10:28`, `10:50`, `15:41`, `16:20`
  - `BU_ID`: `00000`
  - `INV_CODE`: `1`
  - `INV_NO`: `01`, `1`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50426`, `50610`, `51167`, `51365`, `51468`, `51526`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 570.0
  - `AMOUNT`: 40500.0 – 2565000.0

##### `STRANS_202603`

- Rows (metadata JSON): 254,031
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-03-02T00:00:00 → 2026-03-05T00:00:00
  - `DUE_DATE`: 2026-03-02T00:00:00 → 2026-03-05T00:00:00
  - `EF_DATE`: 2026-03-02T00:00:00 → 2026-03-05T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `10:10`, `10:15`, `16:43`, `16:48`, `17:31`
  - `BU_ID`: `00000`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50426`, `51468`, `51511`, `51523`
  - `OSTK_TYPE`: `05`
  - `UNIT_SYMB`: `CAI`, `GOI`, `KG`, `KHA`
- Số liệu (min–max trong mẫu):
  - `QTY`: 2.0 – 30.0
  - `AMOUNT`: 54000.0 – 1800000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `h® 267-5.3.26` → **hđ 267-5.3.26**
  - `REMARK`: `h® 267-5.3.26` → **hđ 267-5.3.26**

##### `STRANS_202604`

- Rows (metadata JSON): 258,327
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-04-01T00:00:00 → 2026-04-10T00:00:00
  - `DUE_DATE`: 2026-04-01T00:00:00 → 2026-04-10T00:00:00
  - `EF_DATE`: 2026-04-01T00:00:00 → 2026-04-10T00:00:00
  - `INV_Date`: 2026-04-01T00:00:00 → 2026-04-10T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `11:55`, `12:02`, `16:16`, `17:48`
  - `BU_ID`: `00000`
  - `INV_CODE`: `1`
  - `INV_NO`: `03`, `1`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50565`, `51373`, `51547`, `51550`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 40.0
  - `AMOUNT`: 58500.0 – 1348050.0

#### loyalty

##### `CRDTRANS_ARC`

- Rows (metadata JSON): 1,586,383
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2025-11-04T00:00:00 → 2025-11-06T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `812`
  - `BU_ID`: `00000`
  - `TYPE`: `01`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -80000000.0 – -100000.0
  - `MARK`: -1600.0 – -2.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `chuyÓn ®iÓm qua thÎ E4205` → **chuyển điểm qua thẻ E4205**
  - `REMARK`: `tÆng 03 thÎ 100k=300®` → **tặng 03 thẻ 100k=300đ**
  - `REMARK`: `chuyÓn ®iÓm qua thÎ E4206` → **chuyển điểm qua thẻ E4206**

## RESTORED_DB2 (db2)

### Tổng hợp chéo bảng (từ mẫu)

**TRANS_CODE** (tần suất trong mẫu):

- `113`: 80 dòng mẫu
- `221`: 60 dòng mẫu
- `821`: 40 dòng mẫu
- `010`: 20 dòng mẫu
- `811`: 20 dòng mẫu
- ``: 20 dòng mẫu
- `334`: 20 dòng mẫu
- `211`: 20 dòng mẫu
- `222`: 16 dòng mẫu
- `008`: 4 dòng mẫu

**PMT_CODE**:

- `CASH`: 40

**CARD_ID prefix** (ký tự đầu):

- `A`: 57
- `@`: 40
- `E`: 23
- `a`: 5
- `F`: 5
- `H`: 5
- `e`: 2
- `N`: 2
- `L`: 1

**STK_ID** (cửa hàng/kho, top mẫu):

- `10001`: 259
- ``: 193
- `10005`: 18
- `20002`: 7
- `10004`: 3

**Shard month:** mẫu khớp suffix `_YYYYMM` (không phát hiện lệch).


**Bảng có text TCVN3 cần decode** (19):

- `ACCOUNT`
- `ASSOLST`
- `CRDTRANS`
- `CSCARD`
- `CTRANS`
- `CUSTOMER`
- `CustSumm`
- `DEBT`
- `INV_ISS`
- `PARTNER`
- `PMCRDISS`
- `PMCRDSTK`
- `PMTRANS`
- `SKU_DEF`
- `STRANS_TMP`
- `SUPPLIER`
- `TRANSHDR`
- `WebRpt_inventory_daily`
- `WebRpt_sales_sku_daily`

### Chi tiết theo nhóm

#### finance

##### `ACCOUNT`

- Rows (metadata JSON): 1,776
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `OPEN_DATE`: 2012-11-29T00:00:00 → 2012-11-29T00:00:00
  - `LAST_DATE`: 2012-11-29T00:00:00 → 2026-04-30T00:00:00
- Giá trị phân loại (mẫu):
  - `ACCOUNT_ID`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `CYS`: `VND`
  - `ACCO_TYPE`: `02`
  - `SUPP_ID`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `STATUS`: `True`
- Ví dụ TCVN3 → Unicode:
  - `NAME`: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t                          ` → **Cụng ty TNHH TM-XNK Việt Thỏi Phỏt                          **
  - `NAME`: `C«ng ty TNHH An Ti` → **Cụng ty TNHH An Ti**
  - `NAME`: `C«ng ty TNHH KD & CBTP Toµn Gia HiÖp Ph­íc` → **Cụng ty TNHH KD & CBTP Toàn Gia Hiệp Phước**

##### `DEBT`

- Rows (metadata JSON): 225,126
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `DEBT_DATE`: 2012-12-01T00:00:00 → 2012-12-01T00:00:00
  - `DUE_DATE`: 2012-12-27T00:00:00 → 2013-01-14T00:00:00
  - `LAST_DATE`: 2012-12-01T00:00:00 → 2012-12-01T00:00:00
- Giá trị phân loại (mẫu):
  - `DEBT_NO`: `000001131212000002`, `000001131212000003`, `000001131212000004`, `000001131212000005`, `000001131212000006`, `000001131212000007`, `000001131212000008`, `000001131212000009`, `000001131212000010`, `000001131212000011`
  - `ACCOUNT_ID`: `00043`, `00097`, `00248`, `00310`, `00469`, `00481`, `00656`, `50193`, `60166`
  - `CYS`: `VND`
  - `ACTION`: `C`
  - `STATUS`: `True`
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `NK theo H§0000133 ngµy 24/12/12                                                                                         ` → **NK theo HĐ0000133 ngày 24/12/12                                                                                         **
  - `REMARK`: `H§ nhËp 3011 ngµy 26/11/2012                                                                                            ` → **HĐ nhập 3011 ngày 26/11/2012                                                                                            **
  - `REMARK`: `H§ nhËp 3012 ngµy 26/11/2012                                                                                            ` → **HĐ nhập 3012 ngày 26/11/2012                                                                                            **

#### inventory_invoice

##### `INV_HDR`

- Rows (metadata JSON): 31,918
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `INV_DATE`: 2025-06-19T00:00:00 → 2026-03-31T00:00:00
  - `STR_DATE`: 2025-06-19T00:00:00 → 2026-03-31T00:00:00
- Giá trị phân loại (mẫu):
  - `INV_CODE`: `1`
  - `INV_NO`: `1`
  - `STR_NUM`: `000001132506000736`, `000001132507002222`, `000001132508002300`, `000001132508002379`, `000001132510000511`, `000001132510002327`, `000001132511000821`, `000001132512001105`, `000001132512001159`, `000001132512001717`
  - `CUSTAC`: `C`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 427600.0 – 22767977.67

##### `INV_ISS`

- Rows (metadata JSON): 55,198
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `INV_DATE`: 2022-06-16T00:00:00 → 2022-06-16T00:00:00
  - `FR_DATE`: 2022-06-16T00:00:00 → 2022-06-16T00:00:00
  - `TO_DATE`: 2022-06-16T00:00:00 → 2022-06-16T00:00:00
- Giá trị phân loại (mẫu):
  - `INV_REF`: `000002022061600000001`, `000002022061600000002`, `000002022061600000003`, `000002022061600000004`, `000002022061600000005`, `000002022061600000006`, `000002022061600000007`, `000002022061600000008`, `000002022061600000009`, `000002022061600000010`
  - `ISS_TYPE`: `1`
  - `CUST_TYPE`: `03`
  - `BU_ID`: `00000`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 32331.43 – 13804439.7
- Ví dụ TCVN3 → Unicode:
  - `CUST_NAME`: `NguyÔn ThÞ MËn E2733` → **Nguyễn Thị Mận E2733**
  - `CUST_NAME`: `NguyÔn TÊn MÉn` → **Nguyễn Tấn Mẫn**
  - `CUST_NAME`: `Bïi ThÞ Ph­¬ng Th¶o` → **Bựi Thị Phương Thảo**

##### `STK_DTL`

- Rows (metadata JSON): 111,613
- Mẫu lấy: 20 dòng
- Giá trị phân loại (mẫu):
  - `PRD_CODE`: `202211`

##### `ST_ORDER`

- Rows (metadata JSON): 2,202
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-01T00:00:00 → 2026-05-02T00:00:00
  - `EF_DATE`: 2026-05-01T00:00:00 → 2026-05-02T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `334`
  - `TRAN_TIME`: `10:10`, `13:13`, `20:14`
  - `BU_ID`: `00000`
  - `ACTION`: `8`
  - `STATUS`: `E`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `10004`
  - `OSTK_TYPE`: `01`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 20.0
  - `AMOUNT`: 6000.0 – 486111.2

#### loyalty

##### `CRD_INFO`

- Rows (metadata JSON): 52,072
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `LAST_DATE`: 2013-11-18T00:00:00 → 2026-05-07T00:00:00
  - `OPEN_DATE`: 2013-11-18T00:00:00 → 2026-05-07T00:00:00
- Giá trị phân loại (mẫu):
  - `NODE_ID`: `000`
  - `TYPE`: `01`

##### `CSCARD`

- Rows (metadata JSON): 45,208
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `ISS_DATE`: 2006-10-17T00:00:00 → 2025-04-04T00:00:00
  - `EF_DATE`: 2006-10-17T00:00:00 → 2025-04-04T00:00:00
  - `DUE_DATE`: 2026-12-31T00:00:00 → 2026-12-31T00:00:00
  - `LAST_DATE`: 2008-07-26T00:00:00 → 2021-06-27T00:00:00
- Giá trị phân loại (mẫu):
  - `BU_ID`: `00000`, `90200`
  - `PERSON_ID`: `023544444`, `A10000000003`, `A10000000004`, `A10000000012`, `A10000000021`, `A10000000038`, `A10000000044`, `A10000000106`, `A10000000156`, `A10000000168`
  - `SEX`: `F`, `M`
  - `PLC_ID`: `001101251`
  - `PHONE`: `012544444`, `0903203411`, `0905812671`, `0913484662`, `0914040050`, `0919503031`, `0983004441`, `0983887728`, `0989078976`, `210968`
  - `IMAGE`: `logo.bmp`
  - `POST`: `D`
  - `STATUS`: `False`, `True`
- Ví dụ TCVN3 → Unicode:
  - `NAME`: `Nguyen Hong S¬n` → **Nguyen Hong Sơn**
  - `REMARK`: `CÊp ph¸t tù ®éng` → **Cấp phỏt tự động**
  - `REMARK`: `CÊp ph¸t tù ®éng` → **Cấp phỏt tự động**

##### `PMCRDINF`

- Rows (metadata JSON): 426,254
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `STK_DATE`: 2012-12-26T00:00:00 → 2012-12-26T00:00:00
  - `DUE_DATE`: 2013-01-31T00:00:00 → 2013-01-31T00:00:00
- Giá trị phân loại (mẫu):
  - `TYPE`: `11`
  - `STK_NUM`: `000008211212000026`
  - `STATUS`: `True`

##### `PMCRDISS`

- Rows (metadata JSON): 31,477
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2017-10-13T00:00:00 → 2017-10-16T00:00:00
  - `DUE_DATE`: 2018-04-30T00:00:00 → 2018-04-30T00:00:00
  - `OPEN_DATE`: 2017-10-13T00:00:00 → 2017-10-16T00:00:00
  - `MODI_DATE`: 2017-10-13T00:00:00 → 2017-10-16T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `821`
  - `TRAN_TIME`: `09:10`, `09:11`, `09:12`, `09:14`, `09:15`, `09:16`, `09:17`, `09:18`, `09:19`, `09:20`
  - `BU_ID`: `00000`
  - `STATUS`: `True`
  - `FR_CARDID`: `@P0000245867`, `@P0000245871`, `@P0000245874`, `@P0000245875`, `@P0000245880`, `@P0000245884`, `@P0000245889`, `@P0000245892`, `@P0000245925`, `@P0000245927`
  - `TO_CARDID`: `@P0000245870`, `@P0000245873`, `@P0000245874`, `@P0000245879`, `@P0000245883`, `@P0000245888`, `@P0000245891`, `@P0000245924`, `@P0000245926`, `@P0000245928`
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `BV h¶i ch©u` → **BV hải chừu**
  - `REMARK`: `bv h¶i ch©u` → **bv hải chừu**
  - `REMARK`: `bv h¶i ch©u` → **bv hải chừu**

##### `PMCRDRCV`

- Rows (metadata JSON): 2,122
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-01T00:00:00 → 2026-06-13T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `BU_ID`: `00000`, `90100`, `90200`
  - `STATUS`: `N`, `R`
  - `TYPE`: `11`

##### `PMCRDSTK`

- Rows (metadata JSON): 31,554
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2012-12-26T00:00:00 → 2013-01-03T00:00:00
  - `DUE_DATE`: 2013-01-31T00:00:00 → 2013-07-10T00:00:00
  - `OPEN_DATE`: 2012-12-26T00:00:00 → 2013-01-03T00:00:00
  - `MODI_DATE`: 2012-12-26T00:00:00 → 2012-12-26T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `821`
  - `TRAN_TIME`: `09:42`
  - `BU_ID`: `00000`
  - `STATUS`: `True`
  - `PREFIX`: `@P`
  - `NODE_ID`: `000`
  - `FR_SERI`: `0000001`, `0000011`, `0000031`, `0000037`, `0000057`, `0000081`, `0000121`, `0000181`, `0000261`, `0000381`
  - `TO_SERI`: `0000010`, `0000030`, `0000036`, `0000056`, `0000080`, `0000120`, `0000180`, `0000260`, `0000380`, `0000680`
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `ThÎ XuÊt tÆng KH nh©n khai tr­¬ng` → **Thẻ Xuất tặng KH nhừn khai trương**
  - `REMARK`: `ThÎ XuÊt tÆng KH nh©n khai tr­¬ng` → **Thẻ Xuất tặng KH nhừn khai trương**
  - `REMARK`: `ThÎ XuÊt tÆng KH nh©n khai tr­¬ng` → **Thẻ Xuất tặng KH nhừn khai trương**

#### party_master

##### `CUSTHIST`

- Rows (metadata JSON): 230,438
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2017-11-30T00:00:00 → 2022-07-15T00:00:00
- Giá trị phân loại (mẫu):
  - `ID`: `00004`, `00006`
  - `TYPE`: `05`
  - `TRANS_CODE`: `113`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 48.0
  - `AMOUNT`: 24225.0 – 3762000.0

##### `CUSTOMER`

- Rows (metadata JSON): 46,793
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `OPEN_DATE`: 2012-12-30T00:00:00 → 2012-12-30T00:00:00
  - `MODI_DATE`: 2012-12-30T00:00:00 → 2012-12-30T00:00:00
  - `DUE_DATE`: 2021-12-31T00:00:00 → 2026-12-31T00:00:00
- Giá trị phân loại (mẫu):
  - `TYPE`: `03`
  - `BU_ID`: `00000`
  - `GRP_ID`: `3001`
  - `PHONE`: `0905348048`, `0913415205`, `0914111553`, `0983004441`, `0983723356`, `0983887728`, `3519475`, `3824242`, `NV siªu thÞ`
  - `MOBI`: `0905348048`, `0914111553`
  - `EMAIL`: `Lecamhoa-qnyahoo.com.vn`, `tnc.danang@gmail.com`
  - `PERSON_ID`: `E10000000003`, `E10000001281`
  - `SEX`: `F`, `M`
- Ví dụ TCVN3 → Unicode:
  - `CUST_NAME`: `NguyÔn Quèc B×nh` → **Nguyễn Quốc Bỡnh**
  - `CUST_NAME_U`: `Nguyễn Quốc Bình` → **Nguyễn Quốc Bỡnh**
  - `CUST_NAME`: `V­¬ng §×nh ChØnh` → **Vương Đỡnh Chỉnh**

##### `CustSumm`

- Rows (metadata JSON): 13,104
- Mẫu lấy: 20 dòng
- Giá trị phân loại (mẫu):
  - `Card_ID`: `H10000001824`, `H10000002134`, `H10000002162`, `H10000002212`, `H10000002231`, `H10000002308`, `H10000002352`, `H10000002432`, `h10000001785`, `h10000001845`
  - `Phone`: `0339615549`, `03784462453`, `0779420825`, `0903501303`, `0905145344`, `0905232710`, `0905293279`, `0905873338`, `0905999900`, `0906555412`
  - `Mobil`: `0905232710`
- Ví dụ TCVN3 → Unicode:
  - `Name`: `Lê Thị Xuân` → **Lờ Thị Xuừn**
  - `Address`: `14 Phan Đình Phùng` → **14 Phan Đỡnh Phựng**
  - `Name`: `Trần Thị Thanh Tâm` → **Trần Thị Thanh Từm**

##### `PARTNER`

- Rows (metadata JSON): 1,790
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `OPEN_DATE`: 2012-11-29T00:00:00 → 2012-11-29T00:00:00
- Giá trị phân loại (mẫu):
  - `ID`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `CODE`: `00036`
  - `TYPE`: `05`
  - `GRP_ID`: `5001`
  - `TAX_ID`: `03011966090-1`, `0303124558`, `0303256057`, `0303898713`, `0400228337`, `0400388131`, `0400393549`, `3600536736`
  - `CON_PERSON`: `An Ti`, `CTy V¹n H­¬ng`, `Cty Ch©u ¢u VN`, `Cty Duy Thanh`, `Cty H­¬ng B×nh`, `Cty Nguyªn Vò`, `Cty Ph­íc Th¸i`, `Cty Toµn Quèc`, `Cty d­îc phÈm AAA`, `Cty d­îc §µ N½ng`
  - `PHONE`: `0511722310`, `087551372-7551796`, `891643`
  - `FAX`: `0510722266`, `087551837`, `833208`
- Ví dụ TCVN3 → Unicode:
  - `NAME`: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t` → **Cụng ty TNHH TM-XNK Việt Thỏi Phỏt**
  - `ADDRESS`: `27A B×nh Phó, P10, Q6, TP HCM` → **27A Bỡnh Phỳ, P10, Q6, TP HCM**
  - `NAME_U`: `Công ty TNHH TM-XNK Việt Thái Phát` → **Cụng ty TNHH TM-XNK Việt Thỏi Phỏt**

##### `SUPPLIER`

- Rows (metadata JSON): 1,758
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `OPEN_DATE`: 2012-11-29T00:00:00 → 2012-11-29T00:00:00
  - `MODI_DATE`: 2012-11-29T00:00:00 → 2020-04-28T00:00:00
  - `LAST_DATE`: 2021-03-11T00:00:00 → 2026-06-17T00:00:00
- Giá trị phân loại (mẫu):
  - `SUPP_ID`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `SUPP_CODE`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `TYPE`: `05`
  - `GRP_ID`: `5001`
  - `ACCOUNT_ID`: `00004`, `00006`, `00010`, `00011`, `00016`, `00017`, `00023`, `00026`, `00027`, `00031`
  - `ACC_CYS`: `VND`
  - `CON_PERSON`: `An Ti`, `CTy V¹n H­¬ng`, `Cty Ch©u ¢u VN`, `Cty Duy Thanh`, `Cty H­¬ng B×nh`, `Cty Nguyªn Vò`, `Cty Ph­íc Th¸i`, `Cty Toµn Quèc`, `Cty d­îc phÈm AAA`, `Cty d­îc §µ N½ng`
  - `TAX_ID`: `03011966090-1`, `0303124558`, `0303256057`, `0303898713`, `0400228337`, `0400388131`, `0400393549`, `3600536736`
- Ví dụ TCVN3 → Unicode:
  - `SUPP_NAME`: `C«ng ty TNHH TM-XNK ViÖt Th¸i Ph¸t` → **Cụng ty TNHH TM-XNK Việt Thỏi Phỏt**
  - `ADDRESS`: `27A B×nh Phó, P10, Q6, TP HCM` → **27A Bỡnh Phỳ, P10, Q6, TP HCM**
  - `SUPP_NAME_U`: `Công ty TNHH TM-XNK Việt Thái Phát` → **Cụng ty TNHH TM-XNK Việt Thỏi Phỏt**

#### pricing_promo

##### `HISRTPR`

- Rows (metadata JSON): 21,745
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `DATE`: 2022-03-09T08:45:14 → 2022-03-11T11:16:56
- Giá trị phân loại (mẫu):
  - `TIME`: `07:46`, `08:45`, `08:52`, `09:36`, `09:37`, `09:38`, `10:01`, `10:16`, `11:16`, `15:08`
  - `ZONE_CODE`: `000`
  - `UNIT_SYMB`: `BAO`, `CAI`, `HOP`, `KG`, `KHA`
  - `BASE_UNIT`: `BAO`, `CAI`, `HOP`, `KG`, `KHA`

##### `HISSPPR`

- Rows (metadata JSON): 92,173
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `DATE`: 2022-03-16T11:15:12 → 2022-03-16T15:22:17
- Giá trị phân loại (mẫu):
  - `TIME`: `11:15`, `11:21`, `14:40`, `14:42`, `14:43`, `14:44`, `14:56`, `14:59`, `15:01`, `15:02`
  - `SUPP_ID`: `00017`, `00114`, `50014`, `50298`, `50753`, `50794`
  - `UNIT_SYMB`: `CHA`, `DOI`, `GOI`, `HOP`
  - `BASE_UNIT`: `CAI`, `CHA`, `GOI`, `HOP`
  - `TAX_CODE`: `N0`, `T2`, `T5`

##### `RDISCINF`

- Rows (metadata JSON): 18,854
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `FR_DATE`: 2017-10-18T00:00:00 → 2017-10-18T00:00:00
  - `TO_DATE`: 2017-10-19T00:00:00 → 2017-10-19T00:00:00
- Giá trị phân loại (mẫu):
  - `DISC_CODE`: `000117101801`, `000117101802`, `000117101803`, `000117101804`
  - `CUST_TYPE`: `03`
  - `ZONE_CODE`: `000`
  - `OBJ_CODE`: `05`
  - `OBJ_VALUE`: `290312553600`, `290312600400`, `290312718000`, `290320023000`, `290320023100`, `290320023500`, `290320040800`, `290320040900`, `290320041100`, `290320041900`
  - `DATA_TYPE`: `C`
  - `CHG_TYPE`: `02`
  - `STATUS`: `False`, `True`

#### product

##### `ASSOLST`

- Rows (metadata JSON): 7,150
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `ISS_DATE`: 2020-02-28T00:00:00 → 2022-06-23T00:00:00
- Giá trị phân loại (mẫu):
  - `ASSO_ID`: `270000400007`, `270000400008`, `270000400009`, `270000400010`, `270000400011`, `270000400012`, `270000400013`, `270000400014`, `270000400015`, `270000400016`
  - `ASSO_TYPE`: `04`
  - `STATUS`: `True`
- Ví dụ TCVN3 → Unicode:
  - `DESCRIPT`: `Quýt rÉy 13k` → **Quýt rẫy 13k**
  - `DESCRIPT`: `Sul¬ xanh 15k` → **Sulơ xanh 15k**
  - `DESCRIPT`: `B¸nh m× hoa cóc-gg` → **Bỏnh mỡ hoa cỳc-gg**

##### `ASSO_INF`

- Rows (metadata JSON): 14,300
- Mẫu lấy: 20 dòng
- Giá trị phân loại (mẫu):
  - `ASSO_ID`: `270000400007`, `270000400008`, `270000400009`, `270000400010`, `270000400011`, `270000400012`, `270000400013`, `270000400014`, `270000400015`, `270000400016`
  - `ASSO_TYPE`: `04`
  - `PLU_CODE`: `0078`, `0510`, `3044`
  - `ITEM_TYPE`: `01`
  - `MERC_TYPE`: `01`, `02`
  - `UNIT_SYMB`: `BAO`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `LOC`
  - `BASE_UNIT`: `BAO`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `LOC`
  - `TAX_CODE`: `NT`, `T5`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.2 – 6.0

##### `BARCODE`

- Rows (metadata JSON): 44,004
- Mẫu lấy: 20 dòng
- Giá trị phân loại (mẫu):
  - `TYPE`: `01`
  - `UNIT_SYMB`: `CHA`, `GOI`, `HOP`, `HU`

##### `PLU`

- Rows (metadata JSON): 3,886
- Mẫu lấy: 20 dòng
- Giá trị phân loại (mẫu):
  - `PLU_CODE`: `0001`, `0002`, `0003`, `0004`, `0005`, `0006`, `0007`, `0008`, `0009`, `0010`
  - `MERC_TYPE`: `02`
  - `STATUS`: `True`

##### `SKU_DEF`

- Rows (metadata JSON): 116,112
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `OPEN_DATE`: 2022-03-09T00:00:00 → 2022-03-11T00:00:00
  - `MODI_DATE`: 2022-03-11T00:00:00 → 2026-03-25T15:21:03
- Giá trị phân loại (mẫu):
  - `SKU_CODE`: `00000001`, `00000002`, `00000003`, `00000004`, `00000005`, `00000007`, `00000008`, `00000009`, `00000010`, `00000011`
  - `PLU_CODE`: `3156`
  - `DEPT_ID`: `0101`, `0301`
  - `GRP_ID`: `030000`, `030100`, `030301`, `080001`
  - `GOODS_ID`: `00000001`, `00000002`, `00000003`, `00000004`, `00000005`, `00000006`, `00000007`, `00000008`, `00000009`, `00000010`
  - `VAR_TYPE`: `0`
  - `VAR_ID`: `00`
  - `PICEUNIT`: `BAO`, `CAI`, `HOP`, `KG`, `KHA`
- Ví dụ TCVN3 → Unicode:
  - `GRP_NAME`: `C¸c s¶n phÈm s¬ chÕ                  ` → **Cỏc sản phẩm sơ chế                  **
  - `SHORT_NAME`: `T«m rim gg 23k` → **Tụm rim gg 23k**
  - `FULL_NAME`: `T«m rim gg 23k` → **Tụm rim gg 23k**

##### `sku_activity`

- Rows (metadata JSON): 54,060
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `first_sale_date`: 2024-01-01 → 2025-06-17
  - `last_sale_date`: 2024-01-24 → 2026-03-31
  - `first_receipt_date`: 2024-01-20 → 2025-08-07
  - `last_receipt_date`: 2024-08-08 → 2026-03-30
- Giá trị phân loại (mẫu):
  - `stk_id`: `10001`
  - `sku_id`: `290000000100`, `290000000300`, `290000000700`, `290000000900`, `290000009100`, `290000009300`, `290000009600`, `290000011100`, `290000011300`, `290000011400`

#### reporting

##### `WebRpt_inventory_daily`

- Rows (metadata JSON): 2,203,446
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `report_date`: 2026-04-02 → 2026-04-02
- Giá trị phân loại (mẫu):
  - `stk_id`: `10001`
  - `sku_id`: `290000000100`, `290000000200`, `290000000400`, `290000000600`, `290000000700`, `290000000800`, `290000007300`, `290000007800`, `290000008200`, `290000008600`
  - `grp_id`: `010000`, `010100`, `020000`, `030000`, `030100`, `060102`
  - `skucode`: `00000001`, `00000002`, `00000004`, `00000007`, `00000008`, `00000073`, `00000078`, `00000082`, `00000086`, `00000091`
  - `stock_status`: `INFO - Never Sold`, `WARN - Discontinued`
- Số liệu (min–max trong mẫu):
  - `qty_onhand`: 0.0 – 226.0
- Ví dụ TCVN3 → Unicode:
  - `stkname`: `Siêu thị Phan Đình Phùng` → **Siờu thị Phan Đỡnh Phựng**
  - `grpname`: `Các sản phẩm sơ chế` → **Cỏc sản phẩm sơ chế**
  - `skuname`: `Tôm rim gg 23k` → **Tụm rim gg 23k**

##### `WebRpt_rfm_snapshot`

- Rows (metadata JSON): 12,309
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `snapshot_date`: 2026-04-01 → 2026-04-01
- Giá trị phân loại (mẫu):
  - `card_id`: `A10000003872`, `A10000004618`, `A10000005616`, `A10000005661`, `A10000006303`, `A10000006307`, `A10000006455`, `A10000006489`, `A10000006490`, `A10000006499`
  - `cust_id`: `230000000935`, `230000006449`, `230000012826`, `230000012877`, `230000029984`, `230000033128`, `239010001245`, `239010004234`, `239010005025`, `239010005165`
  - `card_type`: `01`
  - `rfm_segment`: `At Risk`, `Loyal`, `Others`

##### `WebRpt_sales_sku_daily`

- Rows (metadata JSON): 6,372
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `report_date`: 2026-04-01 → 2026-04-01
- Giá trị phân loại (mẫu):
  - `stk_id`: `10001`
  - `sku_id`: `290000000300`, `290000011100`, `290000012300`, `290000012700`, `290000054800`, `290000059600`, `290000060800`, `290000061300`, `290000062400`, `290000062700`
  - `grp_id`: `010000`, `030000`, `030100`, `030301`, `030302`, `030310`, `060102`
  - `skucode`: `00000003`, `00000111`, `00000123`, `00000127`, `00000548`, `00000596`, `00000608`, `00000613`, `00000624`, `00000627`
- Số liệu (min–max trong mẫu):
  - `qty`: 0.498 – 7.0
  - `revenue`: 5740.74 – 605150.0
  - `gross_profit`: 1566.8 – 605150.0
- Ví dụ TCVN3 → Unicode:
  - `stkname`: `Siêu thị Phan Đình Phùng` → **Siờu thị Phan Đỡnh Phựng**
  - `grpname`: `Ngũ cốc các loại` → **Ngũ cốc cỏc loại**
  - `skuname`: `Bún gạo lứt huyết rồng 500g` → **Bỳn gạo lứt huyết rồng 500g**

#### staging

##### `CRDTRANS_TMP`

- Rows (metadata JSON): 197,387
- Mẫu lấy: 20 dòng
- Tỷ lệ AMOUNT/MARK phổ biến (điểm): [(54420, 1), (56025, 1), (50514, 1)]
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-01-01T00:00:00 → 2024-01-01T00:00:00
- Giá trị phân loại (mẫu):
  - `TRAN_TIME`: `14:32`, `15:07`, `15:09`, `15:21`, `15:42`, `15:51`, `15:54`, `15:57`, `16:03`, `16:05`
  - `TRANS_CODE`: `221`
  - `BU_ID`: `00000`
  - `TYPE`: `01`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 59946.0 – 1190600.0
  - `MARK`: 1.0 – 23.0

##### `STRANS_TMP`

- Rows (metadata JSON): 184,907
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2024-05-03T00:00:00 → 2024-05-08T00:00:00
  - `DUE_DATE`: 2024-05-03T00:00:00 → 2024-05-08T00:00:00
  - `EF_DATE`: 2024-05-03T00:00:00 → 2024-05-08T00:00:00
  - `INV_Date`: 2024-05-04T00:00:00 → 2024-05-08T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `211`
  - `TRAN_TIME`: `08:50`, `11:26`, `11:30`, `11:32`, `11:34`, `17:35`
  - `BU_ID`: `00000`
  - `INV_TYPE`: `1`
  - `INV_CODE`: `1`
  - `INV_NO`: `02`, `03`, `04`, `05`, `06`
  - `INV_DEPT`: `K`
  - `STK_TYPE`: `01`, `02`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 48.0
  - `AMOUNT`: 45370.3 – 13278652.74
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `xuÊt TP 3.5.24` → **xuất TP 3.5.24**
  - `REMARK`: `xuÊt TP 3.5.24` → **xuất TP 3.5.24**
  - `REMARK`: `xuÊt TP 3.5.24` → **xuất TP 3.5.24**

##### `SUSPEND`

- Rows (metadata JSON): 906,372
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2020-07-30T00:00:00 → 2020-07-30T00:00:00
  - `EF_DATE`: 2020-07-30T00:00:00 → 2020-07-30T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `221`
  - `TRAN_TIME`: `11:08`, `11:28`
  - `BU_ID`: `00000`
  - `UNIT_SYMB`: `BAO`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `LOC`
  - `BASE_UNIT`: `BAO`, `CHA`, `GOI`, `HOP`, `KG`, `KHA`, `LOC`
  - `FOREX_CYS`: `VND`
  - `STATUS`: `False`
- Số liệu (min–max trong mẫu):
  - `QTY`: 0.4 – 5.0
  - `AMOUNT`: 7700.0 – 285900.0

#### transactions_live

##### `CASH_ST`

- Rows (metadata JSON): 15,142
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2023-10-23T00:00:00 → 2025-07-31T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `010`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `QTY`: 1.0 – 7.0

##### `CRDTRANS`

- Rows (metadata JSON): 38,091
- Mẫu lấy: 20 dòng
- Tỷ lệ AMOUNT/MARK phổ biến (điểm): [(50000, 20)]
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-01T00:00:00 → 2026-05-16T00:00:00
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `811`
  - `BU_ID`: `00000`
  - `TYPE`: `01`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 100000.0 – 10000000.0
  - `MARK`: 2.0 – 200.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `kh¸ch quªn ®äc m· thÎ bILL BE221...182` → **khỏch quờn đọc mỳ thẻ bILL BE221...182**
  - `REMARK`: `kh¸ch quªn ®äc m· thÎ bill be221...434` → **khỏch quờn đọc mỳ thẻ bill be221...434**
  - `REMARK`: `quªn nhËp m· thÎ cña kh¸ch bill be221...485` → **quờn nhập mỳ thẻ của khỏch bill be221...485**

##### `CTRANS`

- Rows (metadata JSON): 51,314
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2012-12-01T00:00:00 → 2012-12-09T00:00:00
  - `EF_DATE`: 2012-12-06T00:00:00 → 2013-01-12T00:00:00
  - `DEBT_DATE`: 2012-12-01T00:00:00 → 2012-12-09T00:00:00
  - `DUE_DATE`: 2012-12-01T00:00:00 → 2012-12-27T00:00:00
- Giá trị phân loại (mẫu):
  - `BU_ID`: `00000`
  - `DEBT_NO`: `000001131212000004`, `000001131212000008`, `000001131212000015`, `000001131212000017`, `000001131212000019`, `000001131212000030`, `000001131212000048`, `000001131212000049`, `000001131212000053`, `000001131212000056`
  - `TRANS_CODE`: `113`
  - `TRANS_TYPE`: `01`
  - `ACCOUNT_ID`: `00010`, `00026`, `00043`, `00222`, `00248`, `00310`, `00313`, `00559`, `00596`, `00635`
  - `CYS`: `VND`
  - `ACTION`: `C`
  - `DEP_CODE`: `K`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 717536.0 – 81573744.7
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `NK theo H§0000133 ngµy 24/12/12                             ` → **NK theo HĐ0000133 ngày 24/12/12                             **
  - `REMARK`: `H§ nhËp 3011 ngµy 26/11/2012                                ` → **HĐ nhập 3011 ngày 26/11/2012                                **
  - `REMARK`: `NhËp hµng theo H§ 575-28/11/2012                            ` → **Nhập hàng theo HĐ 575-28/11/2012                            **

##### `PMTRANS`

- Rows (metadata JSON): 123,716
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-04T00:00:00 → 2026-06-16T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `008`, `222`
  - `TRAN_TIME`: `09:54`, `09:57`, `09:58`, `10:07`, `10:08`, `10:09`, `10:10`, `10:12`, `10:17`, `10:21`
  - `BU_ID`: `00000`
  - `PMT_CODE`: `CASH`
  - `CYS`: `VND`
  - `STATUS`: `True`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: -1253755.0 – -18000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**
  - `REMARK`: `C©n ®èi ®iÒu chØnh quü thu ng©n vÒ 0` → **Cừn đối điều chỉnh quỹ thu ngừn về 0**

##### `STRANS`

- Rows (metadata JSON): 420,002
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-02T00:00:00 → 2026-05-04T00:00:00
  - `DUE_DATE`: 2026-05-02T00:00:00 → 2026-05-04T00:00:00
  - `EF_DATE`: 2026-05-02T00:00:00 → 2026-05-21T00:00:00
  - `UPDATED`: True → True
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:59`, `11:36`, `11:46`, `14:49`, `14:51`
  - `BU_ID`: `00000`
  - `RS_CODE`: `01`, `03`
  - `STK_TYPE`: `01`
  - `OSTK_ID`: `50747`, `51167`, `51438`
  - `OSTK_TYPE`: `05`
  - `UNIT_SYMB`: `GOI`, `HOP`
- Số liệu (min–max trong mẫu):
  - `QTY`: 2.0 – 25.0
  - `AMOUNT`: 0.0 – 725000.0

##### `TRANSHDR`

- Rows (metadata JSON): 86,733
- Mẫu lấy: 20 dòng
- Khoảng ngày (mẫu):
  - `TRAN_DATE`: 2026-05-02T00:00:00 → 2026-05-05T00:00:00
  - `DUE_DATE`: 2026-05-02T00:00:00 → 2026-05-05T00:00:00
  - `EF_DATE`: 2026-05-02T00:00:00 → 2026-05-21T00:00:00
  - `UPDATED`: False → False
- Giá trị phân loại (mẫu):
  - `TRANS_CODE`: `113`
  - `TRAN_TIME`: `09:59`, `11:31`, `11:36`, `11:46`, `11:49`, `11:50`, `11:52`, `11:53`, `11:54`, `11:57`
  - `BU_ID`: `00000`
  - `SUPP_ID`: `50426`, `50747`, `51167`, `51438`, `51508`, `51547`
  - `IMP_ID`: `10001`, `10004`, `10005`
  - `IMP_TYPE`: `01`
  - `EXP_ID`: `50426`, `50747`, `51167`, `51438`, `51508`, `51547`
  - `EXP_TYPE`: `05`
- Số liệu (min–max trong mẫu):
  - `AMOUNT`: 0.0 – 2206000.0
- Ví dụ TCVN3 → Unicode:
  - `REMARK`: `KM L§L 05/5` → **KM LĐL 05/5**
  - `REMARK`: `H§201 05/5` → **HĐ201 05/5**
  - `REMARK`: `KM L§L 05/5` → **KM LĐL 05/5**

## Đúc kết kiến trúc

### db1 — archive giao dịch (shard)

| Logical | Physical | Ghi chú |
|---------|----------|---------|
| STRANS | `STRANS_YYYYMM` (29 bảng) | Chi tiết dòng bán, 114 cột |
| PMTRANS | `PMTRANS_YYYYMM` (28 bảng) | Thanh toán, 27 cột |
| CRDTRANS | `CRDTRANS_ARC` | Giao dịch thẻ/điểm |
| TRANSHDR | `TRANSHDR_ARC` | Header bill |

Chọn shard theo `TRAN_DATE` → `STRANS_202503` cho tháng 03/2025.

### db2 — vận hành + master + báo cáo

- **Live transactions:** `TRANSHDR`, `STRANS`, `PMTRANS`, `CRDTRANS` (không shard; window gần đây)
- **Staging:** `SUSPEND`, `*_TMP` — bill treo / chưa post
- **Master:** `CUSTOMER`, `CSCARD`, `SKU_DEF`, `SUPPLIER`, …
- **Pre-aggregated:** `WebRpt_*` — ưu tiên cho agent analytics

## Mã nghiệp vụ quan sát được (cần xác nhận)

| Mã | Bảng thường gặp | Dự đoán |
|----|-----------------|---------|
| `221` | PMTRANS | Thanh toán bán lẻ |
| `008` | PMTRANS | Thu/chi quỹ (số tiền lớn) |
| `113` | STRANS, TRANSHDR | Bán lẻ — chi tiết/header |
| `811`/`812` | CRDTRANS | Tích/điều chỉnh điểm thẻ |
| `222`, `320`, `010`, `340` | PMTRANS/STRANS | Loại chứng từ khác |

**PMT_CODE:** `CASH`, `CARD`, `BANK`, `OWNCP` (thường có trailing space).

**Điểm thưởng:** `AMOUNT / MARK ≈ 50,000` trên mẫu CRDTRANS (khớp rule điểm/50k trong domain_definitions stub).

**Thẻ:** prefix `A`, `E`, `F`, `H` — có thể map tier/loại thẻ (cần bạn xác nhận).

## Khuyến nghị cho data_dictionary / agent

1. Logical table + shard resolver cho db1 (`data_dictionary/db1/shards.yaml`).
2. Mô tả cột ưu tiên bảng `WebRpt_*` và master (`SKU_DEF`, `CSCARD`) trước raw STRANS.
3. `domain_definitions.md`: map `TRANS_CODE`, `PMT_CODE`, prefix `CARD_ID`.
4. Pipeline decode TCVN3 trên mọi string từ SQL trước khi đưa LLM/sandbox.
5. Agent II query `WebRpt_*` khi câu hỏi aggregate; chỉ đục STRANS/PMTRANS shard khi cần chi tiết.

---
*Generated by `scripts/explore_db_deep.py` — 2026-06-29 11:54*

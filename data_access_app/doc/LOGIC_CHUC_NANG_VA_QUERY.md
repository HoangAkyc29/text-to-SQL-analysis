# Data Access App — Báo cáo logic chức năng & query

Tài liệu mô tả **cách code hiện tại chạy** (không phải wishlist). Mục đích: review logic đúng/sai.

Nguồn chính:

- `app/db/cutoff.py`, `app/db/dual_query.py`, `app/db/connection.py`
- `app/domain/*.py`, `app/domain/search_opts.py`, `app/domain/columns.py`
- `app/export/*`, `app/ui/pages/*`

---

## 1. Kiến trúc tổng quan

App Flet **độc lập** (không import `project_core`). Kết nối ODBC native tới SQL Server:

| Target | DB | Vai trò |
|--------|-----|---------|
| **db2** | `RESTORED_DB2` | Master (`SKU_DEF`, `CSCARD`) + fact **live** bare (`STRANS`, `TRANSHDR`) |
| **db1** | `RESTORED_DB` | Fact **lịch sử** shard (`STRANS_YYYYMM`, `TRANSHDR_ARC`) |

- DSN từ `.env` / monorepo `.env`; `Server=` luôn rewrite → `DESKTOP-AUQEDC5` (hoặc `DATA_ACCESS_SQL_SERVER`).
- Mọi `SELECT` readonly; LLM không viết SQL — SQL nằm trong handlers domain.
- Text: decode TCVN3 trên một số cột (`NAME`, `FULL_NAME`, …) sau khi đọc (`decode_dataframe`).
- Export: slim column allowlist (`app/domain/columns.py`); không `SELECT *`.

---

## 2. Dual-DB / cutoff (mọi báo cáo theo ngày)

### 2.1 Cutoff

`rolling_cutoff()` = **ngày 1 của tháng trước** (theo “hôm nay”).

Ví dụ hôm nay 2026-07-30 → cutoff = `2026-06-01`.

- `date_end >= cutoff` → cần **db2** (bare `STRANS` / `TRANSHDR`)
- `date_start < cutoff` → cần **db1** (shards)

### 2.2 Shard db1

- `STRANS`: `STRANS_YYYYMM` từ `max(202312, ym(date_start))` → `min(archive_newest_ym, ym(db1_end))`
- `TRANSHDR` lịch sử: **một** bảng `TRANSHDR_ARC` (không shard theo tháng trong code hiện tại)
- `archive_newest_ym` = tháng trước cutoff (tháng “archive mới nhất”)

### 2.3 Date filter trên mọi fact query

Luôn append:

```sql
AND TRAN_DATE >= ? AND TRAN_DATE < ?
```

Params: khoảng con của nhánh (db1 hoặc db2), không phải luôn nguyên `date_start`/`date_end` toàn bộ.

### 2.4 Merge

`run_selects`: chạy lần lượt từng `(target, sql, params)`, `concat` pandas. Bảng shard thiếu → bỏ qua (invalid object name), không fail cả job.

**Không có `TOP` trên fact queries F3/F4/F5** — chỉ master search (SKU/CSCARD) có TOP.

---

## 3. Giá trị dòng / đơn

Hằng số dùng chung (`columns.py`):

```text
line_value / bill_value SQL =
  ISNULL(AMOUNT,0) + ISNULL(SURPLUS,0) + ISNULL(VAT_AMT,0)
```

- **Không** mặc định lọc `TRANS_CODE = 113`.
- Khóa đơn: `(STK_ID, TRANS_NUM)`.
- Điểm F3: `points = floor(total_value / 50000)` (làm tròn xuống).

---

## 4. Search options (CÁCH TÌM)

`SearchOpts` (`search_opts.py`), UI mặc định **bật cả hai**:

| Option | ON (default) | OFF |
|--------|--------------|-----|
| Không phân biệt hoa/thường | `LOWER(LTRIM(RTRIM(CAST(col AS NVARCHAR(4000)))))` + value `.lower()` | Giữ nguyên case |
| Tìm gần đúng | Text thường: `LIKE '%v%'`; **Tiền tố thẻ**: `LIKE 'v%'` (starts-with) | `=` exact |

### TOP master search

- Env / default: `DATA_ACCESS_SEARCH_LIMIT` = **500000**
- Áp dụng: `search_products`, `search_by_group`, `search_customers`, resolve token F4/F5
- Trả `df.attrs["truncated"]` / `["limit"]`; UI cảnh báo nếu cắt
- Resolve SP cho F4/F5: nếu truncated → **`raise ValueError`** (không bỏ SKU im lặng)

**Không áp dụng SearchOpts:** danh sách thẻ paste (`CARD_ID IN (...)`), STK chip (`STK_ID IN (...)`), `lookup_cards` exact IN.

---

## 5. F1 — Tìm mặt hàng

**File:** `domain/product.py` → `search_products`  
**DB:** db2 `SKU_DEF` only

```sql
SELECT TOP ({limit}) <PRODUCT_COLUMNS>
FROM SKU_DEF
WHERE (<code predicates>) AND (<name predicates>)
ORDER BY SKU_CODE
```

- **Mã** (nếu có): OR trên `SKU_CODE`, `SKU_ID`, `BARCODE` với `match_any` + opts
- **Tên** (nếu có): `FULL_NAME_U` với `match_column` + opts
- Cần ít nhất một trong hai; AND nếu cả hai có

Export: slim `PRODUCT_COLUMNS`.

---

## 6. F6 — Mặt hàng theo nhóm

**File:** `search_by_group`  
**DB:** db2 `SKU_DEF`

```sql
SELECT TOP ({limit}) <PRODUCT_COLUMNS>
FROM SKU_DEF
WHERE (<GRP_ID>) AND/OR (<GRP_NAME>)
ORDER BY GRP_ID, SKU_CODE
```

Cùng SearchOpts như F1.

---

## 7. F2 — Tìm khách

**File:** `domain/customer.py` → `search_customers`  
**DB:** db2 `CSCARD`

```sql
SELECT TOP ({limit})
  CARD_ID, NAME_U, NAME, PHONE, SEX, BIRTHDAY, CUST_ID
FROM CSCARD
WHERE <clauses AND>
ORDER BY CARD_ID
```

| Field UI | Predicate |
|----------|-----------|
| Mã thẻ | `match_column(CARD_ID)` → fuzzy `%…%` hoặc `=` |
| Tiền tố thẻ | `match_prefix_column(CARD_ID)` → fuzzy `prefix%` hoặc `=` |
| Tên | OR `NAME_U`, `NAME` (chỉ trong WHERE) |
| SĐT | OR `PHONE`, `MOBI` (MOBI chỉ trong WHERE, không export) |
| Tháng sinh | `MONTH(BIRTHDAY) = ?` (1–12) |
| Độ tuổi | tuổi từ `BIRTHDAY` (tính đến hôm nay) `>=` / `<=` |

Cần ≥1 điều kiện (gồm tháng sinh / tuổi).

**Cột export / preview (`CUSTOMER_COLUMNS`):** `CARD_ID`, `NAME`, `PHONE`, `SEX`, `BIRTHDAY`, `CUST_ID` — **không** `NAME_U`, `MOBI`, `DISC_LVL`, `ISS_DATE`, `DUE_DATE`.

Sau đọc: ưu tiên `NAME_U` → ghi vào `NAME`; nếu `NAME_U` trống thì decode TCVN3 trên `NAME`. `NAME_U` bị drop trước khi trả UI/Excel.

`lookup_cards(ids)`: chunk 400, `CARD_ID IN (...)` exact — trả `CARD_LOOKUP_COLUMNS` (vẫn có `NAME_U`, `MOBI`, `DISC_LVL`) cho F3/F4/F5 gắn hồ sơ. Sheet danh sách thẻ F5 vẫn project về `CUSTOMER_COLUMNS` (slim).

---

## 8. F3 — Khách hàng theo kỳ

**File:** `domain/loyalty_customers.py`  
**Fact:** dual `query_strans` + `GROUP BY CARD_ID` (không TOP; không stream từng dòng)

### 8.1 SQL tổng hợp

Template body ( `{table}` = `STRANS` hoặc `STRANS_YYYYMM` ):

```sql
SELECT
  LTRIM(RTRIM(CARD_ID)) AS CARD_ID,
  MIN(LTRIM(RTRIM(STK_ID))) AS STK_ID,
  SUM(ISNULL(AMOUNT,0)+ISNULL(SURPLUS,0)+ISNULL(VAT_AMT,0)) AS total_value,
  COUNT(DISTINCT LTRIM(RTRIM(STK_ID)) + N'|' + LTRIM(RTRIM(TRANS_NUM))) AS bill_count
FROM {table}
WHERE 1=1
  AND TRAN_DATE >= ? AND TRAN_DATE < ?
  AND CARD_ID IS NOT NULL AND LTRIM(RTRIM(CARD_ID)) <> ''
  [AND LTRIM(RTRIM(STK_ID)) IN (...)]
  [AND LTRIM(RTRIM(CARD_ID)) LIKE ?]  -- fact prefix (không LOWER/CAST)
GROUP BY LTRIM(RTRIM(CARD_ID))
```

### 8.2 Pandas sau query

1. Cộng lại các shard/target cùng `CARD_ID` (`sum` value + bills, `min` STK)
2. `points = floor(total_value / 50000)`
3. Lọc min/max trên `points` hoặc `total_value`
4. `lookup_cards` → merge hồ sơ
5. Sort: UI / export

### 8.3 Export

- Excel: một file hoặc **nhiều file theo bucket điểm**
- TXT: `export/rich_report.py` từ cohort STRANS (cache UI nếu đã fetch)
- Excel thêm `giao_dich_chi_tiet.xlsx` (full dòng cohort trong kỳ)

### Điểm cần review

- `STK_ID` trên sheet khách vẫn `min` (đại diện) — TXT theo siêu thị dùng giao dịch thật.
- Prefix fact: `match_prefix_column_fact` (starts-with, không `LOWER(CAST…)`).

---

## 9. F4 — Đơn hàng theo khách

**File:** `domain/customer_orders.py`

### 9.1 Resolve SP (optional)

Nếu có “sản phẩm trong đơn”:

1. `search_products(code=q)` + `search_products(name=q)` (SearchOpts + TOP limit)
2. `raise_if_truncated` từng nhánh
3. Union `SKU_ID`

Danh sách thẻ: **exact** `IN` sau `strip` (không fuzzy).

### 9.2 Lấy dòng `STRANS` (dual)

```sql
SELECT
  STK_ID, TRANS_NUM, TRAN_DATE, TRAN_TIME, CARD_ID, TRANS_CODE,
  SKU_ID, UNIT_SYMB, AMOUNT,
  (AMOUNT+SURPLUS+VAT_AMT) AS line_value
FROM {table}
WHERE 1=1
  AND date range
  AND CARD_ID IS NOT NULL AND <> ''
  AND CARD_ID IN (...)
  [AND STK_ID IN (...)]
  [AND SKU_ID IN (...) ]          -- nếu có filter SP
  [AND AMOUNT > 0 | = 0]          -- gift/paid trên **dòng SP khớp**, chỉ khi đã có SKU filter
```

Export/preview F4 dùng `F4_ORDER_LINE_COLUMNS` (**không** `IDX`, **không** `QTY`).

Nếu **không** có filter SP: lấy mọi dòng của các thẻ (trong STK/ngày); gift mode **không** áp trên dòng.

### 9.3 Header `TRANSHDR` / `TRANSHDR_ARC`

Lọc min/max `bill_value`; inner join bill keys từ dòng matched.

### 9.4 Enrich + export (2 lớp Excel + rich TXT)

- Preview UI: 2 chế độ — **Dòng đơn khớp** | **Chi tiết full bill** (lazy `fetch_bill_lines` khi đổi mode)
- Export Excel mỗi thẻ: sheets `orders` | `matched_lines` | `bill_lines`
  - `bill_lines` = `fetch_bill_lines` toàn bộ STRANS của các `(STK_ID,TRANS_NUM)` đã giữ
- TXT: `build_orders_rich_report` — bảng STK SO/TÔNG/TB, chi tiết đơn+dòng, tần suất SP (nếu có filter SP → loại trừ SKU lọc = mua kèm)

---

## 10. F5 — Đơn hàng theo sản phẩm

**File:** `domain/product_orders.py`

### 10.1 Resolve token

`resolve_product_tokens` → per-token matched lines + `seed_skus_by_token`.

**Danh sách SP trống:** không resolve — một bucket `(tất cả SP)`:
`SELECT DISTINCT (STK_ID, TRANS_NUM, TRANS_CODE)` trên STRANS (STK đúng; không dump mọi dòng tiền) → TRANSHDR lấy `bill_value` (vẫn lọc siêu thị / thẻ / gift / giá trị / điều kiện khách).

### 10.2 Mỗi token → `_orders_for_skus`

1. STRANS tìm `(STK_ID, TRANS_NUM)` có SKU seed (+ gift/paid trên dòng seed); **SKU list rỗng** → không lọc `SKU_ID`
2. **Mode 1 / `orders`**: TRANSHDR đại diện từng giao dịch (1 dòng / đơn) — lookup theo **TRANS_NUM** (+ TRANS_CODE); **STK_ID lấy từ STRANS** vì TRANSHDR.STK_ID thường trống
3. **Mode 2 / `bill_lines`**: `fetch_bill_lines` full STRANS mọi mặt hàng trong các đơn đó — `F5_ORDER_LINE_COLUMNS` (**không** `IDX`, **không** `QTY`)

Helper: `bill_expand.fetch_transhdr_for_keys`.

### 10.3 Preview / Export

- Preview UI: **Đơn hàng (TRANSHDR)** | **Chi tiết đơn (full STRANS)** (lazy bung khi đổi mode)
- Excel kết quả / token: sheets `orders` + `bill_lines` (đủ cả 2 mode)
- **Tách file**: luôn partition trên **mode 2** (`bill_lines` / STRANS); mỗi file split chỉ sheet `bill_lines`
- **Điều kiện khách (optional):** tuổi / giới tính / tiền tố — khi bật thì chỉ đơn có thẻ (`customer_filters.py`)
- TXT rich: STK SO/TÔNG/TB, **chi tiết mọi đơn đầy đủ** (`per_card_limit=None`), tần suất mua kèm (loại trừ SKU seed)
- Option list thẻ độc lập

---

## 11. UI preview vs dữ liệu thật

| Lớp | Giới hạn |
|-----|----------|
| Master search SQL | `TOP` = `DATA_ACCESS_SEARCH_LIMIT` (500000) |
| Fact F3/F4/F5 | Không TOP |
| Preview bảng Flet | 40 dòng × 10 cột (chỉ hiển thị) |
| Excel F5 `orders` | TRANSHDR — 1 dòng / giao dịch có SP |
| Excel F5 `bill_lines` | Full STRANS các đơn đã xác định |
| Excel F5 split | Chỉ `bill_lines` (mode 2) |
| TXT rich | Thống kê từ bill_lines (giá trị = AMOUNT+SURPLUS+VAT), F5 không cắt chi tiết thẻ |

Helper bung bill: `domain/bill_expand.py`. Báo cáo: `export/rich_report.py`.

**Validate trước query (F3/F4/F5):** `ui/validate.py` — chặn Preview/Xuất nếu sai format; ô lỗi viền đỏ + `error_text` giải thích (ngày YYYY-MM-DD, số khoảng giá trị, danh sách thẻ đúng dạng, không dán nhiều mã thẻ vào ô SP, tiền tố ngắn, cú pháp mức điểm).

**Sắp xếp kết quả (F1–F6):** client-side sau search (`domain/frame_sort.py`) — mặc định `CARD_ID` (F2/F3) / `TRANS_NUM` (F4/F5) / `SKU_CODE` (F1/F6) đẩy cột lên đầu; dropdown chọn bất kỳ cột; bấm header preview đổi ↑↓; Excel dùng đúng lựa chọn sort hiện tại (không sort trong SQL/fetch).

---

## 12. Copy ID → clipboard (chuyển kết quả sang F khác)

Helper: `ui/clipboard_ids.py` — nút **Copy mã thẻ** / **Copy mã SP** trên thanh hành động.

- Lấy giá trị **unique** theo cột (`CARD_ID` hoặc `SKU_CODE`), giữ thứ tự lần đầu xuất hiện.
- Format: **một dòng một mã** (`\n`) — Ctrl+V vào ô multiline F4 (danh sách thẻ) hoặc F5 (danh sách SP).
- Copy toàn bộ frame kết quả (không chỉ 40 dòng preview).
- Clipboard: Flet `page.clipboard.set`, fallback Windows `clip`.

| Nguồn | Nút | Dán vào |
|-------|-----|---------|
| F1 / F6 | Copy mã SP | F5 (token SP), F4 (ô SP trong đơn) |
| F2 / F3 | Copy mã thẻ | F4 (danh sách thẻ) |
| F4 / F5 | Copy mã thẻ + Copy mã SP | F4 / F5 tương ứng |

---

## 13. Checklist review nhanh

1. **Cutoff / shard** — đúng topology db1/db2 và khoảng ngày con chưa?
2. **Bill value** — `AMOUNT+SURPLUS+VAT` (không dùng FOREX_AMT).
3. **F3** — metric aggregate vs báo cáo STK từ giao dịch thật đã tách bạch?
4. **F5** — Excel `orders` (TRANSHDR) + `bill_lines` (STRANS); split chỉ `bill_lines`?
5. **Gift/paid** — chỉ trên dòng SP khớp (F4 khi có SP filter; F5 khi bật).
6. **Prefix vs fuzzy** — tiền tố = starts-with; mã/tên = substring khi fuzzy ON.
7. **F5 split** — exclusive một chiều tách file?

---

## 14. File map nhanh

| Chức năng | UI | Domain |
|-----------|-----|--------|
| F1 SP | `ui/pages/product_page.py` | `domain/product.py` |
| F2 KH | `ui/pages/customer_page.py` | `domain/customer.py` |
| F3 theo kỳ | `ui/pages/loyalty_page.py` | `domain/loyalty_customers.py` |
| F4 đơn theo KH | `ui/pages/customer_orders_page.py` | `domain/customer_orders.py` |
| F5 đơn theo SP | `ui/pages/product_orders_page.py` | `domain/product_orders.py` |
| F6 nhóm | `product_page.build_group_page` | `product.search_by_group` |
| Dual DB | — | `db/cutoff.py`, `db/dual_query.py` |
| Search opts | `ui/form_kit.search_opts_bar` | `domain/search_opts.py` |
| Copy clipboard | `ui/clipboard_ids.py` | — |
| Full bill expand | — | `domain/bill_expand.py` |
| Rich TXT | — | `export/rich_report.py` |

*Cập nhật theo code tại thời điểm viết doc — nếu đổi handler, sửa doc này cùng PR.*

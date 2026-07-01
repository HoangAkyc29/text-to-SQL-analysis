# Data Dictionary Validation Report

> Chạy: `uv run python scripts/validate_data_dictionary.py`  
> Output JSON: `docs/db_exploration_samples/dictionary_validation.json` (gitignored)

## Kết nối

| DB | Trạng thái | Ghi chú |
|----|------------|---------|
| **db1** (`RESTORED_DB`) | OK | Validation đầy đủ trên live DB |
| **db2** (`RESTORED_DB2`) | **Lỗi login** | `analysisagentreadonly` không mở được DB — kiểm tra `ANALYTICS_DB_DSN_2` trong `.env` |

Phần db2 dưới đây dùng **mẫu exploration trước** (`insights_compact.json`) cho đến khi sửa được kết nối.

**Ngưỡng cutoff** (theo ngày chạy script, máy local **2026-07-01**): `2026-06-01` (= ngày 1 tháng trước).

---

## 1. Schema & cột — khớp

| Kiểm tra | Kết quả |
|----------|---------|
| `tables/db1/*.md` (4 file) vs live db1 | **Khớp** 100% tên cột |
| `tables/db2/*.md` (38 file) vs JSON export | **Khớp** 100% |
| `shards.yaml` physical tables vs live db1 | **59/59 tồn tại** |

Số cột tham chiếu: STRANS 114, PMTRANS 27, TRANSHDR_ARC 51, CRDTRANS_ARC 35.

---

## 2. Phân tách thời gian db1 / db2

### db1 (live query MIN/MAX toàn bảng)

| Bảng / nhóm | MIN `TRAN_DATE` | MAX `TRAN_DATE` | Ghi chú |
|-------------|-----------------|-----------------|---------|
| STRANS (29 shard) | 2023-12-31 | **2026-04-30** | Mọi shard có MAX &lt; cutoff 2026-06-01 |
| PMTRANS (28 shard) | 2024-01-01 | **2026-04-30** | Tương tự |
| TRANSHDR_ARC | 2017-09-27 | **2026-04-30** | ~3.7M dòng |
| CRDTRANS_ARC | 2012-12-29 | **2026-04-30** | ~1.6M dòng |

**Kết luận:** Mô tả “db1 = lịch sử trước cutoff” **đúng** với dữ liệu hiện tại. Archive dừng ở **30/04/2026** — tháng **05/2026 chưa roll** sang db1 (vẫn nằm db2). Đây là **độ trễ archive** thực tế, không mâu thuẫn với quy tắc nghiệp vụ nhưng agent cần biết có thể có khoảng “chỉ có trên db2” ngay dưới cutoff.

### db2 (từ mẫu TOP 20 — cần xác nhận lại khi reconnect)

| Bảng | `TRAN_DATE` trong mẫu | TRANS_CODE mẫu |
|------|------------------------|----------------|
| STRANS | 2026-05-02 .. 2026-05-04 | `113` |
| TRANSHDR | 2026-05-02 .. 2026-05-05 | `113` |
| PMTRANS | 2026-05-04 .. **2026-06-16** | `008`, `222` |
| CRDTRANS | 2026-05-01 .. 2026-05-16 | `811` |

**Kết luận:** db2 chứa giao dịch **từ đầu tháng 5/2026** trở đi — khớp vai trò “~2 tháng gần + live”, và lấp khoảng trống giữa db1 (tới 30/4) và cutoff (1/6).

---

## 3. TRANS_CODE / PMT_CODE — đối chiếu `domain_definitions.md`

| Mã | Ghi trong dictionary | Thấy trong dữ liệu | Đánh giá |
|----|----------------------|-------------------|----------|
| `113` | Bán lẻ STRANS/TRANSHDR | db1 shard + db2 | **Đúng** |
| `221` | Thanh toán PMTRANS | db1 PMTRANS, db2 SUSPEND | **Đúng** |
| `008` | Quỹ PMTRANS | db1 + db2 PMTRANS | **Đúng** |
| `811` | CRDTRANS db2 | db2 CRDTRANS | **Đúng** |
| `812` | CRDTRANS_ARC db1 | db1 CRDTRANS_ARC | **Đúng** |
| `821` | Thẻ PM | PMCRDISS, PMCRDSTK | **Đúng** |
| `222`, `320`, `340`, `310`, `318`, `316` | “cần map” | Nhiều trên db1 STRANS shard mới nhất | **Nên bổ sung** domain_definitions |
| `010` | — | CASH_ST | **Thiếu** |
| `211` | — | STRANS_TMP | **Thiếu** |
| `334` | — | ST_ORDER | **Thiếu** |
| `CASH` PMT_CODE | Có | PMTRANS db2 | **Đúng** |

---

## 4. Phạm vi bảng trong `data_dictionary`

| Nguồn | Số bảng |
|-------|---------|
| JSON export db1 | 59 |
| Live db1 | **182** |
| `data_dictionary` db1 | **4 logical** (+ shards.yaml) |

db1 live có **123 bảng archive khác** không nằm trong dictionary, ví dụ: `CONSIGN_YYYYMM`, `CUS_INFO_YYYYMM`, `STK_INFO_YYYYMM`, `STORECS_YYYYMM`, `CTRANS_ARC`, `ORDERS_ARC`, …

**Đánh giá:** Dictionary **đúng** với phạm vi đã chọn (giao dịch bán POS cốt lõi). Không sai — nhưng **không đầy đủ** toàn bộ RESTORED_DB. Bổ sung chỉ khi agent cần query các domain đó.

db2: JSON 38 bảng = `tables/db2/` 38 file — **đầy đủ** theo export.

---

## 5. Việc cần làm

1. **Sửa `ANALYTICS_DB_DSN_2`** — quyền user `analysisagentreadonly` trên `RESTORED_DB2`, rồi chạy lại:
   ```bash
   uv run python scripts/validate_data_dictionary.py
   uv run python scripts/explore_db_samples.py
   ```
2. **Cân nhắc bổ sung** `domain_definitions.md` cho mã `222`, `320`, `340`, `310`, `318`, `010`, `211`, `334`.
3. **Ghi chú archive lag** trong `data_dictionary/README.md` — dữ liệu tháng ngay dưới cutoff có thể chỉ có trên db2 cho đến khi roll sang db1.

---

## 6. Tóm tắt

| Hạng mục | Đúng / Sai |
|----------|------------|
| Cấu trúc db1/db2, cutoff, vai trò master trên db2 | **Đúng** (có lag archive) |
| `shards.yaml` + schema 4 bảng db1 | **Đúng** |
| 38 bảng db2 trong dictionary | **Đúng** (schema JSON) |
| TRANS_CODE chính (113, 221, 008, 811/812, 821) | **Đúng** |
| Toàn bộ bảng trên RESTORED_DB | **Chưa document** (182 vs 4 logical) |
| db2 live validation | **Chưa chạy được** — lỗi kết nối |

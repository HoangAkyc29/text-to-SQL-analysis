# Data Access App — independent supermarket SQL reader (Flet)

Desktop app đọc **db1** (`RESTORED_DB`) + **db2** (`RESTORED_DB2`) qua ODBC, không phụ thuộc agent monorepo.

## Chức năng

1. Tìm mặt hàng / theo nhóm
2. Tìm khách (thẻ)
3. Khách hàng theo kỳ — tiền tố thẻ, điểm = giá trị/50000, siêu thị, chia Excel theo mức điểm, TXT
4. Đơn hàng theo khách — nhiều thẻ → nhiều Excel `Mã thẻ – Tên`
5. Đơn hàng theo sản phẩm — mỗi SP một Excel (+ file tổng); tách theo thẻ/SKU/siêu thị
6. TCVN3 decode trên text output
7. Dual-DB: cutoff rolling + shard lịch sử / live

## Cài đặt

```powershell
cd data_access_app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
# Điền password / Server=localhost,14330 (hoặc tên máy)
```

### Connection string (quan trọng)

| Chạy từ | `Server=` |
|---------|-----------|
| Agent / sql-gateway **trong Docker** | `host.docker.internal,14330` |
| App Flet **trên Windows host** | `DESKTOP-AUQEDC5` |

App luôn ép `Server=` → `DESKTOP-AUQEDC5` (hoặc giá trị `DATA_ACCESS_SQL_SERVER`) khi load DSN từ monorepo `.env`.

## Chạy

```powershell
cd data_access_app
# Cài deps (nếu SSL lỗi với pip, dùng: uv pip install --native-tls -r requirements.txt)
pip install -r requirements.txt
$env:PYTHONPATH="."
python -m app.main
```

## Output

File Excel/TXT ghi vào `DATA_ACCESS_OUTPUT_DIR` hoặc `data_access_app/output/`.

## Tests

```powershell
pip install pytest
pytest tests -q
```

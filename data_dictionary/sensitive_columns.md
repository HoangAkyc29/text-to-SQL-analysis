# Sensitive columns (deny by default for store_manager)

Cột nhạy cảm — role `store_manager` không được SELECT (xem `config/project.yaml` `denied_columns`).

| table | column | reason |
|-------|--------|--------|
| SKU_DEF | SPPRICE | Giá mua NCC |
| SKU_DEF | LASTSPPR | Giá mua NCC gần nhất |
| HISSPPR | SPPRICE | Lịch sử giá mua |
| HISSPPR | LASTSPPR | Giá mua gần nhất |
| STRANS | SPPRICE | Giá vốn trên dòng bán |
| STRANS | LASTSPPR | Giá vốn gần nhất |
| WebRpt_sales_sku_daily | cogs | Giá vốn tổng hợp |
| WebRpt_sales_sku_daily | gross_profit | Lãi gộp |
| WebRpt_sales_sku_daily | free_cogs | Giá vốn hàng tặng |
| WebRpt_inventory_daily | value_onhand | Giá trị tồn kho |
| CSCARD | PASSCODE | PIN thẻ |
| CUSTOMER | PASSCODE | Mã PIN (nếu có) |
| CUSTOMER | PERSON_ID | CMND/CCCD |
| CustSumm | Phone | SĐT khách |
| CustSumm | Mobil | SĐT di động |

**PII:** `CUSTOMER.NAME`, `ADDRESS`, `EMAIL`, `PHONE`, `MOBI` — mask hoặc aggregate khi role hạn chế.

**Ghi chú:** Cột `*_TYPE`, `*_DEPT` ít nhạy cảm; ưu tiên chặn giá vốn và PII trực tiếp.

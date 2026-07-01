# db2 — live (RESTORED_DB2)

db2 là database **vận hành**: danh mục, chứng từ gần đây, staging POS, báo cáo tổng hợp.

## Ba nhóm dữ liệu

### 1. Master / danh mục (luôn trên db2)

Không phụ thuộc cutoff — query bất kỳ lúc nào:

`CUSTOMER`, `CSCARD`, `SKU_DEF`, `PLU`, `BARCODE`, `SUPPLIER`, `PARTNER`, `HISRTPR`, `HISSPPR`, `RDISCINF`, `ASSOLST`, `ASSO_INF`, `ACCOUNT`, `DEBT`, `PMCRDINF`, …

### 2. Giao dịch gần đây (~2 tháng)

`TRAN_DATE >= cutoff` với `cutoff` = **ngày 1 tháng trước**:

- Ví dụ **22/06/2026** → từ **01/05/2026** đến nay (trọn tháng 5 + phần tháng 6).
- Bảng: `TRANSHDR`, `STRANS`, `PMTRANS`, `CRDTRANS`, `CTRANS`, `CASH_ST`, …

### 3. Báo cáo & staging

| Loại | Bảng |
|------|------|
| Báo cáo | `WebRpt_sales_sku_daily`, `WebRpt_inventory_daily`, `WebRpt_rfm_snapshot` |
| Staging | `SUSPEND`, `STRANS_TMP`, `CRDTRANS_TMP` — không dùng báo cáo chính thức |

Schema: `../tables/db2/<TênBảng>.md`

## Gợi ý agent

- Aggregate doanh thu/tồn/RFM → ưu tiên `WebRpt_*`
- Chi tiết bill gần → `TRANSHDR` + `STRANS` + `PMTRANS` trên **db2**
- Lịch sử xa hơn cutoff → chuyển sang **db1** (shard)

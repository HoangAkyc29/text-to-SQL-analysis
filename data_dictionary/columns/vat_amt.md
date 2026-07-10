---
semantic_key: vat_amt
title: Tiền thuế GTGT (VAT_AMT)
display_names:
- VAT_AMT
kind: measure
tables:
- ref: db1:crdtrans_arc
  column: VAT_AMT
  type: numeric
- ref: db1:strans
  column: VAT_AMT
  type: numeric
- ref: db1:transhdr_arc
  column: VAT_AMT
  type: numeric
- ref: db2:crdtrans
  column: VAT_AMT
  type: numeric
- ref: db2:crdtrans_tmp
  column: VAT_AMT
  type: numeric
- ref: db2:custhist
  column: VAT_AMT
  type: numeric
- ref: db2:inv_hdr
  column: VAT_AMT
  type: numeric
- ref: db2:inv_iss
  column: VAT_AMT
  type: numeric
- ref: db2:st_order
  column: VAT_AMT
  type: decimal
- ref: db2:strans
  column: VAT_AMT
  type: numeric
- ref: db2:strans_tmp
  column: VAT_AMT
  type: numeric
- ref: db2:suspend
  column: VAT_AMT
  type: numeric
- ref: db2:transhdr
  column: VAT_AMT
  type: numeric
join_with: []
related_semantic_keys: []
facts:
- Tiền thuế VAT
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Tiền thuế GTGT (VAT_AMT)

**Semantic key:** `vat_amt` · **Cột vật lý:** `VAT_AMT`

## Ý nghĩa nghiệp vụ

Số tiền thuế GTGT (VAT) ghi trên chứng từ — grain phụ thuộc bảng. Trên STRANS/STRANS_TMP/SUSPEND là thuế từng dòng bán; TRANSHDR/TRANSHDR_ARC là tổng thuế cả bill; CRDTRANS/CRDTRANS_ARC/CRDTRANS_TMP là thuế trên doanh thu loyalty; INV_HDR/INV_ISS là thuế trên chứng từ kho; ST_ORDER là thuế trên đơn nội bộ. Không cộng VAT dòng STRANS để suy ra min bill — dùng TRANSHDR.AMOUNT / TRANSHDR.VAT_AMT.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `VAT_AMT` | numeric | thuế trên giao dịch điều chỉnh / đổi quà (812) |
| `db1:strans` | `VAT_AMT` | numeric | thuế GTGT trên từng dòng bán POS |
| `db1:transhdr_arc` | `VAT_AMT` | numeric | tổng thuế GTGT bill đã archive |
| `db2:crdtrans` | `VAT_AMT` | numeric | thuế trên doanh thu gốc tích điểm (811) |
| `db2:crdtrans_tmp` | `VAT_AMT` | numeric | thuế trên giao dịch tích điểm tạm |
| `db2:custhist` | `VAT_AMT` | numeric | thuế ghi trong snapshot lịch sử khách (ít dùng cho phân tích) |
| `db2:inv_hdr` | `VAT_AMT` | numeric | thuế GTGT trên header hóa đơn mua / nhập kho |
| `db2:inv_iss` | `VAT_AMT` | numeric | thuế GTGT trên phiếu xuất kho |
| `db2:st_order` | `VAT_AMT` | decimal | thuế GTGT trên đơn đặt hàng nội bộ |
| `db2:strans` | `VAT_AMT` | numeric | thuế GTGT trên từng dòng bán POS |
| `db2:strans_tmp` | `VAT_AMT` | numeric | thuế GTGT trên dòng bán tạm / bill treo |
| `db2:suspend` | `VAT_AMT` | numeric | thuế GTGT trên dòng bill đang treo |
| `db2:transhdr` | `VAT_AMT` | numeric | tổng thuế GTGT của cả bill header |

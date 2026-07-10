---
semantic_key: customer_id_ref
title: Mã khách hàng nội bộ (CUST_ID)
display_names:
- cust_id
- CUST_ID
kind: identifier
tables:
- ref: db1:crdtrans_arc
  column: CUST_ID
  type: char
- ref: db1:pmtrans
  column: CUST_ID
  type: char
- ref: db1:transhdr_arc
  column: CUST_ID
  type: char
- ref: db2:account
  column: CUST_ID
  type: char
- ref: db2:crd_info
  column: CUST_ID
  type: char
- ref: db2:crdtrans
  column: CUST_ID
  type: char
- ref: db2:crdtrans_tmp
  column: CUST_ID
  type: char
- ref: db2:ctrans
  column: CUST_ID
  type: char
- ref: db2:debt
  column: CUST_ID
  type: char
- ref: db2:inv_hdr
  column: CUST_ID
  type: char
- ref: db2:inv_iss
  column: CUST_ID
  type: char
- ref: db2:pmcrdinf
  column: CUST_ID
  type: char
- ref: db2:pmcrdiss
  column: CUST_ID
  type: char
- ref: db2:pmcrdrcv
  column: CUST_ID
  type: char
- ref: db2:pmcrdstk
  column: CUST_ID
  type: char
- ref: db2:pmtrans
  column: CUST_ID
  type: char
- ref: db2:rdiscinf
  column: CUST_ID
  type: char
- ref: db2:st_order
  column: CUST_ID
  type: char
- ref: db2:webrpt_rfm_snapshot
  column: cust_id
  type: varchar
join_with: []
related_semantic_keys: []
facts:
- Mã khách
sources:
- table_md
- column_semantic_registry
- business_prose
---

# Mã khách hàng nội bộ (CUST_ID)

**Semantic key:** `customer_id_ref` · **Cột vật lý:** `cust_id`, `CUST_ID`

## Ý nghĩa nghiệp vụ

Chỉ số aggregate trên báo cáo WEBRPT_RFM_SNAPSHOT — dùng cho phân tích nhanh, không thay chi tiết POS live.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò |
|------|-----|------|---------|
| `db1:crdtrans_arc` | `CUST_ID` | char | Mã khách hàng |
| `db1:pmtrans` | `CUST_ID` | char | Mã khách hàng |
| `db1:transhdr_arc` | `CUST_ID` | char | Mã khách hàng |
| `db2:account` | `CUST_ID` | char | Mã khách hàng |
| `db2:crd_info` | `CUST_ID` | char | Mã khách hàng |
| `db2:crdtrans` | `CUST_ID` | char | Mã khách hàng |
| `db2:crdtrans_tmp` | `CUST_ID` | char | Mã khách hàng |
| `db2:ctrans` | `CUST_ID` | char | Mã khách hàng |
| `db2:debt` | `CUST_ID` | char | Mã khách hàng |
| `db2:inv_hdr` | `CUST_ID` | char | Mã khách hàng |
| `db2:inv_iss` | `CUST_ID` | char | Mã khách hàng |
| `db2:pmcrdinf` | `CUST_ID` | char | Mã khách hàng |
| `db2:pmcrdiss` | `CUST_ID` | char | Mã khách hàng |
| `db2:pmcrdrcv` | `CUST_ID` | char | Mã khách hàng |
| `db2:pmcrdstk` | `CUST_ID` | char | Mã khách hàng |
| `db2:pmtrans` | `CUST_ID` | char | Mã khách hàng |
| `db2:rdiscinf` | `CUST_ID` | char | Mã khách hàng |
| `db2:st_order` | `CUST_ID` | char | Mã khách hàng |
| `db2:webrpt_rfm_snapshot` | `cust_id` | varchar | Mã khách |

## Ghi chú thêm

- Mã khách

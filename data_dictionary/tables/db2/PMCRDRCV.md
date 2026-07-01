---
logical_table: PMCRDRCV
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Thu hồi / nhận lại thẻ PM.
column_count: 20
---

# PMCRDRCV

Thu hồi / nhận lại thẻ PM.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | char | Trạng thái active/duyệt |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| CUST_ID | char | Mã khách hàng |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| VALUE_AMT | numeric | Mệnh giá / giá trị thẻ PM |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| REF_AMT | numeric | Số tiềnREF_AMT |
| RCV_NUM | char | Cột RCV_NUM |
| RCV_DATE | datetime | NgàyRCV_DATE |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| MARK_MUL | numeric | Hệ số nhân điểm |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| DISC_AMT | numeric | Số tiềnDISC_AMT |

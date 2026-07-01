---
logical_table: PMCRDSTK
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Tồn thẻ PM tại cửa hàng (seri).
column_count: 34
---

# PMCRDSTK

Tồn thẻ PM tại cửa hàng (seri).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| RS_CODE | char | Mã lý do (hủy, trả, …) |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| CUST_ID | char | Mã khách hàng |
| PREFIX | char | Prefix seri thẻ PM (@P) |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| FR_SERI | char | Seri thẻ PM từ |
| TO_SERI | char | Seri thẻ PM đến |
| FR_CARDID | char | Thẻ PM nguồn |
| TO_CARDID | char | Thẻ PM đích |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| VALUE_AMT | numeric | Mệnh giá / giá trị thẻ PM |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| STK_QTY | numeric | Số lượng tồn / xuất kho |
| ISS_QTY | numeric | SL xuất |
| RCV_QTY | numeric | SL nhận |
| STP_QTY | numeric | SL dừng/hủy |
| NODE_LIST | varchar | Cột NODE_LIST |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| MARK_MUL | numeric | Hệ số nhân điểm |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| DISC_AMT | numeric | Số tiềnDISC_AMT |
| ACTIVATE | bit | Đã kích hoạt |

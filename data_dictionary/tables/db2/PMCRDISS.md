---
logical_table: PMCRDISS
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Phiếu xuất thẻ PM cho khách (TRANS_CODE thường 821).
column_count: 33
---

# PMCRDISS

Phiếu xuất thẻ PM cho khách (TRANS_CODE thường 821).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| RS_CODE | char | Mã lý do (hủy, trả, …) |
| REF | char | Mã/tham chiếu nội bộ |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| CUST_ID | char | Mã khách hàng |
| FR_CARDID | char | Thẻ PM nguồn |
| TO_CARDID | char | Thẻ PM đích |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| VALUE_AMT | numeric | Mệnh giá / giá trị thẻ PM |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| ISS_QTY | numeric | SL xuất |
| SALE_AMT | numeric | Số tiền bán |
| DISC_AMT | numeric | Số tiềnDISC_AMT |
| DISC_PC | numeric | Cột DISC_PC |
| DISC_CODE | char | Mã chiết khấu |
| OBJ_CODE | char | MãOBJ_CODE |
| OBJ_VALUE | char | Cột OBJ_VALUE |
| CHG_TYPE | char | Cột CHG_TYPE |
| CHG_VALUE | numeric | Cột CHG_VALUE |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| MARK_MUL | numeric | Hệ số nhân điểm |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |

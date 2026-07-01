---
logical_table: INV_HDR
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Header hóa đơn GTGT điện tử.
column_count: 45
---

# INV_HDR

Header hóa đơn GTGT điện tử.

| column | type | description |
|--------|------|-------------|
| INV_REF | varchar | Tham chiếu hóa đơn |
| INV_TYPE | varchar | Loại hóa đơn |
| INV_CODE | varchar | Mã serial HĐ |
| INV_NO | varchar | Số hóa đơn |
| INV_DATE | datetime | Ngày hóa đơn |
| STR_NUM | char | Cột STR_NUM |
| STR_DATE | datetime | NgàySTR_DATE |
| ATR_NUM | char | Cột ATR_NUM |
| ATR_DATE | datetime | NgàyATR_DATE |
| TAX_NAME | nvarchar | Tên đơn vị trên HĐ |
| TAX_ADDR | nvarchar | Địa chỉ trên HĐ |
| TAX_ID | char | Mã số thuế |
| CUST_ID | char | Mã khách hàng |
| CUST_NAME | nvarchar | Tên khách hàng |
| CUST_ADDR | nvarchar | Cột CUST_ADDR |
| BUY_ID | char | Phát sinh mua/tích: BUY_ID |
| BUY_NAME | nvarchar | Phát sinh mua/tích: BUY_NAME |
| BUY_ADDR | nvarchar | Phát sinh mua/tích: BUY_ADDR |
| BUY_PHONE | varchar | Phát sinh mua/tích: BUY_PHONE |
| BUY_FAX | varchar | Phát sinh mua/tích: BUY_FAX |
| BUY_EMAIL | varchar | Phát sinh mua/tích: BUY_EMAIL |
| BANK_ACC | varchar | Cột BANK_ACC |
| BANK_NAME | nvarchar | Cột BANK_NAME |
| BANK_ADDR | nvarchar | Cột BANK_ADDR |
| ACC_HOLDER | nvarchar | Cột ACC_HOLDER |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| TAX_CODE | char | Mã thuế |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| VAT_AMT | numeric | Tiền thuế VAT |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| MDISC_AMT | numeric | Chiết khấu manual: MDISC_AMT |
| TDISC_AMT | numeric | Chiết khấu transaction: TDISC_AMT |
| TDISC_RATE | numeric | Chiết khấu transaction: TDISC_RATE |
| BANK_POS | varchar | Cột BANK_POS |
| ISS_TYPE | char | Cột ISS_TYPE |
| PMT_TYPE | char | Loại thanh toán |
| OWN | bit | Cột OWN |
| CUSTAC | char | Cột CUSTAC |
| EINV | bit | Hóa đơn điện tử |
| SND_DATE | datetime | NgàySND_DATE |
| RCV_DATE | datetime | NgàyRCV_DATE |
| UPD_DATE | datetime | NgàyUPD_DATE |
| EINV_STATUS | char | Trạng thái HĐ điện tử |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |

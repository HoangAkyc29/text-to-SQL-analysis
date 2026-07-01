---
logical_table: INV_ISS
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Chi tiết phát hành HĐ GTGT, gắn TRANS_NUM bán lẻ.
column_count: 50
---

# INV_ISS

Chi tiết phát hành HĐ GTGT, gắn TRANS_NUM bán lẻ.

| column | type | description |
|--------|------|-------------|
| INV_REF | varchar | Tham chiếu hóa đơn |
| INV_TYPE | varchar | Loại hóa đơn |
| INV_CODE | varchar | Mã serial HĐ |
| INV_NO | varchar | Số hóa đơn |
| INV_DATE | datetime | Ngày hóa đơn |
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| REF_NO | char | Số tham chiếu chứng từ liên quan |
| REF_DATE | datetime | Ngày tham chiếu |
| FR_DATE | datetime | NgàyFR_DATE |
| TO_DATE | datetime | NgàyTO_DATE |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| SHIFT | numeric | Ca làm việc |
| TAX_NAME | nvarchar | Tên đơn vị trên HĐ |
| TAX_ADDR | nvarchar | Địa chỉ trên HĐ |
| TAX_ID | varchar | Mã số thuế |
| TAX_CODE | char | Mã thuế |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| VAT_AMT | numeric | Tiền thuế VAT |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| ISS_TYPE | char | Cột ISS_TYPE |
| PMT_TYPE | char | Loại thanh toán |
| CUST_ID | char | Mã khách hàng |
| CUST_NAME | nvarchar | Tên khách hàng |
| CUST_ADDR | nvarchar | Cột CUST_ADDR |
| CUST_TYPE | char | Cột CUST_TYPE |
| BUY_ID | char | Phát sinh mua/tích: BUY_ID |
| BUY_NAME | nvarchar | Phát sinh mua/tích: BUY_NAME |
| BUY_ADDR | nvarchar | Phát sinh mua/tích: BUY_ADDR |
| PHONE | varchar | Điện thoại |
| FAX | varchar | Cột FAX |
| EMAIL | varchar | Email |
| REP_PERSON | varchar | Cột REP_PERSON |
| CON_PERSON | varchar | Cột CON_PERSON |
| PERSON_ID | varchar | CMND/CCCD |
| BANK_ACC | varchar | Cột BANK_ACC |
| ACC_HOLDER | nvarchar | Cột ACC_HOLDER |
| BANK | nvarchar | Cột BANK |
| BANK_ADDR | nvarchar | Cột BANK_ADDR |
| COMPANY | bit | Cột COMPANY |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| COPIES | numeric | Cột COPIES |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| ACTION | char | Mã thao tác |
| REF | varchar | Mã/tham chiếu nội bộ |
| Gua_ID | char | Cột Gua_ID |

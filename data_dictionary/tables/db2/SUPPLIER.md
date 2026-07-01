---
logical_table: SUPPLIER
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Master nhà cung cấp.
column_count: 74
---

# SUPPLIER

Master nhà cung cấp.

| column | type | description |
|--------|------|-------------|
| SUPP_ID | char | Mã nhà cung cấp |
| SUPP_CODE | varchar | Mã NCC hiển thị |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| SUPP_NAME | nvarchar | Tên nhà cung cấp |
| GRP_ID | char | Mã nhóm |
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| ACC_CYS | char | Cột ACC_CYS |
| CON_PERSON | varchar | Cột CON_PERSON |
| TAX_NAME | nvarchar | Tên đơn vị trên HĐ |
| TAX_ADDR | nvarchar | Địa chỉ trên HĐ |
| TAX_ID | char | Mã số thuế |
| ADDRESS | nvarchar | Địa chỉ |
| ADDRESS2 | nvarchar | Cột ADDRESS2 |
| COUNTRY | char | Cột COUNTRY |
| PLC_ID | char | Mã địa phương |
| PHONE | varchar | Điện thoại |
| FAX | varchar | Cột FAX |
| MOBI | varchar | Di động |
| MOBI2 | varchar | Cột MOBI2 |
| EMAIL | varchar | Email |
| SKYPE | varchar | Cột SKYPE |
| YM | varchar | Cột YM |
| FACEBOOK | varchar | Cột FACEBOOK |
| BANK_ACC | char | Cột BANK_ACC |
| BANK | nvarchar | Cột BANK |
| BANK_ADDR | nvarchar | Cột BANK_ADDR |
| INDUSTRY | char | Cột INDUSTRY |
| DEPT_ID | char | Cột DEPT_ID |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| COMM_RATE | numeric | Tỷ lệ hoa hồng |
| ORD_SEQ | char | Cột ORD_SEQ |
| DLV_SEQ | char | Cột DLV_SEQ |
| ORD_PERIOD | numeric | Cột ORD_PERIOD |
| STO_TIME | char | Cột STO_TIME |
| PMT_SEQ | char | Cột PMT_SEQ |
| LEAD_TIME | char | Cột LEAD_TIME |
| PMT_TIME | char | Thời điểm thanh toán |
| PMT_MODE | char | Chế độ thanh toán |
| PMT_TYPE | char | Loại thanh toán |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| CS_LEVEL | numeric | Cột CS_LEVEL |
| FIXSALEPR | numeric | Cột FIXSALEPR |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| STAFF_ID | char | Mã nhân viên |
| CONTR_NUM | varchar | Cột CONTR_NUM |
| CONTR_DT | datetime | Cột CONTR_DT |
| REG_NUM | varchar | Cột REG_NUM |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| STATUS | bit | Trạng thái active/duyệt |
| FINE_RATE | numeric | Tỷ lệFINE_RATE |
| GUA_ID | char | Cột GUA_ID |
| GUA_RELA | char | Cột GUA_RELA |
| CONTR_BR | nvarchar | Cột CONTR_BR |
| REP_PERSON | varchar | Cột REP_PERSON |
| ACC_HOLDER | nvarchar | Cột ACC_HOLDER |
| BLOCK_CODE | char | MãBLOCK_CODE |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| OWN | bit | Cột OWN |
| MDC_ID | char | Cột MDC_ID |
| COMP_ID | char | Mã công ty |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| OWN_COMPID | char | Cột OWN_COMPID |
| MERC_TYPE | char | Loại hàng hóa |
| COMPANY | bit | Cột COMPANY |
| NOTES | nvarchar | Ghi chú bổ sung |
| PROP_VALUE | numeric | Cột PROP_VALUE |
| PERSON_ID | varchar | CMND/CCCD |
| MOA | numeric | Cột MOA |
| MOQ | numeric | Cột MOQ |
| BUYER_ID | char | Cột BUYER_ID |
| SUPP_NAME_U | nvarchar | Cột SUPP_NAME_U |

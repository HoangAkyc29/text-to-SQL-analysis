---
logical_table: CUSTOMER
data_source: db2
temporal_scope: master
temporal_rule: Không phụ thuộc cutoff — danh mục / báo cáo tổng hợp luôn trên db2.
description: Master khách hàng B2B/B2C — chỉ trên db2 (live).
column_count: 73
---

# CUSTOMER

Master khách hàng B2B/B2C — chỉ trên db2 (live).

| column | type | description |
|--------|------|-------------|
| CUST_ID | char | Mã khách hàng |
| CUST_CODE | varchar | Mã khách (hiển thị) |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| CUST_NAME | nvarchar | Tên khách hàng |
| GRP_ID | char | Mã nhóm |
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| ACC_CYS | char | Cột ACC_CYS |
| TAX_NAME | nvarchar | Tên đơn vị trên HĐ |
| TAX_ADDR | nvarchar | Địa chỉ trên HĐ |
| TAX_ID | varchar | Mã số thuế |
| DISC_LVL | numeric | Mức chiết khấu |
| ADDRESS | nvarchar | Địa chỉ |
| ADDRESS2 | nvarchar | Cột ADDRESS2 |
| COUNTRY | char | Cột COUNTRY |
| PLC_ID | char | Mã địa phương |
| PHONE | varchar | Điện thoại |
| FAX | varchar | Cột FAX |
| CON_PERSON | varchar | Cột CON_PERSON |
| MOBI | varchar | Di động |
| MOBI2 | varchar | Cột MOBI2 |
| EMAIL | varchar | Email |
| SKYPE | varchar | Cột SKYPE |
| YM | varchar | Cột YM |
| FACEBOOK | varchar | Cột FACEBOOK |
| BANK_ACC | varchar | Cột BANK_ACC |
| BANK | nvarchar | Cột BANK |
| BANK_ADDR | nvarchar | Cột BANK_ADDR |
| INDUSTRY | char | Cột INDUSTRY |
| DEPT_ID | char | Cột DEPT_ID |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| COMM_RATE | numeric | Tỷ lệ hoa hồng |
| PERSON_ID | varchar | CMND/CCCD |
| SEX | char | Giới tính |
| BIRTHDAY | datetime | Cột BIRTHDAY |
| FAMILY | nvarchar | Cột FAMILY |
| JOB | nvarchar | Cột JOB |
| HOBBY | nvarchar | Cột HOBBY |
| NOTES | nvarchar | Ghi chú bổ sung |
| DELIVERY | bit | Cột DELIVERY |
| DEBT_MODE | bit | Cột DEBT_MODE |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| COMPANY | bit | Cột COMPANY |
| CS_LEVEL | numeric | Cột CS_LEVEL |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| STATUS | bit | Trạng thái active/duyệt |
| CONTR_BR | nvarchar | Cột CONTR_BR |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| REG_NUM | varchar | Cột REG_NUM |
| CONTR_DT | datetime | Cột CONTR_DT |
| CONTR_NUM | varchar | Cột CONTR_NUM |
| GUA_ID | char | Cột GUA_ID |
| GUA_RELA | char | Cột GUA_RELA |
| REP_PERSON | varchar | Cột REP_PERSON |
| ACC_HOLDER | nvarchar | Cột ACC_HOLDER |
| BLOCK_CODE | char | MãBLOCK_CODE |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| OWN | bit | Cột OWN |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| COMP_ID | char | Mã công ty |
| HAMLET | nvarchar | Cột HAMLET |
| CITY | nvarchar | Cột CITY |
| DISTRICT | nvarchar | Cột DISTRICT |
| WARD | nvarchar | Cột WARD |
| STREET | nvarchar | Cột STREET |
| HOUSE_NO | nvarchar | Cột HOUSE_NO |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| OWN_COMPID | char | Cột OWN_COMPID |
| MERC_TYPE | char | Loại hàng hóa |
| PROP_VALUE | numeric | Cột PROP_VALUE |
| CUST_NAME_U | nvarchar | Cột CUST_NAME_U |

---
logical_table: PARTNER
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Master đối tác (đại lý, guarantor, …).
column_count: 63
---

# PARTNER

Master đối tác (đại lý, guarantor, …).

| column | type | description |
|--------|------|-------------|
| ID | char | Cột ID |
| CODE | varchar | Cột CODE |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| NAME | nvarchar | Tên |
| GRP_ID | char | Mã nhóm |
| ACCOUNT_ID | char | Mã tài khoản công nợ |
| ACC_CYS | char | Cột ACC_CYS |
| TAX_NAME | nvarchar | Tên đơn vị trên HĐ |
| TAX_ADDR | nvarchar | Địa chỉ trên HĐ |
| TAX_ID | varchar | Mã số thuế |
| CON_PERSON | varchar | Cột CON_PERSON |
| BIRTHDAY | datetime | Cột BIRTHDAY |
| SEX | char | Giới tính |
| JOB | char | Cột JOB |
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
| BANK_ACC | varchar | Cột BANK_ACC |
| BANK | nvarchar | Cột BANK |
| BANK_ADDR | nvarchar | Cột BANK_ADDR |
| INDUSTRY | char | Cột INDUSTRY |
| DEPT_ID | char | Cột DEPT_ID |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| DEBT_MODE | bit | Cột DEBT_MODE |
| NDUEDAY | numeric | Cột NDUEDAY |
| PAYDAY | numeric | Cột PAYDAY |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| OPEN_DATE | datetime | Ngày mở / tạo |
| STATUS | bit | Trạng thái active/duyệt |
| GUA_ID | char | Cột GUA_ID |
| GUA_RELA | char | Cột GUA_RELA |
| INTER_RATE | numeric | Tỷ lệINTER_RATE |
| fine_rate | numeric | Cột fine_rate |
| CR_LIMIT | numeric | Hạn mức tín dụng |
| CR_AMT | numeric | Dư nợ hiện tại |
| CONTR_BR | nvarchar | Cột CONTR_BR |
| REP_PERSON | varchar | Cột REP_PERSON |
| ACC_HOLDER | nvarchar | Cột ACC_HOLDER |
| BLOCK_CODE | char | MãBLOCK_CODE |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| OWN | bit | Cột OWN |
| MDC_ID | char | Cột MDC_ID |
| COMP_ID | char | Mã công ty |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| OWN_COMPID | char | Cột OWN_COMPID |
| MERC_TYPE | char | Loại hàng hóa |
| COMPANY | bit | Cột COMPANY |
| NOTES | nvarchar | Ghi chú bổ sung |
| PERSON_ID | varchar | CMND/CCCD |
| BUYER_ID | char | Cột BUYER_ID |
| NAME_U | nvarchar | Cột NAME_U |

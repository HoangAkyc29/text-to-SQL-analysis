---
logical_table: CSCARD
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Master thẻ loyalty.
column_count: 49
---

# CSCARD

Master thẻ loyalty.

| column | type | description |
|--------|------|-------------|
| IDX | int | ID nội bộ bản ghi thẻ |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| CUST_ID | char | Mã khách hàng |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| CARD_ID2 | char | Cột CARD_ID2 |
| BARCODE | char | Mã vạch |
| PASSCODE | char | Mã PIN thẻ |
| PERSON_ID | varchar | CMND/CCCD |
| NAME | nvarchar | Tên chủ thẻ |
| SEX | char | Giới tính |
| ADDRESS | nvarchar | Địa chỉ |
| PLC_ID | char | Mã địa phương |
| EMAIL | varchar | Email |
| PHONE | varchar | Điện thoại |
| DISC_LVL | numeric | Mức chiết khấu / hạng thẻ |
| DISC_CODE | char | Mã chương trình chiết khấu thẻ |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| BONUS_PC | numeric | Phần trăm thưởng |
| ISS_DATE | datetime | Ngày phát hành thẻ |
| EF_DATE | datetime | Ngày hiệu lực |
| DUE_DATE | datetime | Ngày hết hạn thẻ |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| LAST_CALL | datetime | Cột LAST_CALL |
| FRESH_DATE | datetime | NgàyFRESH_DATE |
| BIRTHDAY | datetime | Ngày sinh |
| RS_CODE | char | Mã lý do / trạng thái thẻ |
| IMAGE | varchar | Cột IMAGE |
| POST | char | Trạng thái post chứng từ |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| STATUS | bit | Trạng thái active/duyệt |
| MOBI | varchar | Di động |
| HAMLET | nvarchar | Cột HAMLET |
| CITY | nvarchar | Cột CITY |
| DISTRICT | nvarchar | Cột DISTRICT |
| WARD | nvarchar | Cột WARD |
| STREET | nvarchar | Cột STREET |
| HOUSE_NO | nvarchar | Cột HOUSE_NO |
| OWN_COMPID | char | Cột OWN_COMPID |
| OPEN_DATE | datetime | Ngày mở / tạo |
| CHR_CODE | varchar | MãCHR_CODE |
| HEX_CODE | varchar | MãHEX_CODE |
| RADIUS | int | Cột RADIUS |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| COUNTRY | char | Cột COUNTRY |
| NAME_U | nvarchar | Cột NAME_U |
| CHANGEPWD | bit | Cột CHANGEPWD |
| HASHEDPWD | ntext | Cột HASHEDPWD |
| ISWEBUSE | bit | Cột ISWEBUSE |
| ISLOCKED | bit | Cột ISLOCKED |

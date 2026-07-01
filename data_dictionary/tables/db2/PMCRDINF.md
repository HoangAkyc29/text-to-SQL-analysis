---
logical_table: PMCRDINF
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Thông tin thẻ PM (gift/voucher).
column_count: 29
---

# PMCRDINF

Thông tin thẻ PM (gift/voucher).

| column | type | description |
|--------|------|-------------|
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| PASSCODE | nvarchar | Mã PIN thẻ |
| VALUE_AMT | numeric | Mệnh giá / giá trị thẻ PM |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| COND_AMT | numeric | Số tiềnCOND_AMT |
| NODE_LIST | varchar | Cột NODE_LIST |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| CUST_ID | char | Mã khách hàng |
| ACTIVATE | bit | Đã kích hoạt |
| SALEABLE | char | Được phép bán |
| SALE_AMT | numeric | Số tiền bán |
| STK_NUM | char | Cột STK_NUM |
| STK_DATE | datetime | NgàySTK_DATE |
| ISS_NUM | char | Cột ISS_NUM |
| ISS_DATE | datetime | NgàyISS_DATE |
| RCV_NUM | char | Cột RCV_NUM |
| RCV_DATE | datetime | NgàyRCV_DATE |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| STATUS | bit | Trạng thái active/duyệt |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| MARK_MUL | numeric | Hệ số nhân điểm |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| DISC_AMT | numeric | Số tiềnDISC_AMT |
| BAL_AMT | numeric | Số dư |
| BARCODE | char | Mã vạch |
| CHR_CODE | varchar | MãCHR_CODE |
| HEX_CODE | varchar | MãHEX_CODE |
| PAID_AMT | numeric | Số tiền đã thanh toán |

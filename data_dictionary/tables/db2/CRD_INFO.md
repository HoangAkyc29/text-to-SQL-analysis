---
logical_table: CRD_INFO
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Số dư tích lũy điểm theo kỳ và chương trình.
column_count: 29
---

# CRD_INFO

Số dư tích lũy điểm theo kỳ và chương trình.

| column | type | description |
|--------|------|-------------|
| IDX | numeric | ID nội bộ bản ghi tích lũy |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| CUST_ID | char | Mã khách hàng |
| TYPE | char | Loại bản ghi (ngữ cảnh theo bảng) |
| ACML_CODE | char | Mã chương trình tích lũy |
| DISC_LVL | numeric | Mức chiết khấu |
| FR_DATE | datetime | NgàyFR_DATE |
| TO_DATE | datetime | NgàyTO_DATE |
| PERIOD | char | Cột PERIOD |
| BEG_BMARK | numeric | Số dư đầu kỳ: BEG_BMARK |
| BEG_BAMT | numeric | Số dư đầu kỳ: BEG_BAMT |
| BEG_BTRS | numeric | Số dư đầu kỳ: BEG_BTRS |
| BEG_OMARK | numeric | Số dư đầu kỳ: BEG_OMARK |
| BEG_OAMT | numeric | Số dư đầu kỳ: BEG_OAMT |
| BEG_OTRS | numeric | Số dư đầu kỳ: BEG_OTRS |
| BEG_RAMT | numeric | Số dư đầu kỳ: BEG_RAMT |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| BUY_AMT | numeric | Phát sinh mua/tích: BUY_AMT |
| BUY_TRS | numeric | Phát sinh mua/tích: BUY_TRS |
| OTH_MARK | numeric | Phát sinh khác: OTH_MARK |
| OTH_AMT | numeric | Phát sinh khác: OTH_AMT |
| OTH_TRS | numeric | Phát sinh khác: OTH_TRS |
| RFN_AMT | numeric | Hoàn / refund điểm: RFN_AMT |
| LAST_DATE | datetime | Ngày giao dịch / cập nhật gần nhất |
| LAST_CALL | datetime | Cột LAST_CALL |
| COMP_ID | char | Mã công ty |
| OPEN_DATE | datetime | Ngày mở / tạo |
| CLOSE_DATE | datetime | Ngày đóng |

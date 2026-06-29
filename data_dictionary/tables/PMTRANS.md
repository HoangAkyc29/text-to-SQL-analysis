---
logical_table: PMTRANS
data_source: db1
physical_pattern: PMTRANS_{YYYYMM}
shard_key_column: TRAN_DATE
description: '[TODO: mô tả nghiệp vụ bảng PMTRANS — thanh toán]'
column_count: 27
---

# PMTRANS

[TODO: mô tả nghiệp vụ bảng PMTRANS — thanh toán]

Cột dưới đây đồng nhất trên mọi physical table thuộc logical table này (xem `db1/shards.yaml`).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | [TODO: mô tả cột TRANS_NUM] |
| TRANS_CODE | char | [TODO: mô tả cột TRANS_CODE] |
| TRAN_DATE | datetime | [TODO: mô tả cột TRAN_DATE] |
| TRAN_TIME | char | [TODO: mô tả cột TRAN_TIME] |
| BU_ID | char | [TODO: mô tả cột BU_ID] |
| CARD_ID | char | [TODO: mô tả cột CARD_ID] |
| IDX | int | [TODO: mô tả cột IDX] |
| PMT_CODE | char | [TODO: mô tả cột PMT_CODE] |
| CYS | char | [TODO: mô tả cột CYS] |
| FOREX_RATE | numeric | [TODO: mô tả cột FOREX_RATE] |
| FOREX_AMT | numeric | [TODO: mô tả cột FOREX_AMT] |
| AMOUNT | numeric | [TODO: mô tả cột AMOUNT] |
| ROUNDIFF | numeric | [TODO: mô tả cột ROUNDIFF] |
| STK_ID | char | [TODO: mô tả cột STK_ID] |
| CUST_ID | char | [TODO: mô tả cột CUST_ID] |
| WS_ID | int | [TODO: mô tả cột WS_ID] |
| POS_ID | int | [TODO: mô tả cột POS_ID] |
| SHIFT | numeric | [TODO: mô tả cột SHIFT] |
| USER_ID | int | [TODO: mô tả cột USER_ID] |
| UPDATED | bit | [TODO: mô tả cột UPDATED] |
| REF | char | [TODO: mô tả cột REF] |
| POST | char | [TODO: mô tả cột POST] |
| REMARK | nvarchar | [TODO: mô tả cột REMARK] |
| STATUS | bit | [TODO: mô tả cột STATUS] |
| REF_NO | varchar | [TODO: mô tả cột REF_NO] |
| REF_DATE | datetime | [TODO: mô tả cột REF_DATE] |
| ACTION | char | [TODO: mô tả cột ACTION] |

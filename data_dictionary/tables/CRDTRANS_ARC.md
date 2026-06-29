---
logical_table: CRDTRANS_ARC
data_source: db1
physical_pattern: CRDTRANS_ARC
shard_key_column: TRAN_DATE
description: '[TODO: mô tả nghiệp vụ bảng CRDTRANS_ARC — archive thẻ/điểm]'
column_count: 35
---

# CRDTRANS_ARC

[TODO: mô tả nghiệp vụ bảng CRDTRANS_ARC — archive thẻ/điểm]

Cột dưới đây đồng nhất trên mọi physical table thuộc logical table này (xem `db1/shards.yaml`).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | [TODO: mô tả cột TRANS_NUM] |
| CARD_ID | char | [TODO: mô tả cột CARD_ID] |
| ACML_CODE | char | [TODO: mô tả cột ACML_CODE] |
| TRAN_DATE | datetime | [TODO: mô tả cột TRAN_DATE] |
| TRAN_TIME | char | [TODO: mô tả cột TRAN_TIME] |
| TRANS_CODE | char | [TODO: mô tả cột TRANS_CODE] |
| TRANS_TYPE | char | [TODO: mô tả cột TRANS_TYPE] |
| RS_CODE | char | [TODO: mô tả cột RS_CODE] |
| BU_ID | char | [TODO: mô tả cột BU_ID] |
| IDX | numeric | [TODO: mô tả cột IDX] |
| CUST_ID | char | [TODO: mô tả cột CUST_ID] |
| TYPE | char | [TODO: mô tả cột TYPE] |
| DISCOUNT | numeric | [TODO: mô tả cột DISCOUNT] |
| AMOUNT | numeric | [TODO: mô tả cột AMOUNT] |
| MARK | numeric | [TODO: mô tả cột MARK] |
| MARK_VAL | numeric | [TODO: mô tả cột MARK_VAL] |
| MARK_MUL | numeric | [TODO: mô tả cột MARK_MUL] |
| RFN_AMT | numeric | [TODO: mô tả cột RFN_AMT] |
| RFN_MARK | numeric | [TODO: mô tả cột RFN_MARK] |
| RFN_RATE | numeric | [TODO: mô tả cột RFN_RATE] |
| RBT_AMT | numeric | [TODO: mô tả cột RBT_AMT] |
| PRG_CODE | char | [TODO: mô tả cột PRG_CODE] |
| REF | char | [TODO: mô tả cột REF] |
| USER_ID | int | [TODO: mô tả cột USER_ID] |
| WS_ID | int | [TODO: mô tả cột WS_ID] |
| STAFF_ID | char | [TODO: mô tả cột STAFF_ID] |
| NOTES | nvarchar | [TODO: mô tả cột NOTES] |
| RCV_DATE | datetime | [TODO: mô tả cột RCV_DATE] |
| RCV_TIME | char | [TODO: mô tả cột RCV_TIME] |
| REMARK | nvarchar | [TODO: mô tả cột REMARK] |
| POST | char | [TODO: mô tả cột POST] |
| STATUS | bit | [TODO: mô tả cột STATUS] |
| STK_ID | char | [TODO: mô tả cột STK_ID] |
| VAT_AMT | numeric | [TODO: mô tả cột VAT_AMT] |
| COMM_AMT | numeric | [TODO: mô tả cột COMM_AMT] |

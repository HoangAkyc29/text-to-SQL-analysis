---
logical_table: TRANSHDR_ARC
data_source: db1
physical_pattern: TRANSHDR_ARC
shard_key_column: TRAN_DATE
description: '[TODO: mô tả nghiệp vụ bảng TRANSHDR_ARC — archive header giao dịch]'
column_count: 51
---

# TRANSHDR_ARC

[TODO: mô tả nghiệp vụ bảng TRANSHDR_ARC — archive header giao dịch]

Cột dưới đây đồng nhất trên mọi physical table thuộc logical table này (xem `db1/shards.yaml`).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | [TODO: mô tả cột TRANS_NUM] |
| IDX | numeric | [TODO: mô tả cột IDX] |
| TRANS_CODE | char | [TODO: mô tả cột TRANS_CODE] |
| TRAN_DATE | datetime | [TODO: mô tả cột TRAN_DATE] |
| TRAN_TIME | char | [TODO: mô tả cột TRAN_TIME] |
| DUE_DATE | datetime | [TODO: mô tả cột DUE_DATE] |
| EF_DATE | datetime | [TODO: mô tả cột EF_DATE] |
| BU_ID | char | [TODO: mô tả cột BU_ID] |
| REF_NO | char | [TODO: mô tả cột REF_NO] |
| REF_DATE | datetime | [TODO: mô tả cột REF_DATE] |
| REF_TYPE | char | [TODO: mô tả cột REF_TYPE] |
| POST | char | [TODO: mô tả cột POST] |
| STK_ID | char | [TODO: mô tả cột STK_ID] |
| STK_TYPE | char | [TODO: mô tả cột STK_TYPE] |
| SUPP_ID | char | [TODO: mô tả cột SUPP_ID] |
| SUPP_TYPE | char | [TODO: mô tả cột SUPP_TYPE] |
| CUST_ID | char | [TODO: mô tả cột CUST_ID] |
| CUST_TYPE | char | [TODO: mô tả cột CUST_TYPE] |
| IMP_ID | char | [TODO: mô tả cột IMP_ID] |
| IMP_TYPE | char | [TODO: mô tả cột IMP_TYPE] |
| EXP_ID | char | [TODO: mô tả cột EXP_ID] |
| EXP_TYPE | char | [TODO: mô tả cột EXP_TYPE] |
| AMOUNT | numeric | [TODO: mô tả cột AMOUNT] |
| SURPLUS | numeric | [TODO: mô tả cột SURPLUS] |
| VAT_AMT | numeric | [TODO: mô tả cột VAT_AMT] |
| DISCOUNT | numeric | [TODO: mô tả cột DISCOUNT] |
| COMM_AMT | numeric | [TODO: mô tả cột COMM_AMT] |
| DEPOSIT | numeric | [TODO: mô tả cột DEPOSIT] |
| PAID_AMT | numeric | [TODO: mô tả cột PAID_AMT] |
| DEDUCT | numeric | [TODO: mô tả cột DEDUCT] |
| USER_ID | int | [TODO: mô tả cột USER_ID] |
| WS_ID | int | [TODO: mô tả cột WS_ID] |
| STAFF_ID | char | [TODO: mô tả cột STAFF_ID] |
| CARD_ID | char | [TODO: mô tả cột CARD_ID] |
| REF | char | [TODO: mô tả cột REF] |
| PMT_MODE | char | [TODO: mô tả cột PMT_MODE] |
| UPDATED | bit | [TODO: mô tả cột UPDATED] |
| COPIES | numeric | [TODO: mô tả cột COPIES] |
| SHIFT | numeric | [TODO: mô tả cột SHIFT] |
| ACTION | char | [TODO: mô tả cột ACTION] |
| INV_STATUS | char | [TODO: mô tả cột INV_STATUS] |
| IC_STATUS | char | [TODO: mô tả cột IC_STATUS] |
| REMARK | nvarchar | [TODO: mô tả cột REMARK] |
| STATUS | char | [TODO: mô tả cột STATUS] |
| CTC_ID | char | [TODO: mô tả cột CTC_ID] |
| PMT_TIME | char | [TODO: mô tả cột PMT_TIME] |
| CONTR_DT | datetime | [TODO: mô tả cột CONTR_DT] |
| CONTR_NUM | varchar | [TODO: mô tả cột CONTR_NUM] |
| CAR_ID | char | [TODO: mô tả cột CAR_ID] |
| CONTR_BR | nvarchar | [TODO: mô tả cột CONTR_BR] |
| REG_NUM | varchar | [TODO: mô tả cột REG_NUM] |

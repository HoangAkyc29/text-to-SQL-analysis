---
logical_table: STRANS
data_source: db1
physical_pattern: STRANS_{YYYYMM}
shard_key_column: TRAN_DATE
description: '[TODO: mô tả nghiệp vụ bảng STRANS — chi tiết dòng giao dịch]'
column_count: 114
---

# STRANS

[TODO: mô tả nghiệp vụ bảng STRANS — chi tiết dòng giao dịch]

Cột dưới đây đồng nhất trên mọi physical table thuộc logical table này (xem `db1/shards.yaml`).

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | [TODO: mô tả cột TRANS_NUM] |
| TRANS_CODE | char | [TODO: mô tả cột TRANS_CODE] |
| TRAN_DATE | datetime | [TODO: mô tả cột TRAN_DATE] |
| TRAN_TIME | char | [TODO: mô tả cột TRAN_TIME] |
| DUE_DATE | datetime | [TODO: mô tả cột DUE_DATE] |
| EF_DATE | datetime | [TODO: mô tả cột EF_DATE] |
| BU_ID | char | [TODO: mô tả cột BU_ID] |
| REF_NO | char | [TODO: mô tả cột REF_NO] |
| REF_DATE | datetime | [TODO: mô tả cột REF_DATE] |
| INV_TYPE | varchar | [TODO: mô tả cột INV_TYPE] |
| INV_CODE | varchar | [TODO: mô tả cột INV_CODE] |
| INV_NO | varchar | [TODO: mô tả cột INV_NO] |
| INV_Date | datetime | [TODO: mô tả cột INV_Date] |
| INV_VATAMT | numeric | [TODO: mô tả cột INV_VATAMT] |
| INV_DEPT | char | [TODO: mô tả cột INV_DEPT] |
| POST | char | [TODO: mô tả cột POST] |
| RS_CODE | char | [TODO: mô tả cột RS_CODE] |
| IMPORT | bit | [TODO: mô tả cột IMPORT] |
| STK_ID | char | [TODO: mô tả cột STK_ID] |
| STK_TYPE | char | [TODO: mô tả cột STK_TYPE] |
| OSTK_ID | char | [TODO: mô tả cột OSTK_ID] |
| OSTK_TYPE | char | [TODO: mô tả cột OSTK_TYPE] |
| PACK_ID | char | [TODO: mô tả cột PACK_ID] |
| PACK_TYPE | char | [TODO: mô tả cột PACK_TYPE] |
| PACK_QTY | numeric | [TODO: mô tả cột PACK_QTY] |
| KIT_ID | char | [TODO: mô tả cột KIT_ID] |
| KIT_TYPE | char | [TODO: mô tả cột KIT_TYPE] |
| KIT_QTY | numeric | [TODO: mô tả cột KIT_QTY] |
| ASSO_ID | char | [TODO: mô tả cột ASSO_ID] |
| ASSO_QTY | numeric | [TODO: mô tả cột ASSO_QTY] |
| IDX | numeric | [TODO: mô tả cột IDX] |
| SKU_ID | char | [TODO: mô tả cột SKU_ID] |
| QTY | numeric | [TODO: mô tả cột QTY] |
| STK_QTY | numeric | [TODO: mô tả cột STK_QTY] |
| CNT_QTY | numeric | [TODO: mô tả cột CNT_QTY] |
| UNIT_SYMB | char | [TODO: mô tả cột UNIT_SYMB] |
| BASE_UNIT | char | [TODO: mô tả cột BASE_UNIT] |
| UNITCONV | numeric | [TODO: mô tả cột UNITCONV] |
| AMOUNT | numeric | [TODO: mô tả cột AMOUNT] |
| SURPLUS | numeric | [TODO: mô tả cột SURPLUS] |
| VAT_AMT | numeric | [TODO: mô tả cột VAT_AMT] |
| VAT_INCL | bit | [TODO: mô tả cột VAT_INCL] |
| COMM_AMT | numeric | [TODO: mô tả cột COMM_AMT] |
| COMM_RATE | numeric | [TODO: mô tả cột COMM_RATE] |
| DISCOUNT | numeric | [TODO: mô tả cột DISCOUNT] |
| DISC_RATE | numeric | [TODO: mô tả cột DISC_RATE] |
| CDISC_CODE | char | [TODO: mô tả cột CDISC_CODE] |
| CDISC_RATE | numeric | [TODO: mô tả cột CDISC_RATE] |
| CDISC_AMT | numeric | [TODO: mô tả cột CDISC_AMT] |
| TDISC_CODE | char | [TODO: mô tả cột TDISC_CODE] |
| TDISC_RATE | numeric | [TODO: mô tả cột TDISC_RATE] |
| TDISC_AMT | numeric | [TODO: mô tả cột TDISC_AMT] |
| TDISC_TYPE | char | [TODO: mô tả cột TDISC_TYPE] |
| MDISC_CODE | char | [TODO: mô tả cột MDISC_CODE] |
| MDISC_AMT | numeric | [TODO: mô tả cột MDISC_AMT] |
| MDISC_TYPE | char | [TODO: mô tả cột MDISC_TYPE] |
| GDISC_CODE | char | [TODO: mô tả cột GDISC_CODE] |
| GIFT_SQTY | numeric | [TODO: mô tả cột GIFT_SQTY] |
| GIFT_QTY | numeric | [TODO: mô tả cột GIFT_QTY] |
| CCOMM_CODE | char | [TODO: mô tả cột CCOMM_CODE] |
| CCOMM_RATE | numeric | [TODO: mô tả cột CCOMM_RATE] |
| CCOMM_AMT | numeric | [TODO: mô tả cột CCOMM_AMT] |
| TCOMM_CODE | char | [TODO: mô tả cột TCOMM_CODE] |
| TCOMM_RATE | numeric | [TODO: mô tả cột TCOMM_RATE] |
| TCOMM_AMT | numeric | [TODO: mô tả cột TCOMM_AMT] |
| TCOMM_TYPE | char | [TODO: mô tả cột TCOMM_TYPE] |
| MCOMM_CODE | char | [TODO: mô tả cột MCOMM_CODE] |
| MCOMM_AMT | numeric | [TODO: mô tả cột MCOMM_AMT] |
| MCOMM_TYPE | char | [TODO: mô tả cột MCOMM_TYPE] |
| GCOMM_CODE | char | [TODO: mô tả cột GCOMM_CODE] |
| GCOMM_SQTY | numeric | [TODO: mô tả cột GCOMM_SQTY] |
| GCOMM_QTY | numeric | [TODO: mô tả cột GCOMM_QTY] |
| TAX_CODE | char | [TODO: mô tả cột TAX_CODE] |
| FOREX_RATE | numeric | [TODO: mô tả cột FOREX_RATE] |
| FOREX_CYS | char | [TODO: mô tả cột FOREX_CYS] |
| FOREX_AMT | numeric | [TODO: mô tả cột FOREX_AMT] |
| EXPIRY_DT | datetime | [TODO: mô tả cột EXPIRY_DT] |
| WARR_TM | char | [TODO: mô tả cột WARR_TM] |
| USER_ID | int | [TODO: mô tả cột USER_ID] |
| WS_ID | int | [TODO: mô tả cột WS_ID] |
| CS_ID | char | [TODO: mô tả cột CS_ID] |
| STAFF_ID | char | [TODO: mô tả cột STAFF_ID] |
| CARD_ID | char | [TODO: mô tả cột CARD_ID] |
| REF | char | [TODO: mô tả cột REF] |
| REMARK | nvarchar | [TODO: mô tả cột REMARK] |
| UPDATED | bit | [TODO: mô tả cột UPDATED] |
| MERC_TYPE | char | [TODO: mô tả cột MERC_TYPE] |
| MBC | bit | [TODO: mô tả cột MBC] |
| SKU | bit | [TODO: mô tả cột SKU] |
| COPIES | numeric | [TODO: mô tả cột COPIES] |
| SHIFT | numeric | [TODO: mô tả cột SHIFT] |
| ACTION | char | [TODO: mô tả cột ACTION] |
| INV_STATUS | char | [TODO: mô tả cột INV_STATUS] |
| IC_STATUS | char | [TODO: mô tả cột IC_STATUS] |
| STATUS | char | [TODO: mô tả cột STATUS] |
| SUPP_ID | char | [TODO: mô tả cột SUPP_ID] |
| ITEM_TYPE | char | [TODO: mô tả cột ITEM_TYPE] |
| REF_TYPE | char | [TODO: mô tả cột REF_TYPE] |
| gdisc_amt | numeric | [TODO: mô tả cột gdisc_amt] |
| INV_REF | varchar | [TODO: mô tả cột INV_REF] |
| CDISC_TYPE | char | [TODO: mô tả cột CDISC_TYPE] |
| TDADD_TYPE | char | [TODO: mô tả cột TDADD_TYPE] |
| TDADD_RATE | numeric | [TODO: mô tả cột TDADD_RATE] |
| TDADD_AMT | numeric | [TODO: mô tả cột TDADD_AMT] |
| MDISC_RATE | numeric | [TODO: mô tả cột MDISC_RATE] |
| MDADD_TYPE | char | [TODO: mô tả cột MDADD_TYPE] |
| MDADD_RATE | numeric | [TODO: mô tả cột MDADD_RATE] |
| MDADD_AMT | numeric | [TODO: mô tả cột MDADD_AMT] |
| INV_POS | varchar | [TODO: mô tả cột INV_POS] |
| PMT_MODE | char | [TODO: mô tả cột PMT_MODE] |
| PMT_TYPE | char | [TODO: mô tả cột PMT_TYPE] |
| PMT_TIME | char | [TODO: mô tả cột PMT_TIME] |
| TDADD_CODE | char | [TODO: mô tả cột TDADD_CODE] |
| MDADD_CODE | char | [TODO: mô tả cột MDADD_CODE] |

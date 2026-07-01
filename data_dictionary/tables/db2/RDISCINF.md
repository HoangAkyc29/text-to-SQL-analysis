---
logical_table: RDISCINF
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: "Rule khuyến mãi: điều kiện, đối tượng, thời gian."
column_count: 63
---

# RDISCINF

Rule khuyến mãi: điều kiện, đối tượng, thời gian.

| column | type | description |
|--------|------|-------------|
| IDX | int | ID rule khuyến mãi |
| DISC_CODE | char | Mã chiết khấu |
| CUST_TYPE | char | Cột CUST_TYPE |
| LAYER_ID | int | Cột LAYER_ID |
| ZONE_CODE | char | MãZONE_CODE |
| OBJ_NOT | bit | Cột OBJ_NOT |
| OBJ_CODE | char | MãOBJ_CODE |
| OBJ_VALUE | char | Cột OBJ_VALUE |
| DATA_TYPE | char | Cột DATA_TYPE |
| SOLD_QTY | numeric | Số lượngSOLD_QTY |
| SOLD_AMT | numeric | Số tiềnSOLD_AMT |
| BY_EACH | bit | Cột BY_EACH |
| CHG_TYPE | char | Cột CHG_TYPE |
| CHG_VALUE | numeric | Cột CHG_VALUE |
| BUY_AMT | numeric | Phát sinh mua/tích: BUY_AMT |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| COMP_ID | char | Mã công ty |
| NODE_ID | char | Mã node / chi nhánh hệ thống |
| MAXDISCQTY | numeric | Cột MAXDISCQTY |
| MAXDISCAMT | numeric | Cột MAXDISCAMT |
| MAXDISCTRS | numeric | Cột MAXDISCTRS |
| CARDEXCL | bit | Cột CARDEXCL |
| CARDINCL | bit | Cột CARDINCL |
| CARDRQ | bit | Cột CARDRQ |
| CRD_TYPE | char | Cột CRD_TYPE |
| PREFIX | char | Prefix seri thẻ PM (@P) |
| FR_CARDID | char | Thẻ PM nguồn |
| TO_CARDID | char | Thẻ PM đích |
| CUST_ID | char | Mã khách hàng |
| MARKUP | bit | Cột MARKUP |
| GIFT | bit | Cột GIFT |
| LOTTERY | bit | Cột LOTTERY |
| FR_DATE | datetime | NgàyFR_DATE |
| FR_TIME | numeric | Cột FR_TIME |
| TO_DATE | datetime | NgàyTO_DATE |
| TO_TIME | numeric | Cột TO_TIME |
| DOMMAP | char | Cột DOMMAP |
| DOWMAP | char | Cột DOWMAP |
| IMAGE | varchar | Cột IMAGE |
| VC_PREFIX | char | Cột VC_PREFIX |
| MAXSUMQTY | numeric | Cột MAXSUMQTY |
| MAXSUMAMT | numeric | Cột MAXSUMAMT |
| MAXSUMTRS | numeric | Cột MAXSUMTRS |
| CNTSUMQTY | numeric | Cột CNTSUMQTY |
| CNTSUMAMT | numeric | Cột CNTSUMAMT |
| CNTSUMTRS | numeric | Cột CNTSUMTRS |
| USERDEF1 | nvarchar | Cột USERDEF1 |
| USERDEF2 | nvarchar | Cột USERDEF2 |
| USERDEF3 | nvarchar | Cột USERDEF3 |
| USERDEF4 | nvarchar | Cột USERDEF4 |
| USERDEF5 | nvarchar | Cột USERDEF5 |
| USERDEF6 | nvarchar | Cột USERDEF6 |
| USERDEF7 | nvarchar | Cột USERDEF7 |
| USERDEF8 | nvarchar | Cột USERDEF8 |
| USERDEF9 | nvarchar | Cột USERDEF9 |
| STATUS | bit | Trạng thái active/duyệt |
| WOMMAP | char | Cột WOMMAP |
| DISC_FRB | bit | Cột DISC_FRB |
| RTPR_CODE | char | MãRTPR_CODE |
| SOLD_CNT | numeric | Cột SOLD_CNT |
| GRP_ID | char | Mã nhóm |
| DISC_LMT | numeric | Cột DISC_LMT |
| TRS_AMT | numeric | Số tiềnTRS_AMT |

---
logical_table: SKU_DEF
data_source: db2
temporal_scope: master
temporal_rule: Không phụ thuộc cutoff — danh mục / báo cáo tổng hợp luôn trên db2.
description: Master sản phẩm (SKU), nhóm hàng, đơn vị — chỉ trên db2.
column_count: 84
---

# SKU_DEF

Master sản phẩm (SKU), nhóm hàng, đơn vị — chỉ trên db2.

| column | type | description |
|--------|------|-------------|
| SKU_ID | char | Mã sản phẩm nội bộ |
| SKU_CODE | varchar | Mã SKU hiển thị |
| BARCODE | char | Mã vạch |
| UPC_CODE | char | MãUPC_CODE |
| REF | char | Mã/tham chiếu nội bộ |
| PLU_CODE | varchar | Mã PLU |
| DEPT_ID | char | Cột DEPT_ID |
| GRP_ID | varchar | Mã nhóm |
| GRP_NAME | nvarchar | Cột GRP_NAME |
| MATRIX | char | Cột MATRIX |
| SHORT_NAME | nvarchar | Cột SHORT_NAME |
| FULL_NAME | nvarchar | Cột FULL_NAME |
| MERC_NAME | nvarchar | Cột MERC_NAME |
| GOODS_ID | varchar | Cột GOODS_ID |
| VAR_TYPE | char | Cột VAR_TYPE |
| VAR_ID | varchar | Cột VAR_ID |
| VAR_DESC | nvarchar | Cột VAR_DESC |
| UNIT_DESC | nvarchar | Cột UNIT_DESC |
| PICEUNIT | char | Cột PICEUNIT |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| SUPP_ID | char | Mã nhà cung cấp |
| DISP_GRP | numeric | Cột DISP_GRP |
| BLOCK_CODE | char | MãBLOCK_CODE |
| MIN_MG | numeric | Cột MIN_MG |
| MARGIN | numeric | Cột MARGIN |
| MAX_MG | numeric | Cột MAX_MG |
| BASEPRICE | numeric | Cột BASEPRICE |
| RTPRICE | numeric | Giá bán lẻ |
| WSPRICE | numeric | Cột WSPRICE |
| COSTPRICE | numeric | Cột COSTPRICE |
| PREFPR | numeric | Cột PREFPR |
| LASTIMPPR | numeric | Cột LASTIMPPR |
| MBC | bit | Cột MBC |
| SKU | bit | Cột SKU |
| DMS | numeric | Days of supply |
| CACL_DATE | datetime | NgàyCACL_DATE |
| ATTR_TYPE | char | Cột ATTR_TYPE |
| ITEM_TYPE | char | Loại dòng hàng |
| MERC_TYPE | char | Loại hàng hóa |
| TAX_CODE | char | Mã thuế |
| TAX_RATE | numeric | Thuế suất |
| IMAGE | varchar | Cột IMAGE |
| CO | char | Cột CO |
| TM | char | Cột TM |
| MA | char | Cột MA |
| CL | char | Cột CL |
| SEX | char | Giới tính |
| SS | char | Cột SS |
| BUY_MARK | numeric | Phát sinh mua/tích: BUY_MARK |
| BON_MARK | numeric | Cột BON_MARK |
| DOMESTIC | bit | Cột DOMESTIC |
| EXPIRY | bit | Cột EXPIRY |
| IsOwnBrd | bit | Cột IsOwnBrd |
| IsConsign | bit | Cột IsConsign |
| IsInstall | bit | Cột IsInstall |
| IsSerial | bit | Cột IsSerial |
| IsReserv | bit | Cột IsReserv |
| IsWebshow | bit | Cột IsWebshow |
| RC_TYPE | char | Cột RC_TYPE |
| RC_QTY | numeric | Số lượngRC_QTY |
| LBL_TYPE | char | Cột LBL_TYPE |
| POS_SHW | bit | Cột POS_SHW |
| OPEN_DATE | datetime | Ngày mở / tạo |
| MODI_DATE | datetime | Ngày sửa gần nhất |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| STATUS | char | Trạng thái active/duyệt |
| ABC | varchar | Cột ABC |
| XYZ | varchar | Cột XYZ |
| MDPRICE | numeric | Cột MDPRICE |
| GTYPE_ID | char | Cột GTYPE_ID |
| CLS_ID | char | Cột CLS_ID |
| MRK_ID | char | Cột MRK_ID |
| COMP_ID | char | Mã công ty |
| RES_SHW | bit | Cột RES_SHW |
| IsPack | bit | Cột IsPack |
| DISC_RTPR | numeric | Cột DISC_RTPR |
| DISC_SPPR | numeric | Cột DISC_SPPR |
| DISC_CODE | char | Mã chiết khấu |
| IsTicket | bit | Cột IsTicket |
| FULL_NAME_U | nvarchar | Cột FULL_NAME_U |
| SPCMETHOD | char | Cột SPCMETHOD |
| TAX_DRATE | numeric | Cột TAX_DRATE |

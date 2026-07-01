---
logical_table: SUSPEND
data_source: db2
physical_pattern: SUSPEND
temporal_scope: staging
temporal_rule: Dữ liệu tạm POS — không dùng báo cáo chính thức.
description: Bill treo tại quầy (chưa hoàn tất) — schema gần STRANS.
column_count: 99
---

# SUSPEND

Bill treo tại quầy (chưa hoàn tất) — schema gần STRANS.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| EF_DATE | datetime | Ngày hiệu lực |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| POST | char | Trạng thái post chứng từ |
| RS_CODE | char | Mã lý do (hủy, trả, …) |
| IMPORT | bit | Cờ nhập / import |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| STK_TYPE | char | Loại kho |
| OSTK_ID | char | Kho đích / kho đối ứng |
| OSTK_TYPE | char | Loại kho đối ứng |
| PACK_ID | char | Mã gói đóng |
| PACK_TYPE | char | Cột PACK_TYPE |
| PACK_QTY | numeric | Số lượng gói |
| KIT_ID | char | Mã kit |
| KIT_TYPE | char | Cột KIT_TYPE |
| KIT_QTY | numeric | Số lượng kit |
| ASSO_ID | char | Mã combo/bundle |
| ASSO_QTY | numeric | Số lượng trong combo |
| IDX | numeric | Số thứ tự dòng trong chứng từ |
| SKU_ID | char | Mã sản phẩm nội bộ |
| QTY | numeric | Số lượng |
| STK_QTY | numeric | Số lượng tồn / xuất kho |
| CNT_QTY | numeric | Số lượngCNT_QTY |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| BASE_UNIT | char | Đơn vị cơ sở |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| AMOUNT | numeric | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| SURPLUS | numeric | Phụ phí / surplus |
| VAT_AMT | numeric | Tiền thuế VAT |
| VAT_INCL | bit | Giá đã gồm VAT |
| COMM_AMT | numeric | Tiền hoa hồng |
| COMM_RATE | decimal | Tỷ lệ hoa hồng |
| DISCOUNT | numeric | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| DISC_RATE | numeric | Tỷ lệ chiết khấu |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| CDISC_RATE | numeric | Chiết khấu coupon: CDISC_RATE |
| CDISC_AMT | numeric | Chiết khấu coupon: CDISC_AMT |
| TDISC_CODE | char | Chiết khấu transaction: TDISC_CODE |
| TDISC_RATE | numeric | Chiết khấu transaction: TDISC_RATE |
| TDISC_AMT | numeric | Chiết khấu transaction: TDISC_AMT |
| MDISC_CODE | char | Chiết khấu manual: MDISC_CODE |
| MDISC_AMT | numeric | Chiết khấu manual: MDISC_AMT |
| MDISC_TYPE | char | Chiết khấu manual: MDISC_TYPE |
| GDISC_CODE | char | Chiết khấu gift/khuyến mãi: GDISC_CODE |
| GIFT_SQTY | decimal | Quà tặng: GIFT_SQTY |
| GIFT_QTY | decimal | Quà tặng: GIFT_QTY |
| CCOMM_CODE | char | Hoa hồng coupon: CCOMM_CODE |
| CCOMM_RATE | numeric | Hoa hồng coupon: CCOMM_RATE |
| CCOMM_AMT | numeric | Hoa hồng coupon: CCOMM_AMT |
| TCOMM_CODE | char | Hoa hồng transaction: TCOMM_CODE |
| TCOMM_RATE | numeric | Hoa hồng transaction: TCOMM_RATE |
| TCOMM_AMT | numeric | Hoa hồng transaction: TCOMM_AMT |
| TCOMM_TYPE | char | Hoa hồng transaction: TCOMM_TYPE |
| MCOMM_CODE | char | Hoa hồng manual: MCOMM_CODE |
| MCOMM_AMT | numeric | Hoa hồng manual: MCOMM_AMT |
| MCOMM_TYPE | char | Hoa hồng manual: MCOMM_TYPE |
| GCOMM_CODE | char | Hoa hồng gift: GCOMM_CODE |
| GCOMM_SQTY | numeric | Hoa hồng gift: GCOMM_SQTY |
| GCOMM_QTY | numeric | Hoa hồng gift: GCOMM_QTY |
| TAX_CODE | char | Mã thuế |
| FOREX_RATE | numeric | Tỷ giá ngoại tệ |
| FOREX_CYS | char | Loại tiền ngoại tệ |
| FOREX_AMT | numeric | Số tiền quy đổi ngoại tệ |
| EXPIRY_DT | datetime | Cột EXPIRY_DT |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| CS_ID | char | Cột CS_ID |
| STAFF_ID | char | Mã nhân viên |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| REF | char | Mã/tham chiếu nội bộ |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| UPDATED | bit | Đã cập nhật (bit) |
| MERC_TYPE | char | Loại hàng hóa |
| MBC | bit | Cột MBC |
| SKU | bit | Cột SKU |
| SHIFT | numeric | Ca làm việc |
| STATUS | bit | Trạng thái active/duyệt |
| DTDISC | bit | Cột DTDISC |
| DTDISC_TYPE | char | Cột DTDISC_TYPE |
| DTDISC_RATE | numeric | Tỷ lệDTDISC_RATE |
| DTDISC_AMT | numeric | Số tiềnDTDISC_AMT |
| DMDISC | bit | Cột DMDISC |
| DMDISC_TYPE | char | Cột DMDISC_TYPE |
| DMDISC_RATE | numeric | Tỷ lệDMDISC_RATE |
| DMDISC_AMT | numeric | Số tiềnDMDISC_AMT |
| CDISC_TYPE | char | Chiết khấu coupon: CDISC_TYPE |
| TDISC_TYPE | char | Chiết khấu transaction: TDISC_TYPE |
| TDADD_TYPE | char | Phụ thu transaction: TDADD_TYPE |
| TDADD_RATE | numeric | Phụ thu transaction: TDADD_RATE |
| TDADD_AMT | numeric | Phụ thu transaction: TDADD_AMT |
| MDISC_RATE | numeric | Chiết khấu manual: MDISC_RATE |
| MDADD_TYPE | char | Phụ thu manual: MDADD_TYPE |
| MDADD_RATE | numeric | Phụ thu manual: MDADD_RATE |
| MDADD_AMT | numeric | Phụ thu manual: MDADD_AMT |
| TDADD_CODE | char | Phụ thu transaction: TDADD_CODE |
| MDADD_CODE | char | Phụ thu manual: MDADD_CODE |

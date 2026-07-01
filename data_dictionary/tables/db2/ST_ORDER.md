---
logical_table: ST_ORDER
data_source: db2
temporal_scope: recent
temporal_rule: "TRAN_DATE >= cutoff (~2 tháng: trọn tháng trước + tháng hiện tại đến nay)."
description: Đơn đặt hàng / chuyển kho.
column_count: 117
---

# ST_ORDER

Đơn đặt hàng / chuyển kho.

| column | type | description |
|--------|------|-------------|
| TRANS_NUM | char | Số chứng từ / bill; join header ↔ dòng ↔ thanh toán |
| TRANS_CODE | char | Loại chứng từ — xem domain_definitions.md (113=bán lẻ, 221=thanh toán, 811/812=thẻ, 008=quỹ, …) |
| TRAN_DATE | datetime | Ngày giao dịch (bảng live db2, không shard) |
| TRAN_TIME | char | Giờ giao dịch (HH:MM) |
| EF_DATE | datetime | Ngày hiệu lực |
| DUE_DATE | datetime | Hạn thanh toán / hạn giao |
| DELIVER_DT | datetime | Ngày giao hàng |
| FINISH_DT | datetime | Ngày hoàn tất |
| STOPED_DT | datetime | Cột STOPED_DT |
| BU_ID | char | Đơn vị kinh doanh / chi nhánh logic (00000, 90100, 90200) |
| REF_NO | char | Số tham chiếu chứng từ liên quan |
| REF_DATE | datetime | Ngày tham chiếu |
| REF_TYPE | char | Cột REF_TYPE |
| REF | char | Mã/tham chiếu nội bộ |
| RS_CODE | char | Mã lý do (hủy, trả, …) |
| CS_ID | char | Cột CS_ID |
| STAFF_ID | char | Mã nhân viên |
| CARD_ID | char | Mã thẻ loyalty; prefix A/E/F/H có thể phân hạng |
| CTC_ID | char | Cột CTC_ID |
| PMT_MODE | char | Chế độ thanh toán |
| PMT_TYPE | char | Loại thanh toán |
| PMT_TIME | char | Thời điểm thanh toán |
| CR_TYPE | char | Cột CR_TYPE |
| ORD_WAY | char | Cột ORD_WAY |
| POST | char | Trạng thái post chứng từ |
| UPDATED | bit | Đã cập nhật (bit) |
| ACTION | char | Mã thao tác |
| COPIES | numeric | Cột COPIES |
| SHIFT | numeric | Ca làm việc |
| USER_ID | int | Mã user thao tác |
| WS_ID | int | Mã máy trạm |
| HDR_REMARK | nvarchar | Cột HDR_REMARK |
| STATUS | char | Trạng thái active/duyệt |
| IMPORT | bit | Cờ nhập / import |
| STK_ID | char | Mã cửa hàng / kho (10001, 10004, 10005, …) |
| STK_TYPE | char | Loại kho |
| OSTK_ID | char | Kho đích / kho đối ứng |
| OSTK_TYPE | char | Loại kho đối ứng |
| KIT_ID | char | Mã kit |
| KIT_TYPE | char | Cột KIT_TYPE |
| KIT_QTY | numeric | Số lượng kit |
| IDX | numeric | Số thứ tự dòng trong chứng từ |
| SKU_ID | char | Mã sản phẩm nội bộ |
| UNIT_SYMB | char | Ký hiệu đơn vị (GOI, HOP, KG, …) |
| BASE_UNIT | char | Đơn vị cơ sở |
| UNITCONV | numeric | Hệ số quy đổi đơn vị |
| DMS | numeric | Days of supply |
| SAL_QTY | numeric | Số lượng bán |
| STK_QTY | numeric | Số lượng tồn / xuất kho |
| ORDP_QTY | numeric | Số lượngORDP_QTY |
| ORD_QTY | numeric | Số lượng đặt |
| ORD_PRICE | numeric | Giá đặt hàng |
| DLV_QTY | numeric | Số lượng đã giao |
| ST_QTY | numeric | Số lượngST_QTY |
| QTY | numeric | Số lượng |
| PRICE | decimal | Đơn giá |
| AMOUNT | decimal | Thành tiền / số tiền (ngữ cảnh theo bảng) |
| SURPLUS | decimal | Phụ phí / surplus |
| VAT_AMT | decimal | Tiền thuế VAT |
| VAT_INCL | bit | Giá đã gồm VAT |
| COMM_AMT | decimal | Tiền hoa hồng |
| COMM_RATE | decimal | Tỷ lệ hoa hồng |
| DISCOUNT | decimal | Giảm giá (số tiền hoặc % tùy ngữ cảnh) |
| DISC_RATE | decimal | Tỷ lệ chiết khấu |
| CDISC_CODE | char | Chiết khấu coupon: CDISC_CODE |
| CDISC_RATE | decimal | Chiết khấu coupon: CDISC_RATE |
| CDISC_AMT | numeric | Chiết khấu coupon: CDISC_AMT |
| TDISC_CODE | char | Chiết khấu transaction: TDISC_CODE |
| TDISC_RATE | decimal | Chiết khấu transaction: TDISC_RATE |
| TDISC_AMT | numeric | Chiết khấu transaction: TDISC_AMT |
| MDISC_CODE | char | Chiết khấu manual: MDISC_CODE |
| MDISC_AMT | numeric | Chiết khấu manual: MDISC_AMT |
| MDISC_TYPE | char | Chiết khấu manual: MDISC_TYPE |
| GDISC_CODE | char | Chiết khấu gift/khuyến mãi: GDISC_CODE |
| GDISC_TYPE | char | Chiết khấu gift/khuyến mãi: GDISC_TYPE |
| GDISC_AMT | numeric | Chiết khấu gift/khuyến mãi: GDISC_AMT |
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
| GCOMM_TYPE | char | Hoa hồng gift: GCOMM_TYPE |
| GCOMM_AMT | numeric | Hoa hồng gift: GCOMM_AMT |
| GCOMM_SQTY | numeric | Hoa hồng gift: GCOMM_SQTY |
| GCOMM_QTY | numeric | Hoa hồng gift: GCOMM_QTY |
| TAX_CODE | char | Mã thuế |
| MERC_TYPE | char | Loại hàng hóa |
| ITEM_TYPE | char | Loại dòng hàng |
| FOREX_RATE | numeric | Tỷ giá ngoại tệ |
| FOREX_CYS | char | Loại tiền ngoại tệ |
| FOREX_AMT | numeric | Số tiền quy đổi ngoại tệ |
| EXPIRY_DT | datetime | Cột EXPIRY_DT |
| WARR_TM | char | Cột WARR_TM |
| REMARK | nvarchar | Ghi chú nghiệp vụ |
| SUPP_ID | char | Mã nhà cung cấp |
| CUST_ID | char | Mã khách hàng |
| COSTPRICE | numeric | Cột COSTPRICE |
| RTPRICE | numeric | Giá bán lẻ |
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

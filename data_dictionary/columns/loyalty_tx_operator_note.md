---
semantic_key: loyalty_tx_operator_note
title: Ghi chú thủ công trên giao dịch thẻ (REMARK)
display_names:
- REMARK
kind: text
tables:
- ref: db1:crdtrans_arc
  column: REMARK
  type: nvarchar
- ref: db2:crdtrans
  column: REMARK
  type: nvarchar
join_with: []
related_semantic_keys: []
facts:
- Ghi chú nghiệp vụ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.REMARK: top=tÆng 02 thÎ 50k(1), t¨ng 9 ®iÓm cho gd be221....6538
  ngµy 24.01.24(1), chuyÓn ®iÓm tõ thÎ A65818(1), gi¶m 350 ®iÓm = 04 thÎ 50k(1), tÆng
  03 thÎ 100k=450®(1)'
- 'db2:crdtrans.REMARK: top=tÆng 04 thÎ 100k=400®(2), 150diem=3 the(1), nh©n 3 ®iÓm
  ch­êng tr×nh xanh bill br221...6199(1), chuyÓn ®iÓm qua thÎ E4338(1), gi¶m 906 ®iÓm
  = 15 thÎ 50k(1)'
---

# Ghi chú thủ công trên giao dịch thẻ (REMARK)

**Semantic key:** `loyalty_tx_operator_note` · **Cột vật lý:** `REMARK`

## Ý nghĩa nghiệp vụ

REMARK do nhân viên nhập tay khi điều chỉnh thẻ — giải thích lý do trừ/cộng điểm, đổi quà, tích nhầm mã thẻ. Sample: 'tich nham ma the', 'giam 100 diem = 01 the 100k'.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `REMARK` | nvarchar | Ghi chú NV nhập tay |
| `db2:crdtrans` | `REMARK` | nvarchar | Ghi chú NV nhập tay |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:crdtrans_arc.REMARK`
- Null rate trong sample: 5%
- Distinct ≈18; top: `giam 100 diem = 01 the 100k`×2, `tang 02 the 50k=100d`×1, `tich nham ma the`×1, `chuyÓn ®iÓm qua thÎ E4205`×1, `tang 01 the 100k=100d`×1, `gi?m 200 diem = 02 th? 200k`×1, `gi?m 400 = 04 the 100k`×1, `giam 100 diem = 01 the 100`×1

### `db2:crdtrans.REMARK`
- Null rate trong sample: 0%
- Distinct ≈20; top: `ChuyÓn ®iÓm tõ thÎ A67634`×1, `kÝch ho¹t thÎ cho kh¸ch bill br221.122`×1, `kÝch ho¹t thÎ cho kh¸ch bill bq221..255`×1, `kÝch ho¹t thÎ cho kh¸ch bill br221...523`×1, `ChuyÓn ®iÓm tõ thÎ H1366`×1, `ChuyÓn ®iÓm tõ thÎ A69118`×1, `ChuyÓn ®iÓm tõ thÎ A70699`×1, `ChuyÓn ®iÓm tõ thÎ A74394`×1

## Ghi chú thêm

- Ghi chú nghiệp vụ

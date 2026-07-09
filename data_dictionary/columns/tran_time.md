---
semantic_key: tran_time
title: tran time
display_names:
- TRAN_TIME
kind: date
tables:
- ref: db1:crdtrans_arc
  column: TRAN_TIME
  type: char
- ref: db1:pmtrans
  column: TRAN_TIME
  type: char
- ref: db1:strans
  column: TRAN_TIME
  type: char
- ref: db1:transhdr_arc
  column: TRAN_TIME
  type: char
- ref: db2:crdtrans
  column: TRAN_TIME
  type: char
- ref: db2:crdtrans_tmp
  column: TRAN_TIME
  type: char
- ref: db2:ctrans
  column: TRAN_TIME
  type: char
- ref: db2:pmcrdiss
  column: TRAN_TIME
  type: char
- ref: db2:pmcrdstk
  column: TRAN_TIME
  type: char
- ref: db2:pmtrans
  column: TRAN_TIME
  type: char
- ref: db2:st_order
  column: TRAN_TIME
  type: char
- ref: db2:strans
  column: TRAN_TIME
  type: char
- ref: db2:strans_tmp
  column: TRAN_TIME
  type: char
- ref: db2:suspend
  column: TRAN_TIME
  type: char
- ref: db2:transhdr
  column: TRAN_TIME
  type: char
join_with: []
related_semantic_keys: []
facts:
- Giờ giao dịch (HH:MM)
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.TRAN_TIME: top=17:42(7), 17:35(6), 17:37(6), 18:15(5), 11:17(5)'
- 'db1:pmtrans.TRAN_TIME: top=17:18(9), 17:31(7), 09:37(6), 18:01(6), 19:16(6)'
- 'db1:strans.TRAN_TIME: top=22:22(32), 21:48(31), 00:00(26), 22:42(18), 22:16(14)'
- 'db1:transhdr_arc.TRAN_TIME: top=09:16(7), 17:20(6), 10:27(6), 17:49(5), 09:55(5)'
- 'db2:crdtrans.TRAN_TIME: top=17:49(7), 18:06(7), 10:23(6), 09:45(6), 09:08(6)'
- 'db2:crdtrans_tmp.TRAN_TIME: top=17:59(7), 09:20(7), 17:50(6), 15:26(5), 17:00(5)'
- 'db2:ctrans.TRAN_TIME: top=11:52(8), 16:54(8), 16:42(7), 11:06(7), 11:54(7)'
- 'db2:pmcrdiss.TRAN_TIME: top=15:10(8), 09:23(8), 10:42(8), 09:34(8), 10:56(7)'
- 'db2:pmcrdstk.TRAN_TIME: top=09:55(8), 10:13(8), 10:18(7), 10:03(6), 15:33(6)'
- 'db2:pmtrans.TRAN_TIME: top=10:15(8), 17:33(6), 18:47(6), 19:41(6), 16:36(5)'
- 'db2:st_order.TRAN_TIME: top=16:23(124), 20:40(84), 20:48(52), 20:22(51), 20:41(47)'
- 'db2:strans.TRAN_TIME: top=05:15(46), 05:16(15), 10:09(6), 11:52(6), 11:27(6)'
- 'db2:strans_tmp.TRAN_TIME: top=17:46(8), 17:07(6), 16:46(5), 17:40(5), 18:08(5)'
- 'db2:suspend.TRAN_TIME: top=12:00(7), 16:56(7), 10:07(7), 19:14(6), 17:58(6)'
- 'db2:transhdr.TRAN_TIME: top=11:10(6), 14:31(5), 17:39(5), 10:53(5), 16:58(5)'
---

# tran time

**Semantic key:** `tran_time` · **Cột vật lý:** `TRAN_TIME`

## Ý nghĩa nghiệp vụ

Cột TRAN_TIME trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db1:pmtrans: top 08:49, 08:50, 08:39; db1:strans: top 16:16, 17:48, 12:02; db1:transhdr_arc: top 17:03, 17:07, 17:08; db2:crdtrans_tmp: top 14:32, 15:07, 15:09; db2:ctrans: top 11:08, 12:09, 16:16; db2:pmcrdiss: top 09:16, 09:20, 09:31; db2:pmcrdstk: top 09:42; db2:pmtrans: top 11:51, 11:53, 21:42; db2:st_order: top 15:30, 20:31; db2:strans: top 16:27, 16:16, 12:09; db2:strans_tmp: top 17:35, 11:30, 11:34; db2:suspend: top 11:08, 11:28; db2:transhdr: top 11:08, 12:09, 16:16.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `TRAN_TIME` | char | có dữ liệu |
| `db1:pmtrans` | `TRAN_TIME` | char | có dữ liệu |
| `db1:strans` | `TRAN_TIME` | char | có dữ liệu |
| `db1:transhdr_arc` | `TRAN_TIME` | char | có dữ liệu |
| `db2:crdtrans` | `TRAN_TIME` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `TRAN_TIME` | char | có dữ liệu |
| `db2:ctrans` | `TRAN_TIME` | char | có dữ liệu |
| `db2:pmcrdiss` | `TRAN_TIME` | char | có dữ liệu |
| `db2:pmcrdstk` | `TRAN_TIME` | char | có dữ liệu |
| `db2:pmtrans` | `TRAN_TIME` | char | có dữ liệu |
| `db2:st_order` | `TRAN_TIME` | char | có dữ liệu |
| `db2:strans` | `TRAN_TIME` | char | có dữ liệu |
| `db2:strans_tmp` | `TRAN_TIME` | char | có dữ liệu |
| `db2:suspend` | `TRAN_TIME` | char | có dữ liệu |
| `db2:transhdr` | `TRAN_TIME` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db1:pmtrans.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈10; top: `08:49`×3, `08:50`×3, `08:39`×2, `08:46`×2, `08:48`×2, `08:51`×2, `08:52`×2, `08:58`×2

### `db1:strans.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈4; top: `16:16`×10, `17:48`×5, `12:02`×4, `11:55`×1

### `db1:transhdr_arc.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `17:03`×1, `17:07`×1, `17:08`×1, `17:37`×1, `17:42`×1, `17:43`×1, `17:55`×1, `17:56`×1

### `db2:crdtrans_tmp.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `14:32`×1, `15:07`×1, `15:09`×1, `15:21`×1, `15:42`×1, `15:51`×1, `15:54`×1, `15:57`×1

### `db2:ctrans.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `11:08`×1, `12:09`×1, `16:16`×1, `16:27`×1, `11:16`×1, `15:30`×1, `16:20`×1, `16:21`×1

### `db2:pmcrdiss.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈17; top: `09:16`×2, `09:20`×2, `09:31`×2, `16:58`×1, `09:10`×1, `09:11`×1, `09:12`×1, `09:14`×1

### `db2:pmcrdstk.TRAN_TIME`
- Null rate trong sample: 35%
- Distinct ≈1; top: `09:42`×13

### `db2:pmtrans.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈18; top: `11:51`×2, `11:53`×2, `21:42`×1, `21:31`×1, `21:39`×1, `11:44`×1, `11:45`×1, `11:47`×1

### `db2:st_order.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈2; top: `15:30`×17, `20:31`×3

### `db2:strans.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈4; top: `16:27`×8, `16:16`×7, `12:09`×4, `11:08`×1

### `db2:strans_tmp.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈6; top: `17:35`×7, `11:30`×5, `11:34`×3, `08:50`×2, `11:32`×2, `11:26`×1

### `db2:suspend.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈2; top: `11:08`×13, `11:28`×7

### `db2:transhdr.TRAN_TIME`
- Null rate trong sample: 0%
- Distinct ≈20; top: `11:08`×1, `12:09`×1, `16:16`×1, `16:27`×1, `11:16`×1, `12:16`×1, `15:43`×1, `15:36`×1

## Ghi chú thêm

- Giờ giao dịch (HH:MM)

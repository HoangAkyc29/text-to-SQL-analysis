---
semantic_key: ref
title: ref
display_names:
- REF
kind: text
tables:
- ref: db1:crdtrans_arc
  column: REF
  type: char
- ref: db1:strans
  column: REF
  type: char
- ref: db2:crdtrans
  column: REF
  type: char
- ref: db2:crdtrans_tmp
  column: REF
  type: char
- ref: db2:st_order
  column: REF
  type: char
- ref: db2:strans_tmp
  column: REF
  type: char
- ref: db2:transhdr
  column: REF
  type: char
join_with: []
related_semantic_keys: []
facts:
- Mã/tham chiếu nội bộ
sources:
- table_md
- samples_top20
- column_semantic_registry
evidence:
- 'db1:crdtrans_arc.REF: top=Jan -000B52211701005231(1), Dec -000B52211812000723(1),
  Dec -000B52211912001731(1), Mar -000A12211603009896(1), 9387-000BQ2212509004387(1)'
- 'db1:strans.REF: top=0000-000(1)'
- 'db2:crdtrans.REF: top=9664-000BR2212606003714(1), 9679-901AY2212607000170(1), 9677-000BE2212606009610(1),
  9683-000BE2212607001694(1), 9653-000BR2212606001184(1)'
- 'db2:crdtrans_tmp.REF: top=9038-000AV2212409009730(1), 8832-000BE2212403001864(1),
  9062-000BE2212410006086(1), 8835-901AX2212403002158(1), 8926-000AP2212406001609(1)'
- 'db2:st_order.REF: top=9667-000003102606000108(77), 9667-000003102606000107(49),
  9650-000003102606000017(37), 9669-000003102606000121(33), 9663-000003102606000084(30)'
- 'db2:strans_tmp.REF: top=8892-000BE2212405001691(1)'
- 'db2:transhdr.REF: top=9642-000BQ2212605008910(1), 9653-902BM2212606001503(1)'
---

# ref

**Semantic key:** `ref` · **Cột vật lý:** `REF`

## Ý nghĩa nghiệp vụ

Cột REF trên CRDTRANS, CRDTRANS_ARC, CRDTRANS_TMP. db2:crdtrans_tmp: top 8766-000AB2212401000001, 8766-000AB2212401000004, 8766-000AB2212401000005; db2:st_order: top 9648-000003102606000005, 9648-000003102606000007.

## Bảng & vai trò

| Bảng | Cột | Kiểu | Vai trò / sample |
|------|-----|------|------------------|
| `db1:crdtrans_arc` | `REF` | char | có dữ liệu |
| `db1:strans` | `REF` | char | có dữ liệu |
| `db2:crdtrans` | `REF` | char | có dữ liệu |
| `db2:crdtrans_tmp` | `REF` | char | có dữ liệu |
| `db2:st_order` | `REF` | char | có dữ liệu |
| `db2:strans_tmp` | `REF` | char | có dữ liệu |
| `db2:transhdr` | `REF` | char | có dữ liệu |

## Quan sát từ sample (TOP 20 db2/db1)

### `db2:crdtrans_tmp.REF`
- Null rate trong sample: 0%
- Distinct ≈20; top: `8766-000AB2212401000001`×1, `8766-000AB2212401000004`×1, `8766-000AB2212401000005`×1, `8766-000AB2212401000008`×1, `8766-000AB2212401000014`×1, `8766-000AB2212401000018`×1, `8766-000AB2212401000021`×1, `8766-000AB2212401000022`×1

### `db2:st_order.REF`
- Null rate trong sample: 0%
- Distinct ≈2; top: `9648-000003102606000005`×17, `9648-000003102606000007`×3

## Ghi chú thêm

- Mã/tham chiếu nội bộ

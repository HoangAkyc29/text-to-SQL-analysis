---
logical_table: WebRpt_rfm_snapshot
data_source: db2
temporal_scope: report
temporal_rule: Báo cáo tổng hợp trên db2 — lọc theo report_date / snapshot_date.
description: Snapshot RFM loyalty theo thẻ/khách.
column_count: 10
---

# WebRpt_rfm_snapshot

Snapshot RFM loyalty theo thẻ/khách.

| column | type | description |
|--------|------|-------------|
| snapshot_date | date | Ngày snapshot |
| card_id | varchar | Mã thẻ |
| cust_id | varchar | Mã khách |
| card_type | varchar | Loại thẻ |
| recency_days | int | Số ngày từ lần mua gần nhất |
| frequency | int | Tần suất mua |
| monetary | decimal | Tổng chi tiêu |
| rfm_segment | varchar | Phân khúc RFM: At Risk, Loyal, Others |
| rfm_score | tinyint | Điểm RFM |
| refreshed_at | datetime | Thời điểm làm mới báo cáo |

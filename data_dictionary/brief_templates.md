# Brief templates

Mẫu intent/metric/dimension cho Agent I khi tạo `AnalysisBrief`.

## VIP monthly chart
- intent: VIP customers with monthly spend chart
- filters: card_prefix, trans_codes, date_range
- metrics: [revenue, points]
- dimensions: [time, card_tier]
- output_format: [chart, excel]

## Store revenue ranking
- intent: Top stores by retail revenue in period
- filters: date_range, store_ids
- metrics: [revenue]
- dimensions: [store]
- output_format: [table, excel]

## Product sales lookup
- intent: Revenue for a product code or barcode
- filters: product_code, date_range, lookup_mode
- metrics: [revenue, quantity]
- dimensions: [product]
- output_format: [table]

## Points accrual trend
- intent: Loyalty points earned over time
- filters: date_range, card_prefix
- metrics: [points]
- dimensions: [time]
- output_format: [chart]

## Payment mix VIP
- intent: VIP payment methods breakdown
- filters: date_range, trans_codes
- metrics: [revenue]
- dimensions: [payment_type]
- output_format: [chart, table]

## Cross-store comparison
- intent: Compare KPI across stores
- filters: date_range, store_ids
- metrics: [revenue, transactions]
- dimensions: [store, time]
- output_format: [chart, excel]

## Inventory movement (recent)
- intent: Stock movement for SKU in recent window
- filters: sku, date_range
- metrics: [quantity]
- dimensions: [time, store]
- output_format: [table]

## Promotion effectiveness
- intent: Sales uplift during promotion period
- filters: promo_id, date_range
- metrics: [revenue, quantity]
- dimensions: [time, product]
- output_format: [chart]

## Customer segment drill-down
- intent: Segment customers by spend tier
- filters: date_range, card_prefix
- metrics: [revenue, customer_count]
- dimensions: [segment]
- output_format: [table, chart]

## Daily sales dashboard
- intent: Daily revenue and transaction count
- filters: date_range
- metrics: [revenue, transactions]
- dimensions: [time]
- output_format: [chart, excel]

## Category performance
- intent: Revenue by product category
- filters: date_range, category_ids
- metrics: [revenue]
- dimensions: [category]
- output_format: [table, chart]

## Hour-of-day pattern
- intent: Sales pattern by hour
- filters: date_range, store_ids
- metrics: [revenue, transactions]
- dimensions: [hour]
- output_format: [chart]

## New vs returning (proxy)
- intent: Compare first-time vs repeat card activity
- filters: date_range
- metrics: [transactions, revenue]
- dimensions: [customer_type]
- output_format: [table]

## Data quality probe
- intent: Explore unknown product or empty result
- filters: product_code
- exploration_mode: true
- user_knowledge_level: unknown
- output_format: [table]

## Executive summary export
- intent: KPI summary for leadership
- filters: date_range
- metrics: [revenue, transactions, points]
- dimensions: [time]
- output_format: [excel, chart]

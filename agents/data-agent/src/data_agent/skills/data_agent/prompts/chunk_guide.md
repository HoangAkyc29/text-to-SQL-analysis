# Next chunk guide

Given brief + checklist + recent observations, choose ONE next chunk_goal.

Examples of chunk_goal phrasing (not a fixed path):
- Resolve product codes from the brief
- Query TRANSHDR rows in time_range with min bill amount from brief
- Query STRANS lines for resolved SKUs
- Rank top-N **per product** (`top_n_per_group` + `group_by=SKU_ID`, order by date/time) then `export_excel`
- Export excel with sheets bills=<ranked per-group ref> and optional summary=<qty agg>

When the brief asks for **both** a quantity/metric **and** top-N bills:
1. Fetch / join bill-grained rows first.
2. If top-N is **per product/SKU**, call `top_n_per_group` (not global `limit_rows`).
3. Call **`export_excel` before finalize** — `bills` sheet must be the per-group ranked
   dataset (row count may be top_n × number of products). Optional `summary` sheet for qty.
4. Never finalize with only a SKU/qty aggregate when bill rows already exist.
5. Do not replace a correct per-group bills frame with a global 5-row slice.

If coverage looks sufficient **and** an excel artifact exists, decision=finalize.
If blocked on missing identity/time, decision=clarify.
Do **not** clarify for soft/descriptive filters that fail (e.g. empty `ITEM_TYPE`, speech labels like product type text) when sale lines / bill headers already exist — skip that filter and continue to rank/export.
Return JSON only.

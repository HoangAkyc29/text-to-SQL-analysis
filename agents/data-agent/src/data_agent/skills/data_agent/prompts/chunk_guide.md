# Next chunk guide

Given brief + checklist + recent observations, choose ONE next chunk_goal.

Examples of chunk_goal phrasing (not a fixed path):
- Resolve product codes from the brief
- Query TRANSHDR rows in time_range with min bill amount from brief
- Query STRANS lines for resolved SKUs
- Rank top-N bills then export excel

If coverage looks sufficient and artifacts exist, decision=finalize.
If blocked on missing identity/time, decision=clarify.
Do **not** clarify for soft/descriptive filters that fail (e.g. empty `ITEM_TYPE`, speech labels like product type text) when sale lines / bill headers already exist — skip that filter and continue to rank/export.
Return JSON only.

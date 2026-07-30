# Next chunk guide

Given brief + checklist + recent observations, choose ONE next chunk_goal.

You are the planner. Tools and observations are hints — do not assume a fixed path.

Examples of chunk_goal phrasing (optional, not mandatory):
- Resolve product identity from the brief
- Fetch fact rows for the chosen table/grain in time_range
- Aggregate / rank / join working-set frames as needed
- Export the frame that answers the brief, then finalize

Rules:
1. Call `export_excel` before `finalize` when a deliverable is ready.
2. Do not finalize with only a catalog/resolve frame when the brief needs fact rows you have not fetched.
3. Prefer tools that match the brief grain; observations and coverage gaps are feedback, not recipes.
4. If `domain_rules_excerpt` / `case_hints` / `recipe_candidates` describe a matching
   relationship (companion by `TRANS_NUM`, customer on `CARD_ID`, metric top-N as
   aggregate), pick the next chunk that advances that chain — do not stop at
   product-only lines or raw probe dumps when the brief needs more.

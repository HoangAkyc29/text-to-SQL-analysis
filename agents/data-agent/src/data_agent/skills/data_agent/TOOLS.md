# Data Agent tools

Tools are accessed via Tool-Selector suggestions, then executed through MCP servers
(`product-lookup`, `data-query`, `dataframe-ops`, `deliverables`) or the in-process
bridge that mirrors those parameterized handlers.

Native only: trivial helpers such as current time (if added). Do not call sql-gateway tools directly.

## Grounding (meta — not SQL)

- When `domain_rules_excerpt` or retrieved `case_hints` / `recipe_candidates` are
  present, prefer their **parameterized** `tool_chain` steps (fill placeholders
  from the brief). Do not invent SQL; do not ignore a matching chain for a
  home-grown path that skips companion expand or ranking.
- Grain / join roles: `data_dictionary/analysis_grain.yaml` (`join_keys`) and
  `domain_definitions.md` — companion lines share `TRANS_NUM`; customer profile
  joins on `CARD_ID`; product metric top-N is an **aggregate** frame, not a raw
  line dump.

## Ranking & export (meta)

- **`resolve_products`**: `codes=` for exact SKU_CODE; `name_contains=` (aliases:
  `product_name` / `product_keyword`) for case-insensitive substring on
  `SKU_DEF.FULL_NAME_U`. Do not put a display name into `codes`.
- **`join_datasets`**: overlapping columns become `*_hdr` / `*_line` (or `*_x`/`*_y`).
  Bill totals after header⋈line → use `AMOUNT_hdr` / `AMOUNT_x`, never ask the user
  which AMOUNT. If TRANSHDR was already queried with `min_amount`, skip re-filtering AMOUNT.
  Customer/profile joins: `left_on`/`right_on` = `CARD_ID` when that key is on both sides.
- **`top_n_per_group`**: use when the brief asks for top-N **per** product/SKU/group.
  Pass `group_by`/`partition_by` (e.g. `SKU_ID`) and `order_by` time columns for
  “nearest/most recent”. Do **not** use a global `limit_rows(N)` for per-group asks.
  Empty `partition_by` means global top-N only. For global SKU ranking by revenue/qty,
  aggregate (or `aggregate_rows`) first, then top-N — do not export the probe dump.
- **`tcvn3_converter`** (alias `TCVN3_converter`): decode TCVN3/legacy Vietnamese
  text columns to Unicode before export when names/remarks look mojibaked.
  Pass `columns=` or omit to convert all string columns. Columns ending in `_U`
  are already Unicode and are never converted.
- **`export_excel`**: call **before** `finalize` on the frame you chose.
  Optional multi-sheet maps are allowed when you name distinct existing refs.
  Do not re-slice a correct per-group ranked dataset to N global rows.

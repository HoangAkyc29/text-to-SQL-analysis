# Data Agent tools

Tools are accessed via Tool-Selector suggestions, then executed through MCP servers
(`product-lookup`, `data-query`, `dataframe-ops`, `deliverables`) or the in-process
bridge that mirrors those parameterized handlers.

Native only: trivial helpers such as current time (if added). Do not call sql-gateway tools directly.

## Ranking & export (meta)

- **`resolve_products`**: `codes=` for exact SKU_CODE; `name_contains=` (aliases:
  `product_name` / `product_keyword`) for case-insensitive substring on
  `SKU_DEF.FULL_NAME_U`. Do not put a display name into `codes`.
- **`join_datasets`**: overlapping columns become `*_hdr` / `*_line` (or `*_x`/`*_y`).
  Bill totals after header⋈line → use `AMOUNT_hdr` / `AMOUNT_x`, never ask the user
  which AMOUNT. If TRANSHDR was already queried with `min_amount`, skip re-filtering AMOUNT.
- **`top_n_per_group`**: use when the brief asks for top-N **per** product/SKU/group.
  Pass `group_by`/`partition_by` (e.g. `SKU_ID`) and `order_by` time columns for
  “nearest/most recent”. Do **not** use a global `limit_rows(N)` for per-group asks.
  Empty `partition_by` means global top-N only.
- **`tcvn3_converter`** (alias `TCVN3_converter`): decode TCVN3/legacy Vietnamese
  text columns to Unicode before export when names/remarks look mojibaked.
  Pass `columns=` or omit to convert all string columns.
- **`export_excel`**: call **before** `finalize`. Prefer multi-sheet:
  `sheets={"bills": "<top_n_per_group dataset>", "summary": "<qty aggregate>"}`.
  Export the per-group ranked dataset as `bills` — do not re-slice it to N global rows.

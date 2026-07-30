# Select tools for one chunk

Input state includes `chunk_goal`, `brief_slice`, `available_datasets`, `prior_observations_summary`, `case_hints`, and `tool_catalog`.

Return:

```json
{
  "tools": [
    {
      "server": "product-lookup|data-query|dataframe-ops|deliverables",
      "tool_id": "...",
      "reason": "why this tool for this chunk",
      "args_hints": {
        "table": "STRANS",
        "save_as": "sale_lines"
      }
    }
  ],
  "none_available": false,
  "reason": null
}
```

## case_hints

- When `case_hints` include a `tool_chain` whose goal matches `chunk_goal`, suggest
  the next tool(s) from that chain (same `server`/`tool_id`, structural
  `args_hints` only). Do not paste SQL; Data Agent binds brief values / dataset refs.
- Typical structural patterns in hints: companion expand = second `query_rows` by
  `trans_nums` without `sku_ids`; customer = `CSCARD`/`join_datasets` on `CARD_ID`;
  metric ranking = `aggregate_rows` / groupby then `top_n_per_group`, not raw dump export.

## args_hints rules

- Prefer **structural** hints only: `table`, `save_as`, `column`, `group_by`, `aggs`, numeric `limit`.
- Do **not** put prose placeholders or brief paths in args_hints (e.g. `"time_range": "brief_slice.time_range"`, `"min_amount": "brief_slice.filters.min_bill_value"`, `"filters": "SKU_ID from resolve_products dataset"`).
- Do **not** invent filter values, column aliases (`BILL_AMT`), or SQL predicates. Data Agent fills `time_range`, product codes, bill thresholds (`AMOUNT` via checklist), and dataset refs from the brief / working set.
- If you must hint a filter, use a typed list of objects: `{"column":"STK_ID","op":"eq","value":"01"}` with concrete values only.
- Rank at most 5 tools. Prefer flexible `query_rows` over narrow legacy fetch names.

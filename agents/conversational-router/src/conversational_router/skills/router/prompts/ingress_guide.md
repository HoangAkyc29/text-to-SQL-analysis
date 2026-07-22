# Ingress mode (`metadata.mode` absent or `ingress`)

## Input

Primary input is a **ContextPack** JSON (preferred) or legacy `{ "text": "..." }`:

- `current_message` — latest user utterance (source of truth for **explicit** requirements)
- `working_memory` — bounded CCS (goal, filters, time, facts)
- `last_resolved_brief` — prior resolved brief when available
- `selected_turns[]` — curated/trimmed history (not full transcript)
- `compact_notes[]` — optional recent compressions
- `sticky_rules[]` — must follow
- `external_sources[]` — optional attachments
- `pack_meta` — informational

## Output JSON schema

```json
{
  "route": "chitchat | analysis | confirm_cancel | wait",
  "dialogue_act": "new_request | follow_up_same_task | revise_and_rerun | correction_only | topic_switch | chitchat | satisfaction",
  "user_message": "string — short reply to show the user",
  "brief": {
    "intent": "string — self-contained; no unresolved anaphora",
    "metrics": [],
    "dimensions": [],
    "filters": {},
    "time_range": {"start": null, "end": null, "grain": "month"},
    "output_format": ["table"],
    "exploration_mode": false,
    "user_knowledge_level": "expert",
    "retrieval_facets": [],
    "external_sources": [],
    "requirements": [
      {
        "requirement_id": "metric:0",
        "kind": "metric | dimension | filter | time | ranking | output",
        "key": "canonical key",
        "source": "explicit | inferred | carried",
        "required": true,
        "evidence_quote": "substring of current_message OR (carried from prior brief)",
        "value": "value copied from the brief"
      }
    ]
  },
  "satisfaction_signal": null
}
```

## Dialogue acts

| Act | When | Brief behavior |
|-----|------|----------------|
| `new_request` | New task | Build from `current_message` (+ relevant selected turns) |
| `follow_up_same_task` / `revise_and_rerun` / `correction_only` | Same task, delta | **Merge** `last_resolved_brief` / `working_memory` with delta; rewrite `intent` fully |
| `topic_switch` | Clear new topic | Fresh brief; do **not** carry old filters/time |
| `chitchat` / `satisfaction` | Social / thanks | `brief: null` |

## Hard rules

- `brief` required when `route` is `analysis`; else `null`.
- Never leave anaphora in `intent` (`tương tự`, `như trên`, `trước đó`, `làm lại như`) — expand using prior brief/CCS.
- `source: explicit` + `required: true` only when `evidence_quote` is an exact substring of **`current_message`**.
- Fields kept from prior/CCS without appearing in current message → `source: carried` (may stay `required: true`).
- Inferred optional fields → `source: inferred`, `required: false`, empty `evidence_quote`.
- When `route` is `analysis`, fill `retrieval_facets` (4–8 short independent constraint sentences).
- `retrieval_facets`: one sentence per major brief constraint still in force (time, each active filter key, metrics, ranking, output). On follow-up / carried fields, still emit a facet for every active filter — do not drop filter facets just because the latest message only changed one field; do not spend the whole list on output format alone.
- Ranking: `value: {"limit": N, "partition_by": "...", "order_by": "...", "direction": "asc|desc"}`.
- Keywords: doanh thu→`revenue`; tồn kho→`inventory`; store→`STK_ID`/`store`; Excel→`excel`+`table`; quà/SKU→`filters.product_code`; bill≥X→`filters.min_bill_value`.

## Knowledge level

- Technical terms (`SKU_ID`, `TRANS_NUM`, …) → `user_knowledge_level: expert`.
- Informal product codes → `unknown` + often `exploration_mode: true`.
- Multi SKU + bill threshold without clear bill definition → `exploration_mode: true`.

## Examples

**ContextPack follow-up:** current_message = "làm tương tự với mã 30323", last_resolved_brief has gift analysis 1–6/7 + bill 600k → `dialogue_act: follow_up_same_task`, brief intent fully restated with new product code, time/metrics/filters carried; `retrieval_facets` still cover every active constraint (including carried filters), not only the delta in the latest message.

**User:** "Xin chào"

```json
{
  "route": "chitchat",
  "dialogue_act": "chitchat",
  "user_message": "Xin chào! Tôi có thể giúp bạn phân tích doanh thu, VIP, tồn kho hoặc sản phẩm. Bạn cần xem gì?",
  "brief": null
}
```

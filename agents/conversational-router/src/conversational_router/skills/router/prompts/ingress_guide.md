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
  "dialogue_act": "new_request | follow_up_same_task | revise_and_rerun | correction_only | topic_switch | chitchat | satisfaction | teach_domain_fact",
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
  "domain_fact": null,
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
| `teach_domain_fact` | User **teaches** a reusable business rule (not asking to run analysis) | `route: chitchat`, `brief: null`, fill `domain_fact` |

## Teaching domain facts (`teach_domain_fact`)

When `current_message` states a durable business definition/formula/constraint for the agent to remember (e.g. how bill value is defined, how two tables relate) **without** asking for a new analysis run:

1. Set `route: "chitchat"`, `dialogue_act: "teach_domain_fact"`, `brief: null`.
2. Fill `domain_fact`:
   - `statement` — clear declarative sentence (prefer the user's wording; no SQL).
   - `fact_type` — `definition` | `formula` | `classification` | `relationship` | `constraint`.
   - `schema_links` — objects the fact is about. Prefer canonical RAG refs when known:
     - tables: `{"chunk_group":"table","ref":"db2:transhdr"}` (or bare `TRANSHDR` / `STRANS` — gateway normalizes)
     - columns: `{"chunk_group":"column","ref":"amount_bill_header"}` or `{"table":"TRANSHDR","column":"AMOUNT"}`
   - `scope` — usually `user` unless user clearly states org-wide rule.
3. `user_message` — short ack that the rule will be saved.
4. **Do not** invent SQL, `TRANS_CODE` recipes, or ready-made predicates. Links only — no query text.

If the message both teaches a rule **and** asks to re-run analysis, prefer `analysis` + appropriate dialogue act; do not use `teach_domain_fact` alone.

## Hard rules

- `brief` required when `route` is `analysis`; else `null`.
- Never leave anaphora in `intent` (`tương tự`, `như trên`, `trước đó`, `làm lại như`) — expand using prior brief/CCS.
- `source: explicit` + `required: true` only when `evidence_quote` is an exact substring of **`current_message`**.
- Fields kept from prior/CCS without appearing in current message → `source: carried` (may stay `required: true`).
- Inferred optional fields → `source: inferred`, `required: false`, empty `evidence_quote`.
- When `route` is `analysis`, fill `retrieval_facets` (4–8 short independent constraint sentences).
- Ranking: `value: {"limit": N, "partition_by": "...", "order_by": "...", "direction": "asc|desc"}`.
- Keywords: doanh thu→`revenue`; tồn kho→`inventory`; store→`STK_ID`/`store`; Excel→`excel`+`table`; quà/SKU→`filters.product_code`; bill≥X→`filters.min_bill_value`.

## `retrieval_facets` (schema RAG)

Purpose: each facet is an **independent retrieval cue**. Schema RAG embeds these sentences to find relevant tables/columns — vague facets retrieve the wrong objects.

Rules:

1. **One constraint → one facet.** Cover every major brief obligation still in force: time, each active filter, each metric, ranking, output. On follow-up, include **carried** constraints too — do not emit only the delta from `current_message`.
2. **Name the business object with clear keywords** in that facet (Vietnamese and/or the brief field sense). The sentence must make the *object type* obvious, not only a vague “phân tích / lọc / xuất”.
3. **Object-keyword examples** (use only objects that actually appear in the brief — do not invent extras). Illustrative pairs — **not** recipes from recent trials:

| Object in the request | Put keywords like these in the facet |
|-----------------------|--------------------------------------|
| Tồn kho / tồn cuối kỳ | `tồn kho`, `inventory`, `số tồn` |
| Nhà cung cấp | `nhà cung cấp`, `supplier`, `NCC` |
| Hình thức thanh toán | `thanh toán`, `payment`, `PMT` |
| Công nợ / phải thu | `công nợ`, `debt`, `phải thu` |
| Điểm tích lũy | `điểm tích lũy`, `loyalty points` |
| Khuyến mãi / chiết khấu CTKM | `khuyến mãi`, `chiết khấu`, `promotion` |
| Hóa đơn GTGT / VAT | `hóa đơn GTGT`, `VAT`, `invoice` |
| Nhân viên / thu ngân | `nhân viên`, `thu ngân`, `cashier` |

4. **Do not** put physical table names, column recipes, or SQL in facets. Values may appear when the user stated them; the **object keyword** is mandatory.
5. Do **not** fill the list with only output-format facets (`excel` / `bảng`) when filters or metrics exist.

Weak (object unclear): `"Phân tích theo điều kiện"` · `"Lọc dữ liệu"` · `"Xuất kết quả"`.  
Stronger: name the object explicitly, e.g. `"Lọc theo nhà cung cấp …"` · `"Đo tồn kho cuối kỳ …"` · `"Theo hình thức thanh toán …"`.

## Knowledge level

- Technical terms (`SKU_ID`, `TRANS_NUM`, …) → `user_knowledge_level: expert`.
- Informal product codes → `unknown` + often `exploration_mode: true`.
- Multi SKU + bill threshold without clear bill definition → `exploration_mode: true`.

## Examples

**ContextPack follow-up:** current_message changes one field of a prior analysis → `dialogue_act: follow_up_same_task`, brief intent fully restated with the delta applied, other constraints carried; `retrieval_facets` still one-per-constraint with clear **object keywords** for every active (including carried) obligation — not only the latest delta.

**User:** "Xin chào"

```json
{
  "route": "chitchat",
  "dialogue_act": "chitchat",
  "user_message": "Xin chào! Tôi có thể giúp bạn phân tích doanh thu, VIP, tồn kho hoặc sản phẩm. Bạn cần xem gì?",
  "brief": null
}
```

**User teaches a rule** (no analysis request):

```json
{
  "route": "chitchat",
  "dialogue_act": "teach_domain_fact",
  "user_message": "Đã ghi nhận quy tắc về giá trị bill. Tôi sẽ dùng khi phân tích sau.",
  "brief": null,
  "domain_fact": {
    "statement": "Giá tiền của một bill lấy từ TRANSHDR.AMOUNT, hoặc tổng AMOUNT mọi dòng cùng TRANS_NUM trên STRANS.",
    "fact_type": "formula",
    "scope": "user",
    "schema_links": [
      {"chunk_group": "table", "ref": "db2:transhdr"},
      {"chunk_group": "table", "ref": "db2:strans"},
      {"chunk_group": "column", "ref": "amount_bill_header"},
      {"chunk_group": "column", "ref": "amount_line_item"},
      {"chunk_group": "column", "ref": "sale_document_number"}
    ]
  }
}
```
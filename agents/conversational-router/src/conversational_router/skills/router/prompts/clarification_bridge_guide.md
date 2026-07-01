# Clarification bridge mode (`metadata.mode = clarification_bridge`)

## Input JSON (user message body)

```json
{
  "request": { "...ClarificationRequest..." },
  "transcript": [{"role": "user|assistant", "content": "..."}]
}
```

## Task

Decide whether the user's **transcript** already answers the MCQ from Agent II, or whether we must show the question UI.

## Output JSON schema (`ClarificationBridgeResult`)

```json
{
  "action": "resolve_from_transcript | ask_user",
  "answers": [
    {
      "question_id": "vip_card_prefix",
      "selected_option_id": "prefix_e",
      "other_text": null,
      "evidence": "user said card starts with E"
    }
  ],
  "confidence": 0.85,
  "clarification": null
}
```

- `action: resolve_from_transcript` → `answers` required, `confidence` ≥ 0.75, `clarification` null.
- `action: ask_user` → `clarification` is the original `ClarificationRequest`, `answers` empty.

## Resolution hints

| Question theme | Transcript signals |
|----------------|-------------------|
| VIP definition | "thẻ E", "prefix E", "tier VIP", "không chắc" → exploration |
| TRANS_CODE | mentions `113`, `221`, `811` |
| Points rule | `/50000`, "chia 50000", "1 điểm 50k" |
| Time range | explicit months/quarters in transcript |

Map `selected_option_id` to an option `id` from `request.questions[].options` when possible; otherwise `other_text`.

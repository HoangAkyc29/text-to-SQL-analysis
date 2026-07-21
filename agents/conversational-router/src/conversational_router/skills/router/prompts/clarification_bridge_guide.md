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
      "question_id": "<question_id from request>",
      "selected_option_id": "<option_id from request>",
      "other_text": null,
      "evidence": "<verbatim supporting user statement>"
    }
  ],
  "confidence": 0.85,
  "clarification": null
}
```

- `action: resolve_from_transcript` → `answers` required, `confidence` ≥ 0.75, `clarification` null.
- `action: ask_user` → `clarification` is the original `ClarificationRequest`, `answers` empty.

## Resolution hints

- Resolve only when the transcript clearly states the requested definition,
  identifier meaning, formula, scope, or time range.
- Preserve the user's exact supporting statement in `evidence`.
- If the user says they are unsure, keep the clarification unresolved or select
  the request's exploration option.

Map `selected_option_id` to an option `id` from `request.questions[].options` when possible; otherwise `other_text`.

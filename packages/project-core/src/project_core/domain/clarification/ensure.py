"""Ensure ClarificationRequest always has UI-renderable questions."""

from __future__ import annotations

from project_core.domain.contracts.clarification import (
    ClarificationOption,
    ClarificationQuestion,
    ClarificationRequest,
)


def ensure_clarification_questions(request: ClarificationRequest) -> ClarificationRequest:
    """Fill empty ``questions`` so the console can render ClarificationCard.

    Agent IV often emits ``suggest_clarify`` with only a prose reason. Without at
    least one question the UI shows a plain chat bubble and the bottom Send box
    starts a *new* analysis instead of answering the pending interaction.
    """
    reason = str(request.reason or "").strip()
    evidence = str(request.evidence_summary or "").strip()
    blob = f"{reason} {evidence}".lower()

    questions = list(request.questions or [])
    if questions:
        # Keep structured MCQs; if a question has neither prompt nor options, repair prompt.
        fixed: list[ClarificationQuestion] = []
        for idx, q in enumerate(questions):
            prompt = str(q.prompt or "").strip() or reason or evidence or "Vui lòng bổ sung thông tin."
            options = list(q.options or [])
            fixed.append(
                q.model_copy(
                    update={
                        "id": q.id or f"q{idx + 1}",
                        "prompt": prompt,
                        "options": options,
                        "maps_to_brief_field": q.maps_to_brief_field or "filters.clarify_note",
                    }
                )
            )
        return request.model_copy(
            update={
                "questions": fixed,
                "evidence_summary": evidence or reason,
            }
        )

    if any(
        tok in blob
        for tok in (
            "amount_x",
            "amount_y",
            "amount_hdr",
            "amount_line",
            "header amount",
            "line amount",
            "line item",
            "tổng giá trị",
            "tong gia tri",
            "từng dòng",
            "tung dong",
            "hóa đơn",
            "hoa don",
            "min_bill",
            "600k",
            "600000",
        )
    ):
        synthesized = ClarificationQuestion(
            id="bill_amount_grain",
            prompt=(
                "Điều kiện giá trị bill (ví dụ ≥600k) áp dụng cho tổng hóa đơn "
                "(header amount) hay cho từng dòng sản phẩm?"
            ),
            options=[
                ClarificationOption(
                    id="header_amount",
                    label="Tổng giá trị hóa đơn (header amount)",
                    brief_value={"min_bill_grain": "header"},
                ),
                ClarificationOption(
                    id="line_amount",
                    label="Giá trị từng dòng sản phẩm (line amount)",
                    brief_value={"min_bill_grain": "line"},
                ),
            ],
            maps_to_brief_field="filters.min_bill_grain",
            fact_type="constraint",
        )
    else:
        prompt = reason or evidence or "Vui lòng bổ sung thông tin để tiếp tục phân tích."
        synthesized = ClarificationQuestion(
            id="open_clarify",
            prompt=prompt[:500],
            options=[],
            maps_to_brief_field="filters.clarify_note",
        )

    return request.model_copy(
        update={
            "questions": [synthesized],
            "evidence_summary": evidence or reason or synthesized.prompt,
        }
    )
